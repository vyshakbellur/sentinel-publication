"""
Guardian Layer 2: Intent Classifier

Routes agent requests by intent: READ, WRITE, TRADE, ADMIN, or UNKNOWN.
Supports both rule-based (deterministic) and LLM-based classification.

The Classifier determines the risk tier, which drives how much validation
is applied downstream (Principle 2: Progressive Cost).
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Types
# ─────────────────────────────────────────────────────────────────────────────

class IntentType(Enum):
    """Agent request intent categories, ordered by risk."""
    READ = "READ"               # Low risk: queries, lookups, balance checks
    WRITE = "WRITE"             # Medium risk: updates, modifications
    TRANSFORM = "TRANSFORM"     # Medium risk: data encoding, format shifting
    TRANSMIT = "TRANSMIT"       # High risk: outbound network connections
    TRADE = "TRADE"             # High risk: financial transactions, trades
    ADMIN = "ADMIN"             # Critical: system config, user management
    EXFILTRATION = "EXFILTRATION" # Critical: data movement out of trusted boundaries
    EXECUTION = "EXECUTION"     # Critical: running code, shell commands
    UNKNOWN = "UNKNOWN"         # Unclassifiable → automatically escalated


class RiskTier(Enum):
    """Risk tier derived from intent. Drives validation depth."""
    LOW = "LOW"           # Guard only (~3 checks, ~15ms)
    MEDIUM = "MEDIUM"     # Guard + Classifier (~6 checks, ~50ms)
    HIGH = "HIGH"         # Guard + Classifier + Verifier (~9 checks, ~150ms)
    CRITICAL = "CRITICAL" # Full pipeline + LLM deep analysis (~12 checks, ~5s)


# Intent → Risk mapping
INTENT_RISK_MAP: dict[IntentType, RiskTier] = {
    IntentType.READ: RiskTier.LOW,
    IntentType.WRITE: RiskTier.MEDIUM,
    IntentType.TRANSFORM: RiskTier.MEDIUM,
    IntentType.TRANSMIT: RiskTier.HIGH,
    IntentType.TRADE: RiskTier.HIGH,
    IntentType.ADMIN: RiskTier.CRITICAL,
    IntentType.EXFILTRATION: RiskTier.CRITICAL,
    IntentType.EXECUTION: RiskTier.CRITICAL,
    IntentType.UNKNOWN: RiskTier.CRITICAL,
}


@dataclass
class IntentClassification:
    """Result from intent classification with forensic metadata."""
    intent: IntentType
    risk_tier: RiskTier
    confidence: float        # 0.0-1.0
    method: str              # "rule" or "llm"
    reasoning: str           # Why this classification was chosen
    latency_ms: float        # Classification time
    metadata: dict[str, Any]


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ClassifierConfig:
    """Intent classification patterns and thresholds."""

    # ── Rule-based intent patterns (tool name → intent) ──────────────────
    read_tools: frozenset[str] = frozenset({
        "get_balance", "list_accounts", "read_config", "query_database",
        "fetch_data", "search", "list_users", "get_status", "describe",
        "view", "show", "display", "check", "monitor", "inspect",
    })

    write_tools: frozenset[str] = frozenset({
        "update_profile", "modify_settings", "create_record", "edit",
        "insert", "update", "patch", "set_config", "write", "save",
        "upload", "submit",
    })

    trade_tools: frozenset[str] = frozenset({
        "execute_trade", "transfer_funds", "place_order", "buy", "sell",
        "swap", "withdraw", "deposit", "send_payment", "authorize_payment",
    })

    admin_tools: frozenset[str] = frozenset({
        "delete_user", "grant_permission", "revoke_permission",
        "modify_system", "restart_service", "deploy", "rollback",
        "create_admin", "change_role", "reset_password",
        "modify_firewall", "update_policy",
    })

    exfiltration_tools: frozenset[str] = frozenset({
        "export_all", "send_webhook", "upload_external",
        "post_data", "send_email_external",
    })

    execution_tools: frozenset[str] = frozenset({
        "kubernetes_exec", "run_shell", "execute_command",
        "eval", "run_script", "download_external_binary",
    })

    # ── Keyword patterns for content-based classification ────────────────
    read_keywords: tuple[str, ...] = (
        r"\b(get|fetch|list|show|display|query|search|read|check|view|monitor)\b",
    )
    write_keywords: tuple[str, ...] = (
        r"\b(update|modify|change|set|create|insert|edit|write|save|upload)\b",
    )
    trade_keywords: tuple[str, ...] = (
        r"\b(trade|transfer|buy|sell|execute|order|payment|withdraw|deposit|swap)\b",
    )
    admin_keywords: tuple[str, ...] = (
        r"\b(admin|delete|remove|grant|revoke|deploy|restart|rollback|permission|role)\b",
    )
    exfiltration_keywords: tuple[str, ...] = (
        r"\b(export_all|webhook|post|external|upload_external|exfiltrate)\b",
    )
    execution_keywords: tuple[str, ...] = (
        r"\b(exec|run|shell|eval|script|binary)\b",
    )
    transform_tools: frozenset[str] = frozenset({"encode_data", "base64_encode", "encrypt", "zip_files"})
    transmit_tools: frozenset[str] = frozenset({"http_post", "curl", "send_webhook", "upload_file"})

    # ── LLM settings ────────────────────────────────────────────────────
    llm_provider: str = "ollama"
    llm_model: str = "gemma3:4b"
    llm_timeout_seconds: int = 30


DEFAULT_CLASSIFIER_CONFIG = ClassifierConfig()


# ─────────────────────────────────────────────────────────────────────────────
# Rule-based Classifier
# ─────────────────────────────────────────────────────────────────────────────

def _classify_by_tool_name(
    tool_name: str, cfg: ClassifierConfig
) -> tuple[IntentType, float] | None:
    """Classify intent by matching tool name against known categories."""
    tool_lower = tool_name.lower().strip()

    # Exact match
    if tool_lower in cfg.admin_tools:
        return (IntentType.ADMIN, 0.95)
    if tool_lower in cfg.trade_tools:
        return (IntentType.TRADE, 0.95)
    if tool_lower in cfg.exfiltration_tools:
        return (IntentType.EXFILTRATION, 0.95)
    if tool_lower in cfg.execution_tools:
        return (IntentType.EXECUTION, 0.95)
    if tool_lower in cfg.write_tools:
        return (IntentType.WRITE, 0.85)
    if tool_lower in cfg.read_tools:
        return (IntentType.READ, 0.85)
    if tool_lower in cfg.transform_tools:
        return (IntentType.TRANSFORM, 0.85)
    if tool_lower in cfg.transmit_tools:
        return (IntentType.TRANSMIT, 0.85)

    # Prefix match (e.g., "get_user_balance" → starts with "get")
    for prefix in ("get_", "list_", "fetch_", "show_", "describe_", "check_"):
        if tool_lower.startswith(prefix):
            return (IntentType.READ, 0.80)
    for prefix in ("update_", "modify_", "set_", "create_", "edit_"):
        if tool_lower.startswith(prefix):
            return (IntentType.WRITE, 0.80)
    for prefix in ("execute_", "transfer_", "buy_", "sell_"):
        if tool_lower.startswith(prefix):
            return (IntentType.TRADE, 0.80)
    for prefix in ("delete_", "grant_", "revoke_", "deploy_", "restart_"):
        if tool_lower.startswith(prefix):
            return (IntentType.ADMIN, 0.80)

    return None


def _classify_by_content(
    request: dict[str, Any], cfg: ClassifierConfig
) -> tuple[IntentType, float] | None:
    """Classify intent by keyword analysis of request content."""
    # Collect all text from the request
    text_parts = []
    for key, val in request.items():
        if isinstance(val, str):
            text_parts.append(val)
    combined = " ".join(text_parts).lower()

    if not combined:
        return None

    scores: dict[IntentType, int] = {
        IntentType.READ: 0,
        IntentType.WRITE: 0,
        IntentType.TRADE: 0,
        IntentType.ADMIN: 0,
        IntentType.EXFILTRATION: 0,
        IntentType.EXECUTION: 0,
    }

    for pattern in cfg.admin_keywords:
        scores[IntentType.ADMIN] += len(re.findall(pattern, combined))
    for pattern in cfg.trade_keywords:
        scores[IntentType.TRADE] += len(re.findall(pattern, combined))
    for pattern in cfg.exfiltration_keywords:
        scores[IntentType.EXFILTRATION] += len(re.findall(pattern, combined))
    for pattern in cfg.execution_keywords:
        scores[IntentType.EXECUTION] += len(re.findall(pattern, combined))
    for pattern in cfg.write_keywords:
        scores[IntentType.WRITE] += len(re.findall(pattern, combined))
    for pattern in cfg.read_keywords:
        scores[IntentType.READ] += len(re.findall(pattern, combined))

    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        return None

    total = sum(scores.values())
    confidence = scores[best] / total if total > 0 else 0
    return (best, round(min(0.85, 0.5 + confidence * 0.4), 2))


def _classify_rule(
    request: dict[str, Any], cfg: ClassifierConfig
) -> IntentClassification:
    """Rule-based intent classification (deterministic)."""
    start = time.perf_counter()

    raw_tool_name = request.get("tool_name", "")
    tool_name = raw_tool_name if isinstance(raw_tool_name, str) else ""
    reasoning_parts = []

    # Step 1: Try tool name matching
    tool_result = _classify_by_tool_name(tool_name, cfg) if tool_name else None
    if tool_result:
        intent, confidence = tool_result
        reasoning_parts.append(f"tool_name='{tool_name}' matched {intent.value}")
    else:
        # Step 2: Fall back to content analysis
        content_result = _classify_by_content(request, cfg)
        if content_result:
            intent, confidence = content_result
            reasoning_parts.append(f"content keywords matched {intent.value}")
        else:
            intent = IntentType.UNKNOWN
            confidence = 0.0
            reasoning_parts.append("no matching patterns found")

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return IntentClassification(
        intent=intent,
        risk_tier=INTENT_RISK_MAP[intent],
        confidence=confidence,
        method="rule",
        reasoning="; ".join(reasoning_parts),
        latency_ms=elapsed_ms,
        metadata={
            "layer": "classifier",
            "tool_name": tool_name,
            "timestamp": time.time(),
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# LLM-based Classifier
# ─────────────────────────────────────────────────────────────────────────────

_CLASSIFIER_PROMPT = """You are a security intent classifier for an agentic AI system.

Classify the following agent request into exactly ONE intent category:
- READ: Queries, lookups, data retrieval (low risk)
- WRITE: Updates, modifications, record creation (medium risk)
- TRADE: Financial transactions, fund transfers (high risk)
- ADMIN: System configuration, permission changes, privilege escalation (critical risk)
- EXFILTRATION: Moving data to external destinations, unauthorized export (critical risk)
- EXECUTION: Arbitrary code execution, shell commands (critical risk)

CRITICAL SECURITY RULES:
1. Tools that modify permissions (grant_*, revoke_*) → ALWAYS ADMIN
2. Tools with `system_prompt` or code payloads in parameters → ALWAYS ADMIN
3. Tools moving data to external destinations (export_all, webhook, post) → ALWAYS EXFILTRATION
4. Packages or plugins from unknown sources → ALWAYS EXECUTION (Supply chain risk)
5. Shell execution or file deletion → ALWAYS EXECUTION

Request:
{request_json}

Respond with ONLY this JSON (no markdown, no explanation):
{{"intent": "<READ|WRITE|TRADE|ADMIN|EXFILTRATION|EXECUTION>", "confidence": <0.0-1.0>, "reasoning": "<one sentence>"}}"""


def _call_ollama(prompt: str, model: str, timeout: int) -> dict:
    """Call Ollama for intent classification."""
    import requests as req
    try:
        resp = req.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "")
        # Extract JSON from response
        import re as _re
        match = _re.search(r'\{[^}]+\}', text)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {}


def _classify_llm(
    request: dict[str, Any], cfg: ClassifierConfig
) -> IntentClassification:
    """LLM-based intent classification (Principle 3: Independent Verification)."""
    start = time.perf_counter()

    # Build prompt with sanitized request
    safe_request = {k: v for k, v in request.items() if not k.startswith("_")}
    prompt = _CLASSIFIER_PROMPT.format(
        request_json=json.dumps(safe_request, indent=2, default=str)[:2000]
    )

    result = _call_ollama(prompt, cfg.llm_model, cfg.llm_timeout_seconds)

    intent_str = result.get("intent", "UNKNOWN").upper()
    try:
        intent = IntentType(intent_str)
    except ValueError:
        intent = IntentType.UNKNOWN

    confidence = float(result.get("confidence", 0.5))
    reasoning = result.get("reasoning", "LLM fallback parsing")

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return IntentClassification(
        intent=intent,
        risk_tier=INTENT_RISK_MAP[intent],
        confidence=round(confidence, 3),
        method="llm",
        reasoning=reasoning,
        latency_ms=elapsed_ms,
        metadata={
            "layer": "classifier",
            "llm_model": cfg.llm_model,
            "llm_provider": cfg.llm_provider,
            "timestamp": time.time(),
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def classify_intent(
    request: dict[str, Any],
    method: str = "rule",
    config: ClassifierConfig | None = None,
) -> IntentClassification:
    """Classify the intent of an agent request.

    Args:
        request: Agent request dict with keys like 'tool_name', 'parameters', etc.
        method:  "rule" for deterministic classification, "llm" for LLM-based.
        config:  Classifier configuration. Uses DEFAULT_CLASSIFIER_CONFIG if None.

    Returns:
        IntentClassification with intent type, risk tier, confidence, and metadata.
    """
    cfg = config or DEFAULT_CLASSIFIER_CONFIG

    if method == "llm":
        return _classify_llm(request, cfg)
    return _classify_rule(request, cfg)
