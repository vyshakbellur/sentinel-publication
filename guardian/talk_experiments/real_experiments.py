"""
Guardian Dataset-Context Experiment Suite

The default release command runs against all 375 RCAEval contexts using:
- Real Guardian pipeline (guard → classifier → verifier)
- Real time.perf_counter() measurements
- Real progressive cost (skip verifier for LOW risk)

Redis TTL and repeated latency-distribution modes are optional exploratory
experiments and are not evidence for the workshop's primary claims.

Hardware: MacBook Pro (reported by script)
Software: Python, Redis, Guardian pipeline
Data: 375 RCAEval cases (online-boutique, train-ticket, sock-shop)

Output: JSON results + matplotlib charts
"""

import json
import platform
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

try:
    import redis
except ImportError:  # Redis is optional and only used by the exploratory TTL mode.
    redis = None

# Add guardian to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from guardian.adapters.rcaeval_threat_mapper import (
    get_attack_variant_count,
    map_case_to_clean_request,
    map_case_to_request,
)
from guardian.benchmark.scenario_matrix import (
    SCENARIO_MATRIX_VERSION,
    build_context_scenarios,
    get_scenario_templates,
)
from guardian.layers.progressive_cost import GuardianConfig, validate_request

BENCHMARK_PERMISSIONS = {
    "allowed_intents": {
        "READ", "WRITE", "TRANSFORM", "TRANSMIT", "TRADE", "ADMIN",
        "EXFILTRATION", "EXECUTION",
    },
    "allowed_scope": {"*"},
}


def get_hardware_info():
    """Collect hardware/software info for methodology reporting."""
    return {
        "machine": platform.machine(),
        "processor": platform.processor(),
        "system": platform.system(),
        "python_version": platform.python_version(),
        "node_name": platform.node(),
        "platform": platform.platform(),
    }


def _run_experiment_legacy_progressive_cost(data_dir: str):
    """
    Experiment 1 (Real): Progressive Cost vs Full Static
    
    Runs every case/attack-template pair through both Guardian modes:
    - Full mode: all 3 layers on every request
    - Progressive mode: skip verifier for LOW risk
    
    Measures real wall-clock time with time.perf_counter()
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: Progressive Cost (Real Pipeline)")
    print("=" * 60)

    data_path = Path(data_dir)
    case_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith("re1")])
    if len(case_dirs) != 375:
        raise ValueError(f"Expected exactly 375 cases, found {len(case_dirs)} in {data_path}")

    attack_variant_count = get_attack_variant_count()
    full_latencies = []
    progressive_latencies = []
    full_details = []
    progressive_details = []
    system_counts: Counter[str] = Counter()
    coverage = {
        "tools": set(),
        "operations": set(),
        "source_classes": set(),
        "destination_trust_domains": set(),
    }
    decisions_by_variant: defaultdict[str, set[str]] = defaultdict(set)

    for case_dir in case_dirs:
        # One clean action plus every distinct adversarial template. These are
        # case-action combinations, not independent telemetry samples.
        for variant_index in range(-1, attack_variant_count):
            request = (
                map_case_to_clean_request(case_dir)
                if variant_index == -1
                else map_case_to_request(
                    case_dir, inject_attack=True, variant_index=variant_index
                )
            )
            if not request:
                continue

            variant_name = "clean" if variant_index == -1 else f"attack-{variant_index}"
            if variant_index == -1:
                system_counts[request["_telemetry"]["system"]] += 1
            coverage["tools"].add(request.get("tool_name"))
            coverage["operations"].add(request.get("operation"))
            coverage["source_classes"].add(
                request.get("source", {}).get("classification")
            )
            coverage["destination_trust_domains"].add(
                request.get("destination", {}).get("trust_domain")
            )

            # Run full mode (all contextual checks)
            full_config = GuardianConfig(mode="full")
            start = time.perf_counter()
            full_result = validate_request(
                request, user_permissions=BENCHMARK_PERMISSIONS, config=full_config
            )
            full_elapsed = (time.perf_counter() - start) * 1000
            full_latencies.append(full_elapsed)
            full_details.append({
                "case": case_dir.name,
                "variant": variant_name,
                "latency_ms": round(full_elapsed, 4),
                "layers": full_result.layers_invoked,
                "risk_tier": full_result.risk_tier,
                "decision": full_result.decision,
            })

            # Run progressive mode (skip contextual verifier for LOW)
            prog_config = GuardianConfig(mode="progressive")
            start = time.perf_counter()
            prog_result = validate_request(
                request, user_permissions=BENCHMARK_PERMISSIONS, config=prog_config
            )
            prog_elapsed = (time.perf_counter() - start) * 1000
            progressive_latencies.append(prog_elapsed)
            progressive_details.append({
                "case": case_dir.name,
                "variant": variant_name,
                "latency_ms": round(prog_elapsed, 4),
                "layers": prog_result.layers_invoked,
                "risk_tier": prog_result.risk_tier,
                "decision": prog_result.decision,
            })
            decisions_by_variant[variant_name].add(prog_result.decision)

            if full_result.decision != prog_result.decision:
                raise AssertionError(
                    f"Mode decision mismatch for {case_dir.name} variant {variant_index}: "
                    f"full={full_result.decision}, progressive={prog_result.decision}"
                )

    full_arr = np.array(full_latencies)
    prog_arr = np.array(progressive_latencies)

    # Count how many went through each path
    low_risk_count = sum(1 for d in progressive_details if d["risk_tier"] == "LOW")
    high_risk_count = len(progressive_details) - low_risk_count
    full_verifier_count = sum(1 for d in full_details if "verifier" in d["layers"])
    progressive_verifier_count = sum(
        1 for d in progressive_details if "verifier" in d["layers"]
    )

    results = {
        "experiment": "progressive_cost_real",
        "independent_telemetry_contexts": len(case_dirs),
        "attack_templates": attack_variant_count,
        "clean_action_templates": 1,
        "adversarial_case_action_pairs": len(case_dirs) * attack_variant_count,
        "total_case_action_evaluations": len(full_latencies),
        "low_risk_count": low_risk_count,
        "high_risk_count": high_risk_count,
        "full_verifier_count": full_verifier_count,
        "progressive_verifier_count": progressive_verifier_count,
        "full_mode": {
            "p50_ms": round(float(np.percentile(full_arr, 50)), 4),
            "p95_ms": round(float(np.percentile(full_arr, 95)), 4),
            "p99_ms": round(float(np.percentile(full_arr, 99)), 4),
            "mean_ms": round(float(np.mean(full_arr)), 4),
            "std_ms": round(float(np.std(full_arr)), 4),
        },
        "progressive_mode": {
            "p50_ms": round(float(np.percentile(prog_arr, 50)), 4),
            "p95_ms": round(float(np.percentile(prog_arr, 95)), 4),
            "p99_ms": round(float(np.percentile(prog_arr, 99)), 4),
            "mean_ms": round(float(np.mean(prog_arr)), 4),
            "std_ms": round(float(np.std(prog_arr)), 4),
        },
        "savings_p50_pct": round((1 - np.percentile(prog_arr, 50) / np.percentile(full_arr, 50)) * 100, 2),
        "decision_equivalence": True,
        "coverage": {
            "systems": dict(sorted(system_counts.items())),
            **{
                name: sorted(value for value in values if value is not None)
                for name, values in coverage.items()
            },
            "progressive_decisions": dict(
                Counter(detail["decision"] for detail in progressive_details)
            ),
            "decisions_by_variant": {
                variant: sorted(decisions)
                for variant, decisions in sorted(decisions_by_variant.items())
            },
            "decision_varies_by_telemetry_context": any(
                len(decisions) > 1 for decisions in decisions_by_variant.values()
            ),
        },
        "full_details": full_details,
        "progressive_details": progressive_details,
    }

    print(f"  Independent telemetry contexts: {len(case_dirs)}")
    print(f"  Case-action evaluations: {len(full_latencies)}")
    print(f"  LOW risk (2 layers): {low_risk_count}")
    print(f"  HIGH risk (3 layers): {high_risk_count}")
    print(f"  Full mode     — p50: {results['full_mode']['p50_ms']:.4f}ms, p95: {results['full_mode']['p95_ms']:.4f}ms")
    print(f"  Progressive   — p50: {results['progressive_mode']['p50_ms']:.4f}ms, p95: {results['progressive_mode']['p95_ms']:.4f}ms")
    print(f"  p50 savings: {results['savings_p50_pct']:.2f}%")

    return results


def _unexpected_decision_counts(expected: str, actual: str) -> dict[str, int]:
    """Classify unexpected observed outcomes without merging interventions."""
    return {
        "false_allow": int(actual == "ALLOW" and expected != "ALLOW"),
        "false_block": int(actual == "BLOCK" and expected != "BLOCK"),
        "false_escalate": int(actual == "ESCALATE" and expected != "ESCALATE"),
    }


def run_experiment_progressive_cost(data_dir: str):
    """Run twelve declared oracle scenarios in every RCAEval context.

    The same materialized corpus is evaluated in full and progressive modes.
    RCAEval telemetry is retained only as reporting context and is never added
    to the request passed into Guardian.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: 375-Context Authorization Scenario Matrix")
    print("=" * 60)

    data_path = Path(data_dir)
    case_dirs = sorted(
        d for d in data_path.iterdir() if d.is_dir() and d.name.startswith("re1")
    )
    if len(case_dirs) != 375:
        raise ValueError(
            f"Expected exactly 375 contexts, found {len(case_dirs)} in {data_path}"
        )

    corpus = [
        scenario
        for case_dir in case_dirs
        for scenario in build_context_scenarios(case_dir)
    ]
    templates = get_scenario_templates()
    if len(templates) != 12 or len(corpus) != 4_500:
        raise AssertionError(
            f"Expected 12 templates × 375 contexts = 4500, got "
            f"{len(templates)} × {len(case_dirs)} = {len(corpus)}"
        )

    modes: dict[str, dict[str, Any]] = {}
    for mode in ("full", "progressive"):
        modes[mode] = {
            "latencies": [],
            "actual": Counter(),
            "confusion": Counter(),
            "false_allow": 0,
            "false_block": 0,
            "false_escalate": 0,
            "verifier_calls": 0,
            "oracle_matches": 0,
        }

    per_template: dict[str, dict[str, Any]] = {}
    for template in templates:
        per_template[template["scenario_id"]] = {
            "pair_id": template["pair_id"],
            "variant": template["variant"],
            "expected_decision": template["expected_decision"],
            "oracle_reason": template["oracle_reason"],
            "full": {
                "actual": Counter(), "confusion": Counter(),
                "false_allow": 0, "false_block": 0, "false_escalate": 0,
                "verifier_calls": 0,
            },
            "progressive": {
                "actual": Counter(), "confusion": Counter(),
                "false_allow": 0, "false_block": 0, "false_escalate": 0,
                "verifier_calls": 0,
            },
        }

    equivalence_mismatches = []
    for scenario in corpus:
        expected = scenario["expected_decision"]
        observed: dict[str, str] = {}
        for mode in ("full", "progressive"):
            start = time.perf_counter()
            result = validate_request(
                scenario["request"],
                user_permissions=scenario["user_permissions"],
                config=GuardianConfig(mode=mode),
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            observed[mode] = result.decision

            mode_stats = modes[mode]
            mode_stats["latencies"].append(elapsed_ms)
            mode_stats["actual"][result.decision] += 1
            mode_stats["confusion"][f"{expected}->{result.decision}"] += 1
            mode_stats["oracle_matches"] += int(result.decision == expected)
            mode_stats["verifier_calls"] += int("verifier" in result.layers_invoked)

            errors = _unexpected_decision_counts(expected, result.decision)
            template_stats = per_template[scenario["scenario_id"]][mode]
            template_stats["actual"][result.decision] += 1
            template_stats["confusion"][f"{expected}->{result.decision}"] += 1
            template_stats["verifier_calls"] += int(
                "verifier" in result.layers_invoked
            )
            for name, count in errors.items():
                mode_stats[name] += count
                template_stats[name] += count

        if observed["full"] != observed["progressive"]:
            equivalence_mismatches.append(
                {
                    "case_name": scenario["context"]["case_name"],
                    "scenario_id": scenario["scenario_id"],
                    **observed,
                }
            )

    def summarize_mode(mode: str) -> dict[str, Any]:
        stats = modes[mode]
        arr = np.asarray(stats.pop("latencies"), dtype=float)
        return {
            "evaluations": len(arr),
            "actual_decisions": dict(sorted(stats["actual"].items())),
            "confusion": dict(sorted(stats["confusion"].items())),
            "oracle_matches": stats["oracle_matches"],
            "oracle_accuracy_pct": round(stats["oracle_matches"] / len(arr) * 100, 4),
            "false_allow": stats["false_allow"],
            "false_block": stats["false_block"],
            "false_escalate": stats["false_escalate"],
            "verifier_calls": stats["verifier_calls"],
            "verifier_call_rate_pct": round(stats["verifier_calls"] / len(arr) * 100, 4),
            "measured_in_process_latency_ms": {
                "p50": round(float(np.percentile(arr, 50)), 4),
                "p95": round(float(np.percentile(arr, 95)), 4),
                "p99": round(float(np.percentile(arr, 99)), 4),
                "mean": round(float(np.mean(arr)), 4),
            },
        }

    for scenario_stats in per_template.values():
        for mode in ("full", "progressive"):
            scenario_stats[mode]["actual"] = dict(
                sorted(scenario_stats[mode]["actual"].items())
            )
            scenario_stats[mode]["confusion"] = dict(
                sorted(scenario_stats[mode]["confusion"].items())
            )

    context_systems = Counter()
    context_services = Counter()
    context_faults = Counter()
    for case_dir in case_dirs:
        context = build_context_scenarios(case_dir)[0]["context"]
        context_systems[context["system"]] += 1
        context_services[f"{context['system']}:{context['service']}"] += 1
        context_faults[context["fault_type"]] += 1

    full_summary = summarize_mode("full")
    progressive_summary = summarize_mode("progressive")
    results = {
        "experiment": "authorization_scenario_matrix",
        "scenario_matrix_version": SCENARIO_MATRIX_VERSION,
        "independent_telemetry_contexts": 375,
        "scenario_templates": 12,
        "matched_boundary_pairs": 6,
        "case_scenario_evaluations_per_mode": 4_500,
        "pipeline_evaluations_across_both_modes": 9_000,
        "corpus_reused_between_modes": True,
        "oracle_source": "declared_scenario_templates_not_observed_guardian_output",
        "context_role": "contextual_metadata_only_not_used_for_guardian_decision",
        "claim_boundary": [
            "Closed policy-conformance matrix, not an estimate of open-world attack detection.",
            "Twelve reused templates are not 4,500 independent security samples.",
            "Telemetry metadata does not influence Guardian decisions in this experiment.",
            "Latency values are local in-process measurements, not enterprise service latency.",
        ],
        "context_coverage": {
            "systems": dict(sorted(context_systems.items())),
            "represented_services": dict(sorted(context_services.items())),
            "represented_service_count": len(context_services),
            "fault_types": dict(sorted(context_faults.items())),
        },
        "full_mode": full_summary,
        "progressive_mode": progressive_summary,
        "decision_equivalence": {
            "equivalent": not equivalence_mismatches,
            "mismatch_count": len(equivalence_mismatches),
            "mismatches": equivalence_mismatches,
        },
        "verifier_calls_avoided": (
            full_summary["verifier_calls"] - progressive_summary["verifier_calls"]
        ),
        "per_template": dict(sorted(per_template.items())),
    }

    print("  Contexts: 375 (telemetry retained as contextual metadata only)")
    print("  Templates: 12 in 6 matched boundary pairs")
    print("  Evaluations: 4,500 per mode; 9,000 pipeline executions")
    print(
        "  Outcomes per mode: "
        f"{progressive_summary['actual_decisions']}"
    )
    print(
        "  False ALLOW/BLOCK/ESCALATE: "
        f"{progressive_summary['false_allow']}/"
        f"{progressive_summary['false_block']}/"
        f"{progressive_summary['false_escalate']}"
    )
    print(
        "  Contextual verifier calls: "
        f"full={full_summary['verifier_calls']}, "
        f"progressive={progressive_summary['verifier_calls']}"
    )
    print(f"  Decision equivalence: {not equivalence_mismatches}")
    return results


def run_experiment_redis_ttl(data_dir: str, r):
    """
    Experiment 2 (Real): Redis TTL Caching Strategies
    
    Tests 3 strategies against real Redis:
    - No cache: every request runs full pipeline
    - Static TTL (60s): fixed TTL for all decisions
    - Adaptive TTL: LOW risk = 300s, HIGH risk = 5s
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Redis TTL Caching (Real Redis)")
    print("=" * 60)

    data_path = Path(data_dir)
    case_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith("re1")])

    # Build request list (mix clean + adversarial like real traffic)
    rng = random.Random(20260828)
    requests = []
    for case_dir in case_dirs:
        # 80% clean requests (cacheable reads)
        clean = map_case_to_clean_request(case_dir)
        if clean:
            clean["_case"] = case_dir.name
            clean["_is_adversarial"] = False
            requests.append(clean)

        # 20% adversarial (should not be served from cache ideally)
        if rng.random() < 0.25:
            adv = map_case_to_request(case_dir, inject_attack=True)
            if adv:
                adv["_case"] = case_dir.name
                adv["_is_adversarial"] = True
                requests.append(adv)

    rng.shuffle(requests)

    def compute_adaptive_ttl(risk_tier: str) -> int:
        return {"LOW": 300, "MEDIUM": 60, "HIGH": 5, "CRITICAL": 1}.get(risk_tier, 30)

    def run_strategy(strategy: str):
        # Flush Redis between strategies
        r.flushdb()

        latencies = []
        cache_hits = 0
        cache_misses = 0
        correct_blocks = 0
        missed_blocks = 0  # adversarial served from cache (security gap)

        for req in requests:
            is_adv = req.get("_is_adversarial", False)
            cache_key = f"guardian:{req.get('tool_name', 'unknown')}:{req.get('user_id', 'unknown')}"

            start = time.perf_counter()

            # Try cache first
            cached = None
            if strategy != "no_cache":
                cached = r.get(cache_key)

            if cached is not None:
                cache_hits += 1
                elapsed = (time.perf_counter() - start) * 1000
                cached_decision = cached.decode()
                if is_adv and cached_decision == "ALLOW":
                    missed_blocks += 1  # Security gap!
            else:
                cache_misses += 1
                # Run full Guardian pipeline
                result = validate_request(
                    req,
                    user_permissions=BENCHMARK_PERMISSIONS,
                    config=GuardianConfig(mode="progressive"),
                )
                elapsed = (time.perf_counter() - start) * 1000

                # Cache the decision
                if strategy == "static_ttl":
                    r.setex(cache_key, 60, result.decision)
                elif strategy == "adaptive_ttl":
                    ttl = compute_adaptive_ttl(result.risk_tier)
                    r.setex(cache_key, ttl, result.decision)

                if is_adv and result.decision == "BLOCK":
                    correct_blocks += 1

            latencies.append(elapsed)

        arr = np.array(latencies)
        total = cache_hits + cache_misses

        return {
            "strategy": strategy,
            "total_requests": total,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "hit_ratio_pct": round(cache_hits / max(total, 1) * 100, 2),
            "missed_blocks": missed_blocks,
            "correct_blocks": correct_blocks,
            "p50_ms": round(float(np.percentile(arr, 50)), 4),
            "p95_ms": round(float(np.percentile(arr, 95)), 4),
            "mean_ms": round(float(np.mean(arr)), 4),
            "std_ms": round(float(np.std(arr)), 4),
        }

    res_no = run_strategy("no_cache")
    res_static = run_strategy("static_ttl")
    res_adaptive = run_strategy("adaptive_ttl")

    results = {
        "experiment": "redis_ttl_real",
        "total_requests": res_no["total_requests"],
        "strategies": [res_no, res_static, res_adaptive],
    }

    for s in [res_no, res_static, res_adaptive]:
        print(f"  {s['strategy']:15s} — p50: {s['p50_ms']:.4f}ms, hit ratio: {s['hit_ratio_pct']:.1f}%, missed blocks: {s['missed_blocks']}")

    return results


def run_experiment_latency_distribution(data_dir: str):
    """
    Experiment 3 (Real): Latency Distribution by Risk Tier
    
    Runs all 375 cases multiple times to get stable latency distributions,
    broken down by risk tier.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Latency Distribution by Risk Tier")
    print("=" * 60)

    data_path = Path(data_dir)
    case_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith("re1")])

    NUM_RUNS = 5  # Repeat each case 5 times for stability
    tier_latencies = defaultdict(list)
    all_latencies = []

    rng = random.Random(20260828)
    for run in range(NUM_RUNS):
        for case_dir in case_dirs:
            # Mix of clean and adversarial
            if rng.random() < 0.8:
                req = map_case_to_clean_request(case_dir)
            else:
                req = map_case_to_request(case_dir, inject_attack=True)

            if not req:
                continue

            config = GuardianConfig(mode="progressive")
            start = time.perf_counter()
            result = validate_request(
                req, user_permissions=BENCHMARK_PERMISSIONS, config=config
            )
            elapsed = (time.perf_counter() - start) * 1000

            tier_latencies[result.risk_tier].append(elapsed)
            all_latencies.append({
                "latency_ms": round(elapsed, 4),
                "risk_tier": result.risk_tier,
                "layers": len(result.layers_invoked),
                "decision": result.decision,
            })

    results = {
        "experiment": "latency_distribution_real",
        "num_runs": NUM_RUNS,
        "total_measurements": len(all_latencies),
        "by_tier": {},
    }

    for tier, lats in sorted(tier_latencies.items()):
        arr = np.array(lats)
        tier_stats = {
            "count": len(lats),
            "p50_ms": round(float(np.percentile(arr, 50)), 4),
            "p95_ms": round(float(np.percentile(arr, 95)), 4),
            "p99_ms": round(float(np.percentile(arr, 99)), 4),
            "mean_ms": round(float(np.mean(arr)), 4),
            "std_ms": round(float(np.std(arr)), 4),
            "min_ms": round(float(np.min(arr)), 4),
            "max_ms": round(float(np.max(arr)), 4),
        }
        results["by_tier"][tier] = tier_stats
        print(f"  {tier:15s} — n={tier_stats['count']:5d}, p50: {tier_stats['p50_ms']:.4f}ms, p95: {tier_stats['p95_ms']:.4f}ms")

    return results


def run_experiment_fp_crisis_analysis(data_dir: str):
    """
    Experiment 4: False Positive Crisis Mathematical Analysis
    
    Not a simulation — pure math showing the impact of FP rates at scale.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 4: False Positive Crisis Analysis")
    print("=" * 60)

    scales = [
        ("1K decisions/day", 1_000),
        ("10K decisions/day", 10_000),
        ("100K decisions/day", 100_000),
        ("1M decisions/day", 1_000_000),
        ("10M decisions/day", 10_000_000),
        ("100M decisions/day", 100_000_000),
        ("1B decisions/day", 1_000_000_000),
    ]

    fp_rates = [0.1, 0.01, 0.001, 0.0001, 0.0]  # percentages

    analysis = []
    for label, decision_count in scales:
        for fp_pct in fp_rates:
            blocked = int(decision_count * (fp_pct / 100))
            analysis.append({
                "scale": label,
                "authorization_decisions": decision_count,
                "fp_rate_pct": fp_pct,
                "blocked_per_day": blocked,
            })

    # Calculate Guardian's measured FP rate
    data_path = Path(data_dir)
    case_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith("re1")])
    if len(case_dirs) != 375:
        raise ValueError(f"Expected exactly 375 cases, found {len(case_dirs)} in {data_path}")

    total_clean = 0
    fp_blocks = 0
    fp_escalations = 0

    prog_config = GuardianConfig(mode="progressive")

    for case_dir in case_dirs:
        req = map_case_to_clean_request(case_dir)
        if not req:
            raise ValueError(f"Clean request mapping failed for {case_dir}")
        total_clean += 1
        res = validate_request(
            req, user_permissions=BENCHMARK_PERMISSIONS, config=prog_config
        )
        if res.decision == "BLOCK":
            fp_blocks += 1
        elif res.decision == "ESCALATE":
            fp_escalations += 1

    fp_count = fp_blocks + fp_escalations
    n = total_clean
    if n == 0:
        raise ValueError("No clean cases evaluated. Failing loudly.")

    guardian_fp = (fp_count / n) * 100

    p = fp_count / n if n > 0 else 0
    if fp_count == 0:
        # Exact one-sided 95% Clopper-Pearson upper bound for zero events.
        upper_bound = 1 - (0.05 ** (1 / n))
        upper_bound_method = "exact_one_sided_95pct"
    else:
        # One-sided Wilson upper bound when events are observed.
        z = 1.6448536269514722
        upper_bound = (
            p + z*z/(2*n) + z * np.sqrt((p*(1-p) + z*z/(4*n))/n)
        ) / (1 + z*z/n)
        upper_bound_method = "wilson_one_sided_95pct"
    upper_bound_pct = round(upper_bound * 100, 4)

    results = {
        "experiment": "fp_crisis_analysis",
        "guardian_measured_fp_pct": guardian_fp,
        "sample_size": n,
        "fp_blocks": fp_blocks,
        "fp_escalations": fp_escalations,
        "upper_95pct": upper_bound_pct,
        "upper_bound_method": upper_bound_method,
        "analysis": analysis,
        "insight": f"Guardian measured {guardian_fp}% FP ({fp_blocks} BLOCKS, {fp_escalations} ESCALATIONS) on {n} cases. One-sided 95% upper bound: {upper_bound_pct}%. At 10M decisions/day, that upper bound means up to {int(10_000_000 * upper_bound)} interventions/day.",
    }

    print(f"  Guardian FP: {guardian_fp}% (n={n})")
    print(f"  False Blocks: {fp_blocks}")
    print(f"  False Escalations: {fp_escalations}")
    print(f"  One-sided 95% upper bound: {upper_bound_pct}%")
    print(
        "  At 10M decisions/day with upper bound: "
        f"~{int(10_000_000 * upper_bound)} interventions/day"
    )

    return results


def generate_charts(all_results: dict, output_dir: Path):
    """Generate publication-quality charts from real experiment data."""
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('Agg')

    # Chart 1: Progressive Cost comparison
    if "progressive_cost" in all_results:
        pc = all_results["progressive_cost"]
        fig, ax = plt.subplots(figsize=(8, 5))

        categories = ['p50', 'p95', 'p99']
        if "measured_in_process_latency_ms" in pc["full_mode"]:
            full_latency = pc["full_mode"]["measured_in_process_latency_ms"]
            prog_latency = pc["progressive_mode"]["measured_in_process_latency_ms"]
            full_vals = [full_latency[c] for c in categories]
            prog_vals = [prog_latency[c] for c in categories]
        else:
            full_vals = [pc["full_mode"][f"{c}_ms"] for c in categories]
            prog_vals = [pc["progressive_mode"][f"{c}_ms"] for c in categories]

        x = np.arange(len(categories))
        width = 0.35

        ax.bar(x - width/2, full_vals, width, label='Full (all layers)', color='#ef5350', alpha=0.8)
        ax.bar(x + width/2, prog_vals, width, label='Progressive (risk-based)', color='#26a69a', alpha=0.8)

        ax.set_ylabel('Latency (ms)')
        ax.set_title('Progressive Cost: 12 Scenarios × 375 Contexts')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        for i, (f, p) in enumerate(zip(full_vals, prog_vals)):
            ax.text(i - width/2, f + 0.001, f'{f:.3f}ms', ha='center', va='bottom', fontsize=8)
            ax.text(i + width/2, p + 0.001, f'{p:.3f}ms', ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.savefig(output_dir / "real_exp1_progressive_cost.png", dpi=200)
        plt.close()
        print("  Saved: real_exp1_progressive_cost.png")

    # Chart 2: Redis TTL comparison
    if "redis_ttl" in all_results:
        ttl = all_results["redis_ttl"]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        strategies = [s["strategy"] for s in ttl["strategies"]]
        p50s = [s["p50_ms"] for s in ttl["strategies"]]
        hits = [s["hit_ratio_pct"] for s in ttl["strategies"]]
        missed = [s["missed_blocks"] for s in ttl["strategies"]]

        colors = ['#ef5350', '#ffa726', '#26a69a']
        ax1.bar(strategies, p50s, color=colors, alpha=0.8)
        ax1.set_ylabel('p50 Latency (ms)')
        ax1.set_title('Caching Strategy: Latency Impact')
        for i, v in enumerate(p50s):
            ax1.text(i, v + 0.001, f'{v:.3f}ms', ha='center', va='bottom', fontsize=9)

        ax2.bar(strategies, hits, color=colors, alpha=0.8)
        ax2.set_ylabel('Cache Hit Ratio (%)')
        ax2.set_title('Caching Strategy: Hit Ratios')
        for i, (v, m) in enumerate(zip(hits, missed)):
            ax2.text(i, v + 1, f'{v:.1f}%\n({m} missed)', ha='center', va='bottom', fontsize=8)

        plt.suptitle('Redis TTL Experiment (Real Redis, 375 RCAEval Cases)', fontsize=12)
        plt.tight_layout()
        plt.savefig(output_dir / "real_exp2_redis_ttl.png", dpi=200)
        plt.close()
        print("  Saved: real_exp2_redis_ttl.png")

    # Chart 3: Latency distribution by tier
    if "latency_distribution" in all_results:
        ld = all_results["latency_distribution"]
        fig, ax = plt.subplots(figsize=(8, 5))

        tiers = list(ld["by_tier"].keys())
        p50s = [ld["by_tier"][t]["p50_ms"] for t in tiers]
        p95s = [ld["by_tier"][t]["p95_ms"] for t in tiers]
        counts = [ld["by_tier"][t]["count"] for t in tiers]

        x = np.arange(len(tiers))
        width = 0.35

        ax.bar(x - width/2, p50s, width, label='p50', color='#26a69a', alpha=0.8)
        ax.bar(x + width/2, p95s, width, label='p95', color='#ffa726', alpha=0.8)

        ax.set_ylabel('Latency (ms)')
        ax.set_title(f'Latency by Risk Tier (5 runs × 375 cases = {ld["total_measurements"]} measurements)')
        ax.set_xticks(x)
        ax.set_xticklabels([f'{t}\n(n={c})' for t, c in zip(tiers, counts)])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "real_exp3_latency_by_tier.png", dpi=200)
        plt.close()
        print("  Saved: real_exp3_latency_by_tier.png")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Guardian Real Experiments")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to RCAEval cases directory")
    parser.add_argument(
        "--experiments",
        nargs="+",
        choices=[
            "scenario_matrix",
            "progressive_cost",
            "fp_crisis",
            "redis_ttl",
            "latency_distribution",
        ],
        default=["scenario_matrix", "fp_crisis"],
        help=(
            "Experiments to run. 'progressive_cost' is a legacy alias for "
            "'scenario_matrix'. The default pair supports the talk claims; "
            "Redis TTL and repeated latency distribution are exploratory."
        ),
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    if not Path(data_dir).exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    output_dir = Path(__file__).parent

    print("=" * 60)
    print("GUARDIAN REAL EXPERIMENT SUITE")
    print("=" * 60)

    hardware = get_hardware_info()
    print(f"Hardware: {hardware['platform']}")
    print(f"Python:   {hardware['python_version']}")
    print(f"Data:     {data_dir}")
    needs_redis = "redis_ttl" in args.experiments
    r = None
    if needs_redis:
        if redis is None:
            raise RuntimeError(
                "The exploratory redis_ttl experiment requires the 'redis' package"
            )
        print("Redis:    localhost:6379")
        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()
        print("Redis:    CONNECTED")

    all_results = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hardware": hardware,
            "data_dir": data_dir,
            "redis": "localhost:6379" if needs_redis else None,
            "experiments": args.experiments,
        }
    }

    if {"scenario_matrix", "progressive_cost"}.intersection(args.experiments):
        all_results["progressive_cost"] = run_experiment_progressive_cost(data_dir)
    if "redis_ttl" in args.experiments:
        assert r is not None
        all_results["redis_ttl"] = run_experiment_redis_ttl(data_dir, r)
    if "latency_distribution" in args.experiments:
        all_results["latency_distribution"] = run_experiment_latency_distribution(data_dir)
    if "fp_crisis" in args.experiments:
        all_results["fp_crisis"] = run_experiment_fp_crisis_analysis(data_dir)

    # Generate charts
    print("\nGenerating charts...")
    generate_charts(all_results, output_dir)

    # Save full results
    results_path = output_dir / "real_experiment_results.json"
    with open(results_path, "w") as f:
        # Remove detail lists to keep JSON manageable
        save_results = {k: v for k, v in all_results.items()}
        if "progressive_cost" in save_results:
            save_results["progressive_cost"] = {
                k: v for k, v in save_results["progressive_cost"].items()
                if k not in ("full_details", "progressive_details")
            }
        json.dump(save_results, f, indent=2, default=str)

    if "progressive_cost" in all_results:
        matrix_path = output_dir / "scenario_matrix_results.json"
        matrix_artifact = {
            "metadata": {
                "generated_at_utc": all_results["metadata"]["timestamp"],
                "dataset": "RCAEval public 375-context subset",
                "python_version": hardware["python_version"],
                "platform": hardware["platform"],
                "experiments": ["authorization_scenario_matrix"],
            },
            **all_results["progressive_cost"],
        }
        with open(matrix_path, "w") as f:
            json.dump(matrix_artifact, f, indent=2, default=str)
        print(f"Scenario matrix artifact saved to: {matrix_path}")

    print(f"\nResults saved to: {results_path}")
    print("DONE")


if __name__ == "__main__":
    main()
