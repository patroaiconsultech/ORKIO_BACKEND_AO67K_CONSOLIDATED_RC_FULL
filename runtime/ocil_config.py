from __future__ import annotations

from dataclasses import dataclass
import os


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default

    normalized = str(raw).strip().strip('"').strip("'").lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False

    raise ValueError(f"invalid_boolean_env:{name}")


@dataclass(frozen=True)
class OCILRuntimeConfig:
    enabled: bool
    shadow_mode: bool
    attachment_enforcement: bool
    execution_enforcement: bool

    @property
    def enforcement_active(self) -> bool:
        return (
            self.enabled
            and not self.shadow_mode
            and (
                self.attachment_enforcement
                or self.execution_enforcement
            )
        )


def validate_ocil_runtime_config(config: OCILRuntimeConfig) -> None:
    if not config.enabled and (
        config.attachment_enforcement
        or config.execution_enforcement
    ):
        raise ValueError("ocil_enforcement_requires_ocil_enabled")

    if config.shadow_mode and (
        config.attachment_enforcement
        or config.execution_enforcement
    ):
        raise ValueError("ocil_shadow_mode_cannot_enforce")


def load_ocil_runtime_config() -> OCILRuntimeConfig:
    config = OCILRuntimeConfig(
        enabled=env_bool("OCIL_ENABLED", False),
        shadow_mode=env_bool("OCIL_SHADOW_MODE", True),
        attachment_enforcement=env_bool(
            "OCIL_ATTACHMENT_ENFORCEMENT",
            False,
        ),
        execution_enforcement=env_bool(
            "OCIL_EXECUTION_ENFORCEMENT",
            False,
        ),
    )
    validate_ocil_runtime_config(config)
    return config
