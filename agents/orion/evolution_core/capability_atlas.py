from __future__ import annotations

from typing import Dict, Tuple

from .models import CapabilityRecord


OEC001_CAPABILITIES: Tuple[CapabilityRecord, ...] = (
    CapabilityRecord(
        capability_id="orion.identity",
        name="Orion Technical Identity",
        owner="orion",
        status="foundation",
        maturity=70,
        business_value="estabelece missão, limites e formato operacional único",
        evidence=(
            "agents/orion/profile.py",
            "agents/orion/hooks.py",
            "arcangelic/prompts_cto_squad/orion_cto.txt",
        ),
        next_step="ligar identidade ao runtime de resposta e ao painel administrativo",
    ),
    CapabilityRecord(
        capability_id="evolution.proposal_governance",
        name="Governed Evolution Proposal Flow",
        owner="orion",
        status="active_partial",
        maturity=75,
        business_value="transforma oportunidades em propostas com aprovação humana",
        dependencies=("mutation.authority",),
        evidence=(
            "routes/internal/evolution_internal.py",
            "self_heal/governance.py",
            "evolution/governed_evolution/",
        ),
        next_step="unificar approval_id, TTL e escopo de ação",
    ),
    CapabilityRecord(
        capability_id="mutation.authority",
        name="Mutation Authority",
        owner="orion",
        status="foundation",
        maturity=55,
        business_value="centraliza autorização de branch, patch, commit, PR, merge e deploy",
        evidence=("evolution_os/governance/mutation_authority.py",),
        next_step="homologar create_branch, write_file, create_commit e open_pr",
    ),
    CapabilityRecord(
        capability_id="evolution.capability_atlas",
        name="Capability Atlas",
        owner="orion",
        status="foundation",
        maturity=25,
        business_value="permite que a ORKIO conheça capacidades, dependências e maturidade",
        dependencies=("orion.identity",),
        evidence=("agents/orion/evolution_core/capability_atlas.py",),
        next_step="migrar registros para persistência e expor API read-only",
    ),
    CapabilityRecord(
        capability_id="evolution.master_plan",
        name="Master Evolution Plan",
        owner="orion",
        status="foundation",
        maturity=20,
        business_value="alinha propostas com prioridades, dependências e critérios de aceite",
        dependencies=("evolution.capability_atlas",),
        evidence=("agents/orion/evolution_core/master_plan.py",),
        next_step="criar entidade persistente e painel de acompanhamento",
    ),
)


def build_capability_atlas() -> Dict[str, object]:
    items = [item.to_dict() for item in OEC001_CAPABILITIES]
    return {
        "version": "OEC-001_CAPABILITY_ATLAS_V1",
        "mode": "read_only",
        "count": len(items),
        "items": items,
    }
