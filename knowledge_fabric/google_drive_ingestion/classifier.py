from .models import KnowledgeItem, ClassificationResult

def classify_item(item: KnowledgeItem) -> ClassificationResult:
    name = item.name.lower()
    if any(x in name for x in ["pessoal", "saúde", "familia", "família"]):
        return ClassificationResult("personal", "restricted", False, True, "personal_or_sensitive")
    if any(x in name for x in ["business", "bp", "master plan", "holding"]):
        return ClassificationResult("business", "confidential", False, True, "business_strategy")
    if any(x in name for x in ["arquitetura", "backend", "frontend", "deploy", "cto"]):
        return ClassificationResult("technical", "internal", False, True, "technical_canon_candidate")
    if any(x in name for x in ["roadmap", "plano", "proposal"]):
        return ClassificationResult("roadmap", "internal", False, True, "roadmap_candidate")
    return ClassificationResult("archive", "internal", False, True, "unclassified_requires_review")
