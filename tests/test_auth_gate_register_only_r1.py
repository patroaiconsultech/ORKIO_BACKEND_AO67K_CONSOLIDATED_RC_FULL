from __future__ import annotations

import os
from unittest.mock import patch

from app.services.access_grant_service import (
    access_gate_login_required,
    access_gate_register_required,
    load_access_grant_config,
)


def _base_env() -> dict[str, str]:
    return {
        "ACCESS_GATE_SERVER_SIDE_ONLY": "true",
        "ACCESS_GATE_SIGNING_KEY": "x" * 64,
    }


def test_login_is_not_gated_by_default() -> None:
    with patch.dict(os.environ, _base_env(), clear=False):
        os.environ.pop("ACCESS_GATE_REQUIRE_FOR_LOGIN", None)
        os.environ.pop("ACCESS_GATE_REQUIRE_FOR_REGISTER", None)
        os.environ.pop("ACCESS_GATE_REQUIRE_FOR_AUTH", None)
        assert access_gate_login_required() is False


def test_register_inherits_legacy_auth_flag() -> None:
    env = {
        **_base_env(),
        "ACCESS_GATE_REQUIRE_FOR_AUTH": "true",
    }
    with patch.dict(os.environ, env, clear=False):
        os.environ.pop("ACCESS_GATE_REQUIRE_FOR_REGISTER", None)
        assert access_gate_register_required() is True


def test_route_specific_flags_override_legacy() -> None:
    env = {
        **_base_env(),
        "ACCESS_GATE_REQUIRE_FOR_AUTH": "true",
        "ACCESS_GATE_REQUIRE_FOR_REGISTER": "true",
        "ACCESS_GATE_REQUIRE_FOR_LOGIN": "false",
    }
    with patch.dict(os.environ, env, clear=False):
        config = load_access_grant_config()
        assert config.require_for_register is True
        assert config.require_for_login is False
