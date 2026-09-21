"""
Guardian Benchmark: Experiment Runner

Runs the Guardian pipeline against RCAEval-derived threat scenarios.

Experiments:
  E1 — Threat Detection: Can the Guard detect malicious patterns?
  E2 — Progressive Cost: Latency of tiered vs full validation
  E3 — Intent Classification: Rule-based vs LLM intent accuracy
  E4 — False Positive Rate: % of legitimate requests blocked
  E5 — Adversarial Robustness: Accuracy under perturbation
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from guardian.adapters.rcaeval_threat_mapper import (
    detect_fault_type,
    detect_system,
    extract_ground_truth_service,
    map_case_to_clean_request,
    map_case_to_request,
)
from guardian.config.policies import FAULT_TO_THREAT
from guardian.layers.classifier import ClassifierConfig, IntentType, classify_intent
from guardian.layers.guard import GuardConfig, GuardDecision, screen_request
from guardian.layers.progressive_cost import (
    GuardianConfig,
    ValidationResult,
    validate_request,
)
from guardian.layers.verifier import VerifierConfig, verify_permission


def run_experiments(
    data_dir: str,
    experiments: list[str],
    output_dir: str | None = None,
    classify_method: str = "rule",
    max_cases: int | None = None,
) -> dict:
    """Run the Guardian experiment suite.

    Args:
        data_dir:        Path to RCAEval data directory.
        experiments:     List of experiment IDs (E1-E5).
        output_dir:      Output directory for results.
        classify_method: "rule" or "llm" for intent classification.
        max_cases:       Max cases to process.

    Returns:
        Dict with experiment results and summary statistics.
    """
    data_path = Path(data_dir)
    experiments = [e.upper() for e in experiments]

    if not data_path.exists():
        print(f"Data directory not found: {data_dir}")
        return {}

    # Find case directories
    case_dirs = sorted([
        d for d in data_path.iterdir()
        if d.is_dir() and d.name.startswith("re1")
    ])

    if max_cases:
        case_dirs = case_dirs[:max_cases]

    total = len(case_dirs)
    print("\nGuardian Benchmark Runner")
    print(f"{'=' * 60}")
    print(f"Cases: {total}")
    print(f"Experiments: {', '.join(experiments)}")
    print(f"Classification: {classify_method}")
    print()

    # ── Results storage ──────────────────────────────────────────────────
    results = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_cases": total,
            "experiments": experiments,
            "classify_method": classify_method,
        },
        "cases": [],
        "summary": {},
    }

    # ── Counters ─────────────────────────────────────────────────────────
    # E1: Threat detection
    threats_detected = 0
    threat_counts: dict[str, dict] = defaultdict(
        lambda: {"total": 0, "detected": 0, "blocked": 0}
    )
    system_counts: dict[str, dict] = defaultdict(
        lambda: {"total": 0, "detected": 0, "blocked": 0}
    )

    # E2: Progressive cost latency
    progressive_latencies: list[float] = []
    full_latencies: list[float] = []

    # E3: Intent classification
    intent_correct_rule = 0
    intent_correct_llm = 0

    # E4: False positive
    fp_count = 0
    fp_total = 0

    # ── Process cases ────────────────────────────────────────────────────
    for idx, case_dir in enumerate(case_dirs, 1):
        case_name = case_dir.name
        fault_type = detect_fault_type(case_name)
        system = detect_system(case_name)
        threat_type = FAULT_TO_THREAT.get(fault_type)

        if not threat_type:
            continue

        threat_key = threat_type.value
        threat_counts[threat_key]["total"] += 1
        system_counts[system]["total"] += 1

        # Map to agent request
        request = map_case_to_request(case_dir, inject_attack=True)
        if not request:
            continue

        case_result: dict[str, Any] = {
            "case": case_name,
            "system": system,
            "fault_type": fault_type,
            "threat_type": threat_key,
            "ground_truth": extract_ground_truth_service(case_name),
        }

        # ── E1: Threat Detection ─────────────────────────────────────────
        if "E1" in experiments:
            guard_result = screen_request(request)
            detected = guard_result.decision != GuardDecision.ALLOW

            case_result["guard_decision"] = guard_result.decision.value
            case_result["guard_risk_score"] = guard_result.risk_score
            case_result["guard_rules_triggered"] = guard_result.triggered_rules
            case_result["guard_latency_ms"] = guard_result.latency_ms

            if detected:
                threats_detected += 1
                threat_counts[threat_key]["detected"] += 1
                system_counts[system]["detected"] += 1

        # ── E2: Progressive Cost Latency ─────────────────────────────────
        if "E2" in experiments:
            # Progressive mode
            prog_config = GuardianConfig(mode="progressive", classify_method="rule")
            prog_result = validate_request(request, config=prog_config)
            progressive_latencies.append(prog_result.total_latency_ms)

            # Full mode
            full_config = GuardianConfig(mode="full", classify_method="rule")
            full_result = validate_request(request, config=full_config)
            full_latencies.append(full_result.total_latency_ms)

            case_result["progressive_latency_ms"] = prog_result.total_latency_ms
            case_result["progressive_layers"] = prog_result.layers_invoked
            case_result["progressive_checks"] = prog_result.total_checks
            case_result["full_latency_ms"] = full_result.total_latency_ms
            case_result["full_layers"] = full_result.layers_invoked
            case_result["full_checks"] = full_result.total_checks

        # ── E3: Intent Classification ────────────────────────────────────
        if "E3" in experiments:
            # Rule-based
            rule_class = classify_intent(request, method="rule")
            # Ground truth intent: map fault→threat→expected intent
            expected_intents = {
                "EXCESSIVE_AGENCY": IntentType.ADMIN,
                "EXFILTRATION": IntentType.READ,
                "PROMPT_INJECTION": IntentType.TRADE,
                "SUPPLY_CHAIN": IntentType.ADMIN,
                "TOOL_POISONING": IntentType.TRADE,
            }
            expected = expected_intents.get(threat_key, IntentType.UNKNOWN)

            rule_correct = rule_class.intent == expected
            if rule_correct:
                intent_correct_rule += 1

            case_result["intent_rule"] = rule_class.intent.value
            case_result["intent_rule_confidence"] = rule_class.confidence
            case_result["intent_expected"] = expected.value
            case_result["intent_rule_correct"] = rule_correct

            # LLM-based (only if requested)
            if classify_method == "llm":
                llm_class = classify_intent(request, method="llm")
                llm_correct = llm_class.intent == expected
                if llm_correct:
                    intent_correct_llm += 1
                case_result["intent_llm"] = llm_class.intent.value
                case_result["intent_llm_confidence"] = llm_class.confidence
                case_result["intent_llm_correct"] = llm_correct
                case_result["intent_llm_latency_ms"] = llm_class.latency_ms

        # ── E4: False Positive Rate ──────────────────────────────────────
        if "E4" in experiments:
            clean_request = map_case_to_clean_request(case_dir)
            if clean_request:
                fp_total += 1
                clean_result = validate_request(clean_request)
                if clean_result.blocked:
                    fp_count += 1
                case_result["fp_clean_blocked"] = clean_result.blocked
                case_result["fp_clean_decision"] = clean_result.decision

        results["cases"].append(case_result)

        # Progress
        det_str = ""
        if "E1" in experiments:
            det_pct = threats_detected / idx * 100
            det_str = f" — Detection: {threats_detected}/{idx} ({det_pct:.1f}%)"
        print(f"\r  [{idx:>4}/{total}] {idx/total*100:.1f}%{det_str}", end="", flush=True)

    print()

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 60}")

    if "E1" in experiments:
        det_rate = threats_detected / total * 100 if total > 0 else 0
        print(f"Threat Detection Rate: {det_rate:.1f}%")
        results["summary"]["detection_rate"] = round(det_rate, 1)

        print("\nBy Threat Type:")
        for tt in sorted(threat_counts.keys()):
            c = threat_counts[tt]
            rate = c["detected"] / c["total"] * 100 if c["total"] > 0 else 0
            print(f"  {tt:<22} — Detection: {rate:.1f}%  ({c['detected']}/{c['total']})")

        print("\nBy System:")
        for sys_name in sorted(system_counts.keys()):
            c = system_counts[sys_name]
            rate = c["detected"] / c["total"] * 100 if c["total"] > 0 else 0
            print(f"  {sys_name:<22} — Detection: {rate:.1f}%")

    if "E2" in experiments and progressive_latencies:
        prog_mean = sum(progressive_latencies) / len(progressive_latencies)
        full_mean = sum(full_latencies) / len(full_latencies)
        savings = (1 - prog_mean / full_mean) * 100 if full_mean > 0 else 0
        print("\nProgressive Cost:")
        print(f"  Progressive mean: {prog_mean:.2f}ms")
        print(f"  Full mean:        {full_mean:.2f}ms")
        print(f"  Latency savings:  {savings:.1f}%")
        results["summary"]["progressive_mean_ms"] = round(prog_mean, 2)
        results["summary"]["full_mean_ms"] = round(full_mean, 2)
        results["summary"]["latency_savings_pct"] = round(savings, 1)

    if "E3" in experiments:
        rule_acc = intent_correct_rule / total * 100 if total > 0 else 0
        print(f"\nIntent Classification (Rule): {rule_acc:.1f}%")
        results["summary"]["intent_rule_accuracy"] = round(rule_acc, 1)

        if classify_method == "llm":
            llm_acc = intent_correct_llm / total * 100 if total > 0 else 0
            print(f"Intent Classification (LLM):  {llm_acc:.1f}%")
            results["summary"]["intent_llm_accuracy"] = round(llm_acc, 1)

    if "E4" in experiments and fp_total > 0:
        fp_rate = fp_count / fp_total * 100
        print(f"\nFalse Positive Rate: {fp_rate:.2f}% ({fp_count}/{fp_total})")
        projected_1m = int(fp_rate / 100 * 1_000_000)
        print(f"  Projected at 1M requests/day: {projected_1m:,} blocked")
        results["summary"]["false_positive_rate"] = round(fp_rate, 2)
        results["summary"]["false_positives"] = fp_count

    # ── Save results ─────────────────────────────────────────────────────
    out_dir = Path(output_dir or "guardian_benchmark_results")
    run_dir = out_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    results_file = run_dir / "results.json"
    results_file.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n✓ Results saved to {run_dir}")

    return results
