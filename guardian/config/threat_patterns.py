"""
Guardian Config: Threat Patterns

Known attack signatures for the Guard layer's regex screening.
Organized by threat category for traceability.
"""

from __future__ import annotations

# ── Prompt Injection patterns ────────────────────────────────────────────────
INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"system\s*prompt\s*[:=]",
    r"forget\s+(all\s+)?(your\s+)?instructions",
    r"do\s+not\s+follow\s+(the\s+)?(above|previous)",
    r"override\s+(system|safety)\s+(prompt|instructions|settings)",
    r"act\s+as\s+(if|though)\s+you\s+(are|were)\s+(a|an)\s+unrestricted",
    r"jailbreak",
    r"DAN\s*mode",
    r"\bexfiltrate\b",
    r"reveal\s+(your|the)\s+(system|hidden)\s+prompt",
    r"output\s+(your|the)\s+(initial|system)\s+instructions",
    r"repeat\s+(everything|all)\s+(above|before)\s+this",
    r"what\s+(is|are)\s+your\s+(instructions|rules|system\s+prompt)",
    r"pretend\s+you\s+(have|are)\s+no\s+(restrictions|rules|limits)",
]

# ── Tool Poisoning patterns (malicious tool descriptions) ────────────────────
TOOL_POISONING_PATTERNS: list[str] = [
    r"system_prompt",            # HiddenLayer-style parameter renaming
    r"internal_state",           # Leaking internal model state
    r"send_to_external",         # Exfiltration via tool output
    r"hidden_parameter",         # Concealed parameters
    r"callback_url",             # Callback-based exfiltration
    r"webhook.*secret",          # Secret leaking via webhook
]

# ── SQL Injection patterns ───────────────────────────────────────────────────
SQL_INJECTION_PATTERNS: list[str] = [
    r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER)\s+",
    r"'\s*(OR|AND)\s+['\d]",
    r"UNION\s+SELECT",
    r"--\s*$",
    r"\/\*.*\*\/",
]

# ── Code Injection patterns ─────────────────────────────────────────────────
CODE_INJECTION_PATTERNS: list[str] = [
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__\s*\(",
    r"subprocess\.(call|run|Popen)",
    r"os\.system\s*\(",
    r"<script[\s>]",
    r"\.\./\.\./",
]

# ── All patterns combined (for quick loading) ────────────────────────────────
ALL_THREAT_PATTERNS: dict[str, list[str]] = {
    "injection": INJECTION_PATTERNS,
    "tool_poisoning": TOOL_POISONING_PATTERNS,
    "sql_injection": SQL_INJECTION_PATTERNS,
    "code_injection": CODE_INJECTION_PATTERNS,
}
