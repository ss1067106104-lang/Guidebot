"""Hardware abstraction contracts."""

from __future__ import annotations

from typing import Protocol

from guidebot.models import Action, Reading


class DeviceAdapter(Protocol):
    name: str

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def read(self) -> Reading | None: ...

    async def execute(self, action: Action) -> None: ...

