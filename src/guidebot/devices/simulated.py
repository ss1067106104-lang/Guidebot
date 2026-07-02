"""In-memory robot used for development before physical hardware exists."""

from __future__ import annotations

import asyncio

from guidebot.models import Action, Reading


class SimulatedDevice:
    name = "simulator"

    def __init__(self) -> None:
        self._readings: asyncio.Queue[Reading] = asyncio.Queue()
        self.executed_actions: list[Action] = []
        self.running = False

    async def start(self) -> None:
        self.running = True

    async def stop(self) -> None:
        self.running = False

    async def emit(self, reading: Reading) -> None:
        await self._readings.put(reading)

    async def read(self) -> Reading | None:
        return await self._readings.get()

    async def execute(self, action: Action) -> None:
        if not self.running:
            raise RuntimeError("device is not running")
        self.executed_actions.append(action)

