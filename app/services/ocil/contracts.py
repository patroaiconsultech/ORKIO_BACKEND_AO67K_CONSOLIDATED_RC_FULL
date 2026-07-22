from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class ArchitectureContract:
    initiative: str = "ORKIO_CORE_INTELLIGENCE_LAYER"
    version: str = "PREMIUM_3_FOUNDATION"
    architecture_type: str = "shared_platform_infrastructure"
    first_functional_pillar: str = "ATTACHMENT_INTELLIGENCE"
    foundation_capability: str = "EXECUTION_INTELLIGENCE"
    governance_owner: str = "platform"
    orion_role: str = "orchestrator_and_consumer"
    chris_role: str = "strategic_context_only"
    main_py_role: str = "bootstrap_only"
    proposal_only: bool = True
    human_approval_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AttachmentResolutionContract:
    message_id: str
    thread_id: str
    current_attachment_ids: List[str] = field(default_factory=list)
    historical_attachment_ids: List[str] = field(default_factory=list)
    explicit_historical_context_requested: bool = False
    selection_reason: str = "no_attachment"
    context_isolated: bool = True
    cache_invalidated: bool = False
    evidence_required: bool = False
    resolver_version: str = "OCIL_ATTACHMENT_RESOLVER_V1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExecutionProfileContract:
    requested_agent: str
    selected_agent: str
    execution_profile: str
    required_capabilities: List[str] = field(default_factory=list)
    document_grounding_required: bool = False
    vision_required: bool = False
    lite_allowed: bool = True
    fallback_allowed: bool = True
    selection_reason: str = "default_standard"
    policy_version: str = "OCIL_EXECUTION_POLICY_V1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentAuthorityContract:
    agent: str
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    allowed_capabilities: List[str] = field(default_factory=list)
    can_create_technical_proposal: bool = False
    can_issue_technical_go_no_go: bool = False
    can_write_repository: bool = False
    can_use_network: bool = False
    can_call_agents_directly: bool = False
    authority_version: str = "OCIL_AGENT_AUTHORITY_V1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
