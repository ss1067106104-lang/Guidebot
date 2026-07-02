from __future__ import annotations

from guidebot.devices import SimulatedDevice
from guidebot.hub import GuidebotHub
from guidebot.models import Action, ActionKind, Decision, Event, Reading, RobotState, SensorKind


async def test_hot_room_triggers_safe_hvac_action() -> None:
    device = SimulatedDevice()
    hub = GuidebotHub(device)
    await hub.start()

    trajectory = await hub.ingest(Reading(SensorKind.TEMPERATURE, 29.5, "°C", "test"))

    assert trajectory.accepted_actions[0].kind is ActionKind.SET_HVAC
    assert hub.state.hvac_target_c == 25
    assert device.executed_actions == list(trajectory.accepted_actions)


async def test_touch_gets_a_social_response() -> None:
    device = SimulatedDevice()
    hub = GuidebotHub(device)
    await hub.start()

    trajectory = await hub.ingest(Reading(SensorKind.TOUCH, True, source="test"))

    assert trajectory.decision.response == "嘿，我在呢。"
    assert trajectory.accepted_actions[0].kind is ActionKind.SPEAK


async def test_device_reading_can_flow_through_runtime_loop() -> None:
    device = SimulatedDevice()
    hub = GuidebotHub(device)
    await hub.start()
    await device.emit(Reading(SensorKind.AIR_QUALITY, 120, "AQI", "test"))

    trajectory = await hub.run_once()

    assert trajectory is not None
    assert trajectory.accepted_actions[0].kind is ActionKind.NOTIFY
    scored = hub.record_feedback(0, 1.0, "good warning")
    assert scored.score == 1.0


class UnsafeAgent:
    async def decide(self, event: Event, state: RobotState) -> Decision:
        return Decision((Action(ActionKind.SET_HVAC, {"target_c": 45}, "bad plan"),))


async def test_safety_gate_rejects_unsafe_agent_action() -> None:
    device = SimulatedDevice()
    hub = GuidebotHub(device, agent=UnsafeAgent())
    await hub.start()

    trajectory = await hub.say("make it hot")

    assert not trajectory.accepted_actions
    assert len(trajectory.rejected_actions) == 1
    assert not device.executed_actions
