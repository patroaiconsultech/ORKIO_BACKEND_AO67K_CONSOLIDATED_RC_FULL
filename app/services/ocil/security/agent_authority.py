from __future__ import annotations

from ..contracts import AgentAuthorityContract


def authority_for_agent(agent: str) -> AgentAuthorityContract:
    normalized = (agent or "orion").strip().lower()

    if normalized == "chris":
        return AgentAuthorityContract(
            agent="chris",
            allowed_domains=[
                "business_context",
                "valuation",
                "strategic_analysis",
            ],
            blocked_domains=[
                "backend_architecture",
                "runtime",
                "stream",
                "technical_governance",
                "repository_write",
            ],
            allowed_capabilities=["read_context", "strategic_analysis"],
            can_create_technical_proposal=False,
            can_issue_technical_go_no_go=False,
        )

    if normalized == "orion":
        return AgentAuthorityContract(
            agent="orion",
            allowed_domains=[
                "orchestration",
                "technical_analysis",
                "proposal_drafting",
            ],
            blocked_domains=[
                "platform_policy_override",
                "repository_write",
                "deployment",
                "credential_access",
            ],
            allowed_capabilities=[
                "read_context",
                "orchestrate",
                "draft_proposal",
            ],
            can_create_technical_proposal=True,
            can_issue_technical_go_no_go=True,
        )

    return AgentAuthorityContract(
        agent=normalized,
        allowed_domains=["assigned_specialty"],
        blocked_domains=[
            "platform_policy_override",
            "repository_write",
            "deployment",
            "credential_access",
        ],
        allowed_capabilities=["read_context"],
        can_create_technical_proposal=False,
        can_issue_technical_go_no_go=False,
    )
