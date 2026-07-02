from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

# Permite imports como app.services, app.runtime, app.self_heal
# apontando para os diretórios reais na raiz do repo.
__path__.append(str(_ROOT))
