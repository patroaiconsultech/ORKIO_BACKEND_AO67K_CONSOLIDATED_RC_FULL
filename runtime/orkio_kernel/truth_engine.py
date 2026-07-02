from typing import List

def truth_labels_for_category(category: str) -> List[str]:
    if category == "quantitative_business_math":
        return ["user_provided_numbers", "calculated_result"]
    if category == "governance_proposal_only":
        return ["declared_request", "proposal_only", "requires_human_approval"]
    if category == "autoevolution_capability_boundary":
        return ["capability_declared", "runtime_availability_unverified", "human_approval_required"]
    if category == "platform_capability_question":
        return ["capability_registry", "status_separation_required"]
    return ["general_response", "uncertainty_allowed"]

def enforce_truth_policy(text: str) -> str:
    forbidden = [
        "deploy automático sem aprovação",
        "roadmap disponível em produção",
    ]
    lowered = text.lower()
    for phrase in forbidden:
        if phrase in lowered:
            raise ValueError(f"Truth policy violation: {phrase}")
    return text
