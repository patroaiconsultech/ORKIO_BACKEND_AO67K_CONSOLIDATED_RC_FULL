# AO67E — Main.py Slim Extraction Plan
# Destino real: app/runtime/main_slim_extraction_plan.py
# Modo: READONLY_CONTRACT / no runtime side effect
#
# Este módulo não altera fluxo. Ele documenta, de forma importável e auditável,
# onde o main.py deve ser progressivamente desinchado nas fases seguintes.
#
from __future__ import annotations

from typing import Any, Dict, List


MAIN_SLIM_EXTRACTION_PLAN_VERSION = "AO67E_MAIN_SLIM_EXTRACTION_PLAN_V1"


INSERTION_CORRIDOR = [
    "AO32_AFTER_RUNTIME_ENRICHMENT",
    "AO38C_SKIP_CONSTRAINTS_FOR_PLAIN_CONVERSATION",
    "AO34C_SIMPLE_CONVERSATION_BYPASS",
    "AO32_BEFORE_RAG",
    "AO32_BEFORE_AGENT_RUNTIME",
]


DO_NOT_TOUCH_IN_AO67E = [
    "app/main.py",
    "app/routes/realtime.py",
    "frontend",
    "database_migrations",
]


FUTURE_EXTRACTION_SEQUENCE = [
    {
        "phase": "AO67E",
        "status": "foundation_only",
        "goal": "Criar gateway e compatibilidade entre AO67B/AO67D sem editar main.py.",
    },
    {
        "phase": "AO67F",
        "status": "future",
        "goal": "Inserir chamada mínima ao chat_stream_decision_gateway antes do RAG/OpenAI.",
    },
    {
        "phase": "AO67G",
        "status": "future",
        "goal": "Extrair fast-paths públicos de main.py para runtime/public_chat_pipeline.py.",
    },
    {
        "phase": "AO67H",
        "status": "future",
        "goal": "Extrair eventos de execução/trace para service dedicado.",
    },
]


def build_main_slim_extraction_contract() -> Dict[str, Any]:
    return {
        "version": MAIN_SLIM_EXTRACTION_PLAN_VERSION,
        "strategy": "parallel_modular_foundation_before_main_py_edit",
        "public_speaker": "Orkio",
        "specialists_visible": False,
        "insert_before": "AO34C_SIMPLE_CONVERSATION_BYPASS / AO32_BEFORE_RAG",
        "current_patch_edits_main_py": False,
        "do_not_touch": list(DO_NOT_TOUCH_IN_AO67E),
        "insertion_corridor": list(INSERTION_CORRIDOR),
        "future_sequence": list(FUTURE_EXTRACTION_SEQUENCE),
        "rollback": "Não copiar/remover app/runtime/chat_stream_decision_gateway.py e restaurar journey_memory.py anterior se necessário.",
    }


def auditor_checklist() -> List[str]:
    return [
        "Confirmar que AO67E não altera main.py.",
        "Confirmar que journey_memory.py preserva funções AO67D e compatibilidade AO67B.",
        "Confirmar que agent_access_policy.py aceita kwargs do Decision Mesh.",
        "Confirmar que chat_stream_decision_gateway.py não chama LLM.",
        "Confirmar que commit_memory default é False.",
        "Confirmar que Orkio permanece único speaker público.",
        "Confirmar que o gateway falha aberto se alguma dependência modular não existir.",
    ]
