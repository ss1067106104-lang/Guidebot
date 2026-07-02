"""Deterministic policy gate between probabilistic agents and the physical world."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Action, ActionKind, RobotState


@dataclass(frozen=True, slots=True)
class SafetyResult:
    allowed: bool
    reason: str


class SafetyPolicy:
    """Hard limits are code/config, never an evolvable skill."""

    def __init__(self, min_hvac_c: float = 16.0, max_hvac_c: float = 30.0) -> None:
        self.min_hvac_c = min_hvac_c
        self.max_hvac_c = max_hvac_c
        self.allowed_actions = frozenset(ActionKind)

    def evaluate(self, action: Action, state: RobotState) -> SafetyResult:
        if action.kind not in self.allowed_actions:
            return SafetyResult(False, "action type is not allow-listed")

        if action.kind is ActionKind.SET_HVAC:
            target = action.parameters.get("target_c")
            if not isinstance(target, (int, float)):
                return SafetyResult(False, "HVAC target must be numeric")
            if not self.min_hvac_c <= float(target) <= self.max_hvac_c:
                return SafetyResult(False, "HVAC target is outside the hard safety range")

        if action.kind is ActionKind.MOVE:
            speed = action.parameters.get("speed", 0)
            if not isinstance(speed, (int, float)) or not 0 <= float(speed) <= 1:
                return SafetyResult(False, "motion speed must be within 0..1")

        return SafetyResult(True, "allowed")

