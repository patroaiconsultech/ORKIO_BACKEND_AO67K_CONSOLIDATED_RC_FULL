from .models import Classification

def classify_message(message: str) -> Classification:
    text = (message or "").lower()
    quantitative_terms = ["fatura", "custos", "margem", "lucro", "gap", "percentual", "calcule"]
    governance_terms = ["observe_only", "proposal_only", "rollback", "aprovação humana", "não execute", "riscos"]
    capability_terms = ["o que é", "capacidades", "oferece hoje", "roadmap", "produção", "beta", "proposta"]
    code_terms = ["alterar código", "abrir pr", "deploy", "pull request", "commit"]

    if any(t in text for t in quantitative_terms):
        return Classification("quantitative_business_math", 0.96, [t for t in quantitative_terms if t in text])
    if any(t in text for t in governance_terms):
        return Classification("governance_proposal_only", 0.95, [t for t in governance_terms if t in text])
    if any(t in text for t in code_terms):
        return Classification("autoevolution_capability_boundary", 0.94, [t for t in code_terms if t in text])
    if any(t in text for t in capability_terms):
        return Classification("platform_capability_question", 0.90, [t for t in capability_terms if t in text])
    return Classification("general_executive", 0.70, [])
