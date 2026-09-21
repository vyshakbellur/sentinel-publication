from typing import Any

from guardian.layers.progressive_cost import GuardianConfig, validate_request
from guardian.layers.state_tracker import StatefulDetector


class ToolAuthorizationGateway:
    """
    Integrates point-in-time stateless validation (validate_request) with 
    stateful consequence tracking (StatefulDetector) without polluting the 
    core pipeline logic.

    This acts as a wrapper around a tool execution environment.
    """

    def __init__(self, detector: StatefulDetector, config: GuardianConfig = None):
        self.detector = detector
        self.config = config or GuardianConfig(mode="progressive")

    def authorize_action(
        self,
        session_id: str,
        request: dict[str, Any],
        user_permissions: dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Evaluate if an action is authorized to execute.
        Returns (is_authorized, reason)
        """
        # 1. Point-in-time stateless policy check
        stateless_result = validate_request(request, user_permissions, self.config)

        if stateless_result.decision != "ALLOW":
            return False, f"Stateless Policy: {stateless_result.decision}"

        # 2. Stateful consequence check
        is_blocked, block_reason = self.detector.evaluate_action(session_id, request)
        if is_blocked:
            return False, f"Stateful Tracker: {block_reason}"

        return True, "Authorized"
