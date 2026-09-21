"""
Guardian Config: Tool Registry

Registered tools with their permission levels and risk classifications.
Each tool specifies what intent type it represents and what permissions
are required to invoke it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDefinition:
    """A registered tool in the agentic system."""
    name: str
    intent: str              # READ, WRITE, TRADE, ADMIN
    min_permission: str      # Minimum required permission level
    description: str
    risk_score: float        # 0.0-1.0 inherent risk


# ── Financial services tool registry ─────────────────────────────────────────
TOOL_REGISTRY: dict[str, ToolDefinition] = {
    # READ tools (low risk)
    "get_balance": ToolDefinition(
        "get_balance", "READ", "READ", "Retrieve account balance", 0.05),
    "list_accounts": ToolDefinition(
        "list_accounts", "READ", "READ", "List user's accounts", 0.05),
    "get_portfolio": ToolDefinition(
        "get_portfolio", "READ", "READ", "Retrieve portfolio allocations", 0.1),
    "search_transactions": ToolDefinition(
        "search_transactions", "READ", "READ", "Search transaction history", 0.15),

    # WRITE tools (medium risk)
    "update_profile": ToolDefinition(
        "update_profile", "WRITE", "WRITE", "Update user profile", 0.3),
    "create_alert": ToolDefinition(
        "create_alert", "WRITE", "WRITE", "Create price alert", 0.2),
    "modify_settings": ToolDefinition(
        "modify_settings", "WRITE", "WRITE", "Modify account settings", 0.35),

    # TRADE tools (high risk)
    "execute_trade": ToolDefinition(
        "execute_trade", "TRADE", "TRADE", "Execute a financial trade", 0.75),
    "transfer_funds": ToolDefinition(
        "transfer_funds", "TRADE", "TRADE", "Transfer funds between accounts", 0.8),
    "place_order": ToolDefinition(
        "place_order", "TRADE", "TRADE", "Place a buy/sell order", 0.7),

    # ADMIN tools (critical risk)
    "grant_permission": ToolDefinition(
        "grant_permission", "ADMIN", "ADMIN", "Grant user permissions", 0.9),
    "deploy_model": ToolDefinition(
        "deploy_model", "ADMIN", "ADMIN", "Deploy a new model version", 0.95),
    "modify_policy": ToolDefinition(
        "modify_policy", "ADMIN", "ADMIN", "Modify security policy", 1.0),
}
