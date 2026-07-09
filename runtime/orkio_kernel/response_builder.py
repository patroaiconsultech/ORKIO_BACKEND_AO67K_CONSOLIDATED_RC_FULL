from .models import KernelInput, KernelResult, new_turn_id
from .classifier import classify_message
from .truth_engine import truth_labels_for_category, enforce_truth_policy
from .governance import governance_flags
from .executive_reasoning import (
    build_quantitative_response,
    build_executive_strategy_response,
    build_executive_crisis_response,
    build_executive_dashboard_response,
    build_governance_response,
    build_capability_response,
    build_autoevolution_boundary_response,
)

def build_response(kernel_input: KernelInput) -> KernelResult:
    classification = classify_message(kernel_input.message)

    if classification.category == "quantitative_business_math":
        text = build_quantitative_response(kernel_input.message)
    elif classification.category == "executive_strategy_mode":
        text = build_executive_strategy_response(kernel_input.message)
    elif classification.category == "executive_crisis_mode":
        text = build_executive_crisis_response(kernel_input.message)
    elif classification.category == "executive_dashboard_mode":
        text = build_executive_dashboard_response(kernel_input.message)
    elif classification.category == "governance_proposal_only":
        text = build_governance_response()
    elif classification.category == "autoevolution_capability_boundary":
        text = build_autoevolution_boundary_response()
    elif classification.category == "platform_capability_question":
        text = build_capability_response(kernel_input.capability_registry)
    else:
        text = (
            "Entendi. Vou responder de forma executiva, separando o que é comprovado, "
            "o que depende de capacidade disponível e o que exigiria validação."
        )

    text = enforce_truth_policy(text)
    return KernelResult(
        handled=True,
        assistant_turn_id=new_turn_id(),
        response_text=text,
        classification=classification,
        truth_labels=truth_labels_for_category(classification.category),
        governance_flags=governance_flags(),
        capability_references=[],
        metadata={"kernel_version": "orkio_os_1_0_foundation"},
    )
