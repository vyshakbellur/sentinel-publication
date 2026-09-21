"""SENTINEL effect-grounded guardrail experiments."""

from .contracts import Fault, FaultLayer, TrialRecord, TrialSpec
from .harness import run_matrix, run_trial

__all__ = [
    "Fault",
    "FaultLayer",
    "TrialRecord",
    "TrialSpec",
    "run_matrix",
    "run_trial",
]

