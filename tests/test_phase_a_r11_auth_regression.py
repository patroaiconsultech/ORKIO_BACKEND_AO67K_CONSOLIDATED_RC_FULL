from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "main.py").read_text(encoding="utf-8-sig")
TREE = ast.parse(SOURCE)
EXPECTED = {'forgot_password': '19401988f01913a3f01cae8f06f111e72fe64e980404ca756724d7d41d5e1411', 'reset_password': 'f04390cab41a7018ad70d920e6a81bcf26da44878c923a652affb9f922574244', 'change_password': 'b89fb1a1b53280d82a15b5c3512aad701e4536bc9616c0c781c17ec26bce9dcf', 'register': '42a99b6f161231d71b15d573af4c6193b539d30d4fbc686a346cb462845a7c82', 'login': 'a32fea598f47d9164d31f577402e5a46e06dc9c21300e0d30531623541c7478e', '_startup_access_gate_guard': '8cc19bc6d0f84035be1521481fcba8675231d4a8db342bf8fd5aebbba313b2a7'}


def _function_source(name: str) -> str:
    node = next(
        item for item in ast.walk(TREE)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == name
    )
    lines = SOURCE.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno])


def test_current_auth_and_access_gate_functions_are_preserved_exactly():
    observed = {
        name: hashlib.sha256(_function_source(name).encode("utf-8")).hexdigest()
        for name in EXPECTED
    }
    assert observed == EXPECTED


def test_auth_reset_migration_0038_is_preserved():
    path = ROOT / "alembic" / "versions" / "0038_patch_auth_password_reset_tokens.py"
    assert path.is_file()
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)

    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"revision", "down_revision"}:
                    values[target.id] = ast.literal_eval(node.value)

    assert values["revision"] == "0038_patch_auth_password_reset_tokens"
    assert values["down_revision"] == "0037_patch_evolution_signals_metrics"
    assert "password_reset_tokens" in source


def test_login_and_registration_gates_remain_separate():
    register = _function_source("register")
    login = _function_source("login")
    assert "access_gate_register_required()" in register
    assert "access_gate_login_required()" not in register
    assert "access_gate_login_required()" in login
    assert "access_gate_register_required()" not in login
