from __future__ import annotations

"""
AO67B — Hook Registry

Objetivo:
- Transformar capacidades em hooks auditáveis.
- Permitir que o Orkio consulte sinais internos sem transformar especialistas em
  personas públicas.
- Manter Orkio como único speaker público.

Este módulo não chama LLM, não acessa banco, não escreve arquivos e não faz
deploy. Ele apenas registra e seleciona hooks por intenção.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


HOOK_REGISTRY_VERSION = "AO68G_PATROAI_IDENTITY_AMCHAM_ON_DEMAND_V1"

PUBLIC_VISIBLE_AGENT_ID = "orkio"
PUBLIC_VISIBLE_AGENT_NAME = "Orkio"


def strip_accents(value: Any) -> str:
    raw = str(value or "")
    normalized = unicodedata.normalize("NFD", raw)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_text(value: Any) -> str:
    raw = strip_accents(value).lower()
    raw = re.sub(r"[^a-z0-9_@/\-\s]+", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def contains_any(text: Any, markers: Iterable[str]) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(marker) in normalized for marker in markers if str(marker or "").strip())


@dataclass(frozen=True)
class HookSpec:
    hook_id: str
    family: str
    label: str
    description: str
    triggers: tuple[str, ...] = field(default_factory=tuple)
    priority: int = 100
    public_safe: bool = True
    internal_only: bool = False
    visible_agent: str = PUBLIC_VISIBLE_AGENT_NAME
    synthesis_role: str = "signal"

    def score(self, message: Any) -> float:
        normalized = normalize_text(message)
        if not normalized:
            return 0.0

        hits = 0
        strong_hits = 0
        for marker in self.triggers:
            marker_norm = normalize_text(marker)
            if not marker_norm:
                continue
            if marker_norm in normalized:
                hits += 1
                if " " in marker_norm or len(marker_norm) >= 8:
                    strong_hits += 1

        if hits <= 0:
            return 0.0

        base = min(0.92, 0.34 + (hits * 0.14) + (strong_hits * 0.16))
        if self.family == "guard":
            base = min(0.98, base + 0.12)
        return round(base, 3)

    def to_dict(self, *, public: bool = False, include_triggers: bool = False) -> Dict[str, Any]:
        data = {
            "hook_id": self.hook_id,
            "family": self.family,
            "label": self.label if not public else _public_label(self),
            "description": self.description if not public else _public_description(self),
            "priority": self.priority,
            "public_safe": bool(self.public_safe),
            "internal_only": bool(self.internal_only),
            "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
            "synthesis_role": self.synthesis_role,
        }
        if include_triggers and not public:
            data["triggers"] = list(self.triggers)
        return data


def _public_label(hook: HookSpec) -> str:
    # Nunca exponha especialistas internos. O público só vê capacidades genéricas.
    if hook.family == "specialist":
        return "capacidade especializada interna"
    if hook.family == "guard":
        return "proteção de superfície pública"
    return hook.label


def _public_description(hook: HookSpec) -> str:
    if hook.internal_only or hook.family == "specialist":
        return "Sinal interno usado pelo Orkio para decidir melhor, sem expor agentes internos."
    return hook.description


_HOOKS: Dict[str, HookSpec] = {}


def register_hook(spec: HookSpec) -> HookSpec:
    if not isinstance(spec, HookSpec):
        raise TypeError("register_hook expects HookSpec")
    if not spec.hook_id:
        raise ValueError("hook_id is required")
    _HOOKS[spec.hook_id] = spec
    return spec


def get_hook(hook_id: str) -> Optional[HookSpec]:
    return _HOOKS.get(str(hook_id or "").strip())


def all_hooks(*, include_internal: bool = True) -> List[HookSpec]:
    items = list(_HOOKS.values())
    if not include_internal:
        items = [hook for hook in items if not hook.internal_only]
    return sorted(items, key=lambda hook: (hook.priority, hook.hook_id))


def select_hooks(
    message: Any,
    *,
    include_internal: bool = True,
    include_guards: bool = True,
    max_hooks: int = 6,
    min_score: float = 0.34,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    for hook in all_hooks(include_internal=include_internal):
        if hook.family == "guard" and not include_guards:
            continue
        score = hook.score(message)
        if score < min_score:
            continue
        payload = hook.to_dict(public=False, include_triggers=False)
        payload["score"] = score
        candidates.append(payload)

    candidates.sort(key=lambda item: (-float(item.get("score") or 0), int(item.get("priority") or 100), str(item.get("hook_id") or "")))
    return candidates[: max(1, int(max_hooks or 1))]


def public_hook_summary(selected_hooks: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    public_items: List[Dict[str, Any]] = []
    for item in selected_hooks or []:
        hook = get_hook(str(item.get("hook_id") or ""))
        if not hook:
            continue
        public_item = hook.to_dict(public=True, include_triggers=False)
        public_item["score"] = item.get("score")
        public_items.append(public_item)
    return public_items


def hook_runtime_hints(
    selected_hooks: Iterable[Dict[str, Any]],
    *,
    reason: str = "orkio_decision_mesh_hooks",
    route_family: str = "decision_mesh",
) -> Dict[str, Any]:
    selected = list(selected_hooks or [])
    return {
        "routing": {
            "routing_source": "hook_registry",
            "route_applied": bool(selected),
            "route_family": route_family,
            "route_reason": reason,
            "policy_version": HOOK_REGISTRY_VERSION,
            "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
        },
        "hook_registry": {
            "version": HOOK_REGISTRY_VERSION,
            "selected_hook_ids": [str(item.get("hook_id") or "") for item in selected],
            "selected_families": sorted({str(item.get("family") or "") for item in selected if item.get("family")}),
            "public_summary": public_hook_summary(selected),
        },
    }


def _seed_hooks() -> None:
    # Guard hooks: devem ter prioridade alta e entrar antes de qualquer síntese.
    register_hook(HookSpec(
        hook_id="guard.agent_catalog",
        family="guard",
        label="catálogo público de agentes",
        description="Bloqueia listagem pública de agentes internos e responde com Orkio como condutor.",
        triggers=(
            "quais agentes", "que agentes", "agentes especializados", "especialistas existem",
            "existem na plataforma", "quem pode ajudar", "lista de agentes", "catalogo de agentes",
            "catálogo de agentes",
        ),
        priority=1,
        synthesis_role="block_public_catalog",
    ))
    register_hook(HookSpec(
        hook_id="guard.internal_agent_request",
        family="guard",
        label="pedido de agente interno",
        description="Converte pedidos por agentes internos em resposta pública conduzida pelo Orkio.",
        triggers=(
            "chama o chris", "chame o chris", "chama chris", "chris",
            "chama o orion", "chame o orion", "chama orion", "orion",
            "cfo", "cto", "auditor", "planner",
        ),
        priority=2,
        synthesis_role="block_internal_agent",
    ))
    register_hook(HookSpec(
        hook_id="guard.technical_governance",
        family="guard",
        label="governança técnica pública",
        description="Evita expor runtime, patch, branch, PR, deploy, autoevolução e fluxos internos.",
        triggers=(
            "autoevolucao", "autoevolução", "readonly", "read only", "branch", "pull request",
            "pr", "deploy", "patch", "runtime", "pipeline", "write_executed", "branch_created",
        ),
        priority=3,
        synthesis_role="block_technical_governance",
    ))

    # Journey hooks: superfície pública normal.
    register_hook(HookSpec(
        hook_id="journey.institutional",
        family="journey",
        label="institucional Patroai/Orkio",
        description="Explica Patroai, Orkio e, somente quando solicitado, a relação com AMCHAM RS.",
        triggers=("patroai", "patroaí", "patroai consultech", "o que e a patroai", "o que é a patroai", "orkio", "testar o orkio", "amcham", "amcham rs", "associados amcham"),
        priority=20,
        synthesis_role="answer_public_institutional",
    ))
    register_hook(HookSpec(
        hook_id="journey.platform_exploration",
        family="journey",
        label="exploração guiada",
        description="Ajuda usuários que não sabem por onde começar.",
        triggers=("nao sei", "não sei", "me conduza", "por onde comeco", "por onde começo", "como testar", "explorar plataforma"),
        priority=21,
        synthesis_role="discover_intent",
    ))
    register_hook(HookSpec(
        hook_id="journey.professional_development",
        family="journey",
        label="desenvolvimento profissional",
        description="Conduz objetivos de evolução profissional, carreira e posicionamento.",
        triggers=("me desenvolver", "desenvolvimento profissional", "carreira", "crescer profissionalmente", "evoluir profissionalmente"),
        priority=30,
        synthesis_role="career_discovery",
    ))
    register_hook(HookSpec(
        hook_id="journey.skills_mapping",
        family="journey",
        label="mapeamento de skills",
        description="Ajuda a mapear competências, lacunas e próximos passos.",
        triggers=("skills", "habilidades", "competencias", "competências", "mapear meus skills", "mapear habilidades", "soft skills", "hard skills"),
        priority=31,
        synthesis_role="skills_discovery",
    ))
    register_hook(HookSpec(
        hook_id="journey.networking",
        family="journey",
        label="networking",
        description="Ajuda a fortalecer conexões, posicionamento e proposta de valor pessoal.",
        triggers=("networking", "rede de contatos", "conexoes", "conexões", "me conectar", "relacionamento", "comunidade"),
        priority=32,
        synthesis_role="networking_discovery",
    ))
    register_hook(HookSpec(
        hook_id="journey.leadership",
        family="journey",
        label="liderança e comunicação",
        description="Conduz evolução em liderança, comunicação e influência.",
        triggers=("lideranca", "liderança", "liderar", "comunicacao", "comunicação", "influencia", "influência"),
        priority=33,
        synthesis_role="leadership_discovery",
    ))
    register_hook(HookSpec(
        hook_id="journey.internal_innovation",
        family="journey",
        label="inovação interna",
        description="Ajuda a desenhar projetos de inovação dentro de empresas.",
        triggers=("inovacao", "inovação", "dentro da minha empresa", "na minha empresa", "projeto interno", "melhorar processo"),
        priority=34,
        synthesis_role="innovation_discovery",
    ))
    register_hook(HookSpec(
        hook_id="journey.ai_project",
        family="journey",
        label="projeto de IA",
        description="Ajuda a estruturar ideias de IA no trabalho ou na empresa.",
        triggers=("projeto de ia", "inteligencia artificial", "inteligência artificial", "automacao com ia", "automação com ia", "usar ia"),
        priority=35,
        synthesis_role="ai_project_discovery",
    ))
    register_hook(HookSpec(
        hook_id="journey.entrepreneurship",
        family="journey",
        label="empreendedorismo",
        description="Conduz criação de novo negócio sem oferecer agentes cedo demais.",
        triggers=("novo negocio", "novo negócio", "empreender", "abrir empresa", "criar empresa", "startup", "ideia de negocio", "ideia de negócio"),
        priority=36,
        synthesis_role="business_discovery",
    ))
    register_hook(HookSpec(
        hook_id="journey.business_diagnostic",
        family="journey",
        label="diagnóstico de negócio ou projeto",
        description="Ajuda a organizar problema, risco, oportunidade e próximos passos.",
        triggers=("diagnostico", "diagnóstico", "avaliar meu negocio", "avaliar meu negócio", "revisar um problema", "plano de acao", "plano de ação"),
        priority=37,
        synthesis_role="diagnostic_discovery",
    ))

    # Specialist hooks: inteligência invisível. Nunca são speaker público.
    register_hook(HookSpec(
        hook_id="specialist.financial_strategy",
        family="specialist",
        label="estratégia financeira interna",
        description="Sinal financeiro interno para apoiar síntese do Orkio quando necessário.",
        triggers=("financeiro", "financas", "finanças", "receita", "custos", "margem", "viabilidade", "valuation", "captação", "captacao"),
        priority=70,
        public_safe=False,
        internal_only=True,
        synthesis_role="internal_financial_signal",
    ))
    register_hook(HookSpec(
        hook_id="specialist.technical_architecture",
        family="specialist",
        label="arquitetura técnica interna",
        description="Sinal técnico interno para apoiar síntese do Orkio quando necessário.",
        triggers=("arquitetura", "backend", "frontend", "api", "plataforma", "sistema", "deploy", "pwa", "realtime"),
        priority=71,
        public_safe=False,
        internal_only=True,
        synthesis_role="internal_technical_signal",
    ))
    register_hook(HookSpec(
        hook_id="specialist.governance_audit",
        family="specialist",
        label="governança interna",
        description="Sinal interno de governança para auditoria e controle de risco.",
        triggers=("governanca", "governança", "auditoria", "risco", "compliance", "seguranca", "segurança"),
        priority=72,
        public_safe=False,
        internal_only=True,
        synthesis_role="internal_governance_signal",
    ))
    register_hook(HookSpec(
        hook_id="specialist.execution_planning",
        family="specialist",
        label="planejamento de execução interno",
        description="Sinal interno para organizar roadmap, execução e próximos passos.",
        triggers=("execucao", "execução", "roadmap", "cronograma", "prioridade", "proximos passos", "próximos passos"),
        priority=73,
        public_safe=False,
        internal_only=True,
        synthesis_role="internal_execution_signal",
    ))


_seed_hooks()
