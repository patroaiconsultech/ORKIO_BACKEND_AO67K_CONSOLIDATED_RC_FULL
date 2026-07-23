from __future__ import annotations

from typing import Iterable, Sequence


class CommandPolicyError(ValueError):
    pass


class CommandPolicy:
    ALLOWED_PREFIXES = (
        ("python", "-m", "pytest"),
        ("python", "-m", "compileall"),
        ("python", "-m", "py_compile"),
    )
    FORBIDDEN_TOKENS = {
        "git", "push", "deploy", "railway", "docker", "curl", "wget",
        "bash", "sh", "powershell", "rm", "sudo",
    }

    def validate(self, command: Sequence[str]) -> list[str]:
        parts = [str(item) for item in command]
        if not parts:
            raise CommandPolicyError("empty_command")
        lowered = [item.lower() for item in parts]
        if any(token in self.FORBIDDEN_TOKENS for token in lowered):
            raise CommandPolicyError("forbidden_command_token")
        if not any(tuple(lowered[:len(prefix)]) == prefix for prefix in self.ALLOWED_PREFIXES):
            raise CommandPolicyError("command_not_allowlisted")
        return parts
