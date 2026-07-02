"""Developer-facing simulation command."""

from __future__ import annotations

import argparse
import asyncio

from .devices import SimulatedDevice
from .hub import GuidebotHub
from .models import Reading, SensorKind


async def run_demo() -> None:
    device = SimulatedDevice()
    hub = GuidebotHub(device)
    await hub.start()
    samples = (
        Reading(SensorKind.TEMPERATURE, 29.2, "°C", "simulator"),
        Reading(SensorKind.TOUCH, True, source="simulator"),
        Reading(SensorKind.AIR_QUALITY, 126, "AQI", "simulator"),
    )
    for sample in samples:
        trajectory = await hub.ingest(sample)
        print(f"[{sample.kind}] {trajectory.decision.response or '已记录，无需动作'}")
    await hub.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Guidebot development runtime")
    parser.add_argument("command", choices=("demo",), nargs="?", default="demo")
    parser.parse_args()
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()

