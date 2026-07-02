"""
EO-05 — Executive Decision Engine.

Classificador simples e determinístico de intenção.
Pode ser usado antes do provider para orientar resposta.
"""

from typing import Dict, List


_INTENT_KEYWORDS = {
    "quantitative": ["calcule", "margem", "lucro", "gap", "faturamento", "custo", "%", "r$"],
    "governance": ["proposal_only", "observe_only", "aprovação humana", "rollback", "risco", "validação"],
    "platform_capability": ["o que a plataforma faz", "capacidade", "faz hoje", "roadmap", "produção", "beta"],
    "technical": ["backend", "frontend", "api", "stream", "sse", "deploy", "runtime", "logs"],
    "commercial": ["cliente", "plano", "preço", "venda", "empresarial", "contratar"],
    "strategy": ["estratégia", "crescer", "mercado", "go to market", "posicionamento"],
}


def classify_intent(message: str) -> Dict[str, object]:
    text = (message or "").lower()
    scores: Dict[str, int] = {}
    matched: Dict[str, List[str]] = {}
    for intent, keys in _INTENT_KEYWORDS.items():
        hits = [k for k in keys if k in text]
        if hits:
            scores[intent] = len(hits)
            matched[intent] = hits
    if not scores:
        return {"intent": "general", "confidence": 0.3, "matched": []}
    intent = max(scores, key=scores.get)
    confidence = min(0.95, 0.45 + 0.12 * scores[intent])
    return {"intent": intent, "confidence": confidence, "matched": matched[intent]}
