"""Frozen initial SENTINEL smoke matrix."""

from __future__ import annotations

from .contracts import Fault, FaultLayer, TrialSpec


def initial_matrix() -> tuple[TrialSpec, ...]:
    incident = "online-boutique/adservice/replicas-zero"
    return (
        TrialSpec("guardian-nominal", incident, "adservice"),
        TrialSpec(
            "guardian-wrong-prediction",
            incident,
            "adservice",
            faults=(Fault("wrong_service", FaultLayer.PREDICTOR),),
        ),
        TrialSpec(
            "guardian-wrong-plus-overbroad-policy",
            incident,
            "adservice",
            faults=(
                Fault("wrong_service", FaultLayer.PREDICTOR),
                Fault("overbroad_scope", FaultLayer.POLICY),
            ),
        ),
        TrialSpec(
            "guardian-forged-authority",
            incident,
            "adservice",
            faults=(Fault("forged_authority", FaultLayer.BINDING),),
        ),
        TrialSpec(
            "guardian-stale-manifest",
            incident,
            "adservice",
            faults=(Fault("stale_manifest", FaultLayer.BINDING),),
        ),
        TrialSpec(
            "guardian-post-decision-substitution",
            incident,
            "adservice",
            faults=(Fault("argument_substitution", FaultLayer.ENFORCEMENT),),
        ),
        TrialSpec(
            "guardian-duplicate-retry",
            incident,
            "adservice",
            faults=(Fault("duplicate_retry", FaultLayer.ENFORCEMENT),),
        ),
        TrialSpec(
            "guardian-false-success",
            incident,
            "adservice",
            faults=(
                Fault("drop_effect", FaultLayer.ENFORCEMENT),
                Fault("false_success", FaultLayer.OBSERVATION),
            ),
        ),
        TrialSpec(
            "no-guard-wrong-prediction",
            incident,
            "adservice",
            guardrail="none",
            faults=(Fault("wrong_service", FaultLayer.PREDICTOR),),
        ),
    )


def baseline_matrix() -> tuple[TrialSpec, ...]:
    """Frozen proposal pairs for the first differential baseline smoke run."""
    incident = "online-boutique/adservice/replicas-zero"
    specs: list[TrialSpec] = []
    for guardrail in ("none", "schema_allowlist", "guardian"):
        specs.extend(
            (
                TrialSpec(
                    f"{guardrail}-nominal",
                    incident,
                    "adservice",
                    guardrail=guardrail,
                ),
                TrialSpec(
                    f"{guardrail}-wrong-prediction",
                    incident,
                    "adservice",
                    guardrail=guardrail,
                    faults=(Fault("wrong_service", FaultLayer.PREDICTOR),),
                ),
            )
        )
    return tuple(specs)


def policy_baseline_matrix() -> tuple[TrialSpec, ...]:
    """Frozen pairs spanning every guardrail in the confirmatory protocol."""
    incident = "online-boutique/adservice/replicas-zero"
    specs: list[TrialSpec] = []
    for guardrail in (
        "none",
        "schema_allowlist",
        "guardian",
        "external_policy",
        "always_deny",
    ):
        specs.extend(
            (
                TrialSpec(
                    f"{guardrail}-nominal",
                    incident,
                    "adservice",
                    guardrail=guardrail,
                ),
                TrialSpec(
                    f"{guardrail}-wrong-prediction",
                    incident,
                    "adservice",
                    guardrail=guardrail,
                    faults=(Fault("wrong_service", FaultLayer.PREDICTOR),),
                ),
            )
        )
    return tuple(specs)
