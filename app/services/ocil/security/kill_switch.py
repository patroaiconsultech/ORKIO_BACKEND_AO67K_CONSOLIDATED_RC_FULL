from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KillSwitch:
    engaged: bool = False
    reason: str = ""

    def engage(self, reason: str) -> None:
        self.engaged = True
        self.reason = reason or "manual_kill_switch"

    def reset(self) -> None:
        self.engaged = False
        self.reason = ""

    def assert_safe(self) -> None:
        if self.engaged:
            raise RuntimeError(f"OCIL_KILL_SWITCH_ENGAGED: {self.reason}")
