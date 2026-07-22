from __future__ import annotations

from dataclasses import dataclass
import os


_ALLOWED_MODES = {"open", "invite_only", "private"}


@dataclass(frozen=True)
class AccessRuntimeConfig:
    mode: str

    @property
    def is_open(self) -> bool:
        return self.mode == "open"

    @property
    def register_requires_code(self) -> bool:
        return self.mode != "open"

    @property
    def login_requires_grant(self) -> bool:
        return self.mode == "private"


def load_access_runtime_config() -> AccessRuntimeConfig:
    mode = os.getenv("ACCESS_MODE", "invite_only").strip().lower()
    if mode not in _ALLOWED_MODES:
        raise ValueError(
            "invalid_access_mode:"
            f"{mode};expected_one_of={','.join(sorted(_ALLOWED_MODES))}"
        )
    return AccessRuntimeConfig(mode=mode)
