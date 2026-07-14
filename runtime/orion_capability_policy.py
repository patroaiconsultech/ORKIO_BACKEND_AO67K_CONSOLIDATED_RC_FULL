from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Iterable


def _normalize(value: str) -> str:
    raw = unicodedata.normalize("NFKD", str(value or ""))
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    raw = raw.lower()
    return re.sub(r"\s+", " ", raw).strip()


def _matches_any(text: str, patterns: Iterable[str]) -> tuple[str, ...]:
    matched: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            matched.append(pattern)
    return tuple(matched)


@dataclass(frozen=True)
class MutationConstraints:
    explicit_readonly: bool
    block_proposal: bool
    block_write: bool
    block_pr: bool
    block_merge: bool
    block_deploy: bool
    matched_markers: tuple[str, ...]

    @property
    def force_readonly(self) -> bool:
        return self.explicit_readonly or self.block_write

    @property
    def mutation_allowed(self) -> bool:
        return not self.force_readonly


_READONLY_PATTERNS = (
    r"\bread[- ]?only\b",
    r"\bsomente leitura\b",
    r"\bapenas leitura\b",
    r"\bmodo leitura\b",
    r"\bsem escrita\b",
)

_BLOCK_PROPOSAL_PATTERNS = (
    r"\bsem (?:criar |gerar |abrir )?proposta(?:s)?\b",
    r"\bnao (?:crie|gere|abra|produza) (?:uma )?proposta(?:s)?\b",
    r"\bproposta(?:s)? (?:nao|nunca) permitida(?:s)?\b",
)

_BLOCK_WRITE_PATTERNS = (
    r"\bsem escrita\b",
    r"\bnao (?:escreva|altere|modifique|aplique|edite) (?:o |a |os |as )?(?:codigo|code|arquivo|arquivos|repo|repositorio)\b",
    r"\bnenhuma escrita\b",
)

_BLOCK_PR_PATTERNS = (
    r"\bsem (?:abrir |criar |gerar )?(?:pr|pull request)\b",
    r"\bnao (?:abra|crie|gere) (?:um |uma )?(?:pr|pull request)\b",
)

_BLOCK_MERGE_PATTERNS = (
    r"\bsem merge\b",
    r"\bnao (?:faca|execute|realize) merge\b",
)

_BLOCK_DEPLOY_PATTERNS = (
    r"\bsem deploy\b",
    r"\bnao (?:faca|execute|realize|publique) (?:o )?deploy\b",
)

_TECHNICAL_ACTION_PATTERNS = (
    r"\bmapear\b",
    r"\bmapeie\b",
    r"\bmapeasse\b",
    r"\bmapeando\b",
    r"\bmapeamento\b",
    r"\bmapa\b",
    r"\bauditar\b",
    r"\baudite\b",
    r"\baudit\b",
    r"\banalisar\b",
    r"\banalise\b",
    r"\binspecionar\b",
    r"\binspecione\b",
    r"\blistar\b",
    r"\bliste\b",
    r"\bbuscar\b",
    r"\bbusque\b",
    r"\bverificar\b",
    r"\bverifique\b",
    r"\binventariar\b",
    r"\binventarie\b",
)

_TECHNICAL_SCOPE_PATTERNS = (
    r"\bcode(?:base)?\b",
    r"\bcodigo\b",
    r"\brepo(?:sitorio)?\b",
    r"\bgithub\b",
    r"\barquitetura\b",
    r"\bruntime\b",
    r"\bbackend\b",
    r"\bfrontend\b",
    r"\bmain\.py\b",
    r"\bintent_engine\.py\b",
    r"\brota(?:s)?\b",
    r"\broute(?:s)?\b",
    r"\bcapabilit(?:y|ies)\b",
    r"\bownership\b",
    r"\bsse\b",
)

_POSITIVE_MUTATION_PATTERNS = (
    r"\baplicar (?:o |um |a )?(?:patch|correcao|mudanca|alteracao)\b",
    r"\bcorrigir (?:o |a |os |as )?(?:codigo|code|arquivo|arquivos|repo|repositorio)\b",
    r"\bescrever (?:o |a |os |as )?(?:codigo|code|arquivo|arquivos)\b",
    r"\bcriar branch\b",
    r"\babrir (?:um |uma )?(?:pr|pull request)\b",
    r"\b(?:merge|deploy|commit)\b",
)

_UX_ACTION_PATTERNS = (
    r"\b(?:audite|auditar|analise|analisar|avalie|avaliar|revise|revisar|planeje|planejar|mapeie|mapear)\b",
)

_UX_SCOPE_PATTERNS = (
    r"\bux\b",
    r"\binterface\b",
    r"\bonboarding\b",
    r"\bjornada\b",
    r"\blanding(?:s)?\b",
    r"\bpwa\b",
    r"\bmobile\b",
    r"\bappconsole\b",
    r"\bapp console\b",
)

_ARCHITECTURE_MISSION_MARKERS = (
    "cef-001",
    "cef001",
    "runtime, route & ownership",
    "runtime route ownership",
    "ownership authority",
    "orion capability proof",
    "capability registry",
    "mapear o codigo",
    "mapear o code",
    "mapa do codigo",
    "architecture index",
)


def extract_mutation_constraints(text: str) -> MutationConstraints:
    normalized = _normalize(text)
    readonly = _matches_any(normalized, _READONLY_PATTERNS)
    proposal = _matches_any(normalized, _BLOCK_PROPOSAL_PATTERNS)
    write = _matches_any(normalized, _BLOCK_WRITE_PATTERNS)
    pr = _matches_any(normalized, _BLOCK_PR_PATTERNS)
    merge = _matches_any(normalized, _BLOCK_MERGE_PATTERNS)
    deploy = _matches_any(normalized, _BLOCK_DEPLOY_PATTERNS)
    markers = readonly + proposal + write + pr + merge + deploy
    return MutationConstraints(
        explicit_readonly=bool(readonly),
        block_proposal=bool(proposal),
        block_write=bool(write),
        block_pr=bool(pr),
        block_merge=bool(merge),
        block_deploy=bool(deploy),
        matched_markers=markers,
    )


def is_readonly_technical_request(text: str) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return False
    has_action = bool(_matches_any(normalized, _TECHNICAL_ACTION_PATTERNS))
    has_scope = bool(_matches_any(normalized, _TECHNICAL_SCOPE_PATTERNS))
    constraints = extract_mutation_constraints(normalized)
    has_positive_mutation = bool(_matches_any(normalized, _POSITIVE_MUTATION_PATTERNS))
    return bool(has_action and has_scope and (constraints.force_readonly or not has_positive_mutation))


def should_route_explicit_agent_to_capability(text: str, target_agent: str) -> bool:
    target = _normalize(target_agent).replace("@", "").strip()
    return target == "orion" and is_readonly_technical_request(text)


def is_explicit_ux_audit_request(text: str) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return False

    if any(marker in normalized for marker in _ARCHITECTURE_MISSION_MARKERS):
        return False

    if re.search(r"\b(?:nao|sem)\b.{0,40}\b(?:ux|interface|onboarding|pwa|mobile)\b", normalized):
        return False

    action_matches = list(re.finditer("|".join(_UX_ACTION_PATTERNS), normalized, flags=re.IGNORECASE))
    scope_matches = list(re.finditer("|".join(_UX_SCOPE_PATTERNS), normalized, flags=re.IGNORECASE))
    if not action_matches or not scope_matches:
        return False

    # Require an explicit action and UX target in the same local clause. Merely
    # mentioning UX terms inside an attached report or historical context is not
    # sufficient to select AO-17.
    return any(abs(action.start() - scope.start()) <= 120 for action in action_matches for scope in scope_matches)
