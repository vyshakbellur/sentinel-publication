import time
from typing import Any


class SessionState:
    """Tracks cumulative properties of an agent session using data lineage."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        # Tracks which data_ids contain sensitive information
        self.sensitive_data_ids: set[str] = set()
        # Tracks which data_ids have been transformed
        self.transformed_data_ids: set[str] = set()
        self.action_history: list[dict[str, Any]] = []
        self.last_updated = time.time()

    def update(self, action: dict[str, Any], classification: str):
        """Update session state based on a new action."""
        self.action_history.append(action)
        self.last_updated = time.time()

        # Extract data flow parameters
        outputs = action.get("outputs", [])
        inputs = action.get("inputs", [])

        # If action reads sensitive data, mark outputs as sensitive
        if classification in ("secret", "confidential"):
            for out_id in outputs:
                self.sensitive_data_ids.add(out_id)

        # If action uses sensitive inputs, taint the outputs
        for in_id in inputs:
            if in_id in self.sensitive_data_ids:
                for out_id in outputs:
                    self.sensitive_data_ids.add(out_id)

            if in_id in self.transformed_data_ids:
                for out_id in outputs:
                    self.transformed_data_ids.add(out_id)

        # Track if data is being transformed/encoded
        if action.get("operation") == "encode" or action.get("tool_name") == "encode_data":
            for out_id in outputs:
                self.transformed_data_ids.add(out_id)


class StatefulDetector:
    """Detects cumulative consequence violations using data provenance."""

    def __init__(self):
        self.sessions: dict[str, SessionState] = {}

    def get_session(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id)
        return self.sessions[session_id]

    def evaluate_action(self, session_id: str, action: dict[str, Any]) -> tuple[bool, str]:
        """
        Evaluates whether the next action violates cumulative boundaries.
        Returns (is_blocked, reason).
        """
        if not isinstance(session_id, str) or not session_id.strip():
            return True, "stateful_block:malformed_session_id"
        if not isinstance(action, dict):
            return True, "stateful_block:malformed_action"

        session = self.get_session(session_id)

        source = action.get("source", {})
        dest = action.get("destination", {})
        inputs = action.get("inputs", [])

        if not isinstance(source, dict) or not isinstance(dest, dict):
            return True, "stateful_block:malformed_provenance"
        if not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs):
            return True, "stateful_block:malformed_inputs"
        outputs = action.get("outputs", [])
        if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
            return True, "stateful_block:malformed_outputs"

        current_class = source.get("classification", "")
        current_trust = dest.get("trust_domain", "")
        operation = action.get("operation", "")

        if not all(isinstance(value, str) for value in (
            current_class, current_trust, operation,
        )):
            return True, "stateful_block:malformed_attributes"

        current_class = current_class.lower()
        current_trust = current_trust.lower()
        operation = operation.lower()

        # Check if the action is trying to transmit sensitive data
        is_transmitting = operation in ("transmit", "execute", "http_post")
        is_external = current_trust.startswith("external")

        if is_transmitting and is_external:
            # Check if any input to this transmission is tainted
            for in_id in inputs:
                if in_id in session.sensitive_data_ids:
                    # If it was also transformed, this is a clear evasion attempt
                    if in_id in session.transformed_data_ids:
                        return True, "stateful_block:obfuscated_sensitive_data_to_external"
                    return True, "stateful_block:sensitive_data_to_external"

        # Update actual state if permitted
        session.update(action, current_class)

        return False, "allowed"
