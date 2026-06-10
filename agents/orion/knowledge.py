from __future__ import annotations

from app.agents.base import KnowledgeCard


ORION_KNOWLEDGE_VERSION = "AO67C_ORION_KNOWLEDGE_V1"


def get_knowledge_cards() -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            card_id="orion.architecture.runtime",
            agent_id="orion",
            title="Arquitetura e runtime",
            summary=(
                "Sinal interno para avaliar separação de camadas, runtime, policies, hooks, main.py, frontend e risco de acoplamento."
            ),
            domains=("architecture", "runtime", "backend", "frontend"),
            triggers=("arquitetura", "runtime", "main.py", "backend", "frontend", "appconsole", "hook", "mesh", "policy"),
            public_safe=False,
            internal_only=True,
            priority=40,
        ),
        KnowledgeCard(
            card_id="orion.governance.safety",
            agent_id="orion",
            title="Governança técnica e segurança",
            summary=(
                "Sinal interno para identificar riscos de vazamento de bastidores, agentes internos, branch, deploy, patch e execução técnica."
            ),
            domains=("governance", "security", "visibility"),
            triggers=("governança", "governanca", "segurança", "seguranca", "auditoria", "patch", "branch", "deploy", "autoevolução", "autoevolucao"),
            public_safe=False,
            internal_only=True,
            priority=41,
        ),
        KnowledgeCard(
            card_id="orion.integration.risk",
            agent_id="orion",
            title="Risco de integração",
            summary=(
                "Sinal interno para orientar rollout em fases, rollback, staging, py_compile e validação antes de produção."
            ),
            domains=("deploy_risk", "rollback", "staging", "validation"),
            triggers=("deploy", "produção", "producao", "staging", "rollback", "compile", "py_compile", "regressão", "regressao"),
            public_safe=False,
            internal_only=True,
            priority=42,
        ),
    ]
