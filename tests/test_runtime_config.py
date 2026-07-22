import os
import unittest
from unittest.mock import patch

from runtime.access_mode import load_access_runtime_config
from runtime.ocil_config import load_ocil_runtime_config


class RuntimeConfigTests(unittest.TestCase):
    def test_safe_ocil_disabled_shadow(self):
        env = {
            "OCIL_ENABLED": "false",
            "OCIL_SHADOW_MODE": "true",
            "OCIL_ATTACHMENT_ENFORCEMENT": "false",
            "OCIL_EXECUTION_ENFORCEMENT": "false",
        }
        with patch.dict(os.environ, env, clear=False):
            cfg = load_ocil_runtime_config()
        self.assertFalse(cfg.enabled)
        self.assertTrue(cfg.shadow_mode)
        self.assertFalse(cfg.enforcement_active)

    def test_reject_enforcement_while_disabled(self):
        env = {
            "OCIL_ENABLED": "false",
            "OCIL_SHADOW_MODE": "false",
            "OCIL_EXECUTION_ENFORCEMENT": "true",
        }
        with patch.dict(os.environ, env, clear=False):
            with self.assertRaisesRegex(
                ValueError,
                "ocil_enforcement_requires_ocil_enabled",
            ):
                load_ocil_runtime_config()

    def test_reject_shadow_enforcement(self):
        env = {
            "OCIL_ENABLED": "true",
            "OCIL_SHADOW_MODE": "true",
            "OCIL_ATTACHMENT_ENFORCEMENT": "true",
        }
        with patch.dict(os.environ, env, clear=False):
            with self.assertRaisesRegex(
                ValueError,
                "ocil_shadow_mode_cannot_enforce",
            ):
                load_ocil_runtime_config()

    def test_access_open(self):
        with patch.dict(os.environ, {"ACCESS_MODE": "open"}, clear=False):
            cfg = load_access_runtime_config()
        self.assertTrue(cfg.is_open)
        self.assertFalse(cfg.register_requires_code)


if __name__ == "__main__":
    unittest.main()
