from __future__ import annotations
import re
from dataclasses import dataclass
from .models import ConversationMessage, DistilledItem

@dataclass(frozen=True)
class ClassificationRule:
    bucket: str
    item_type: str
    keywords: tuple[str, ...]
    confidence: float = 0.75

DEFAULT_RULES: tuple[ClassificationRule, ...] = (
    ClassificationRule("decisions", "decision", ("decidimos", "decisão", "decisao", "fica decidido", "aprovado"), 0.86),
    ClassificationRule("actions", "action", ("vamos", "criar", "corrigir", "implementar", "executar", "rodar", "testar", "aplicar"), 0.78),
    ClassificationRule("bugs", "bug", ("erro", "bug", "falha", "quebrou", "traceback", "exception", "crash", "regressão", "regressao"), 0.82),
    ClassificationRule("improvements", "improvement", ("melhoria", "otimizar", "evoluir", "aprimorar", "refatorar"), 0.74),
    ClassificationRule("ideas", "idea", ("ideia", "sugestão", "sugestao", "poderíamos", "poderiamos", "que tal"), 0.70),
    ClassificationRule("lessons", "lesson", ("aprendemos", "lição", "licao", "aprendizado", "lesson"), 0.76),
    ClassificationRule("risks", "risk", ("risco", "perigo", "atenção", "atencao", "cuidado", "vazamento", "bloqueio"), 0.80),
)

class RuleBasedConversationClassifier:
    def __init__(self, rules: tuple[ClassificationRule, ...] = DEFAULT_RULES) -> None:
        self._rules = rules

    def classify_message(self, message: ConversationMessage) -> dict[str, list[DistilledItem]]:
        text = message.normalized_content()
        lowered = text.lower()
        buckets: dict[str, list[DistilledItem]] = {k: [] for k in ("decisions","actions","bugs","improvements","ideas","lessons","risks")}
        for rule in self._rules:
            matched = [k for k in rule.keywords if self._contains_keyword(lowered, k)]
            if matched:
                buckets[rule.bucket].append(DistilledItem(rule.item_type, text, rule.confidence, message.message_id, {"matched_keywords": matched}))
        return buckets

    @staticmethod
    def _contains_keyword(text: str, keyword: str) -> bool:
        return re.search(rf"(?<!\w){re.escape(keyword.lower())}(?!\w)", text) is not None
