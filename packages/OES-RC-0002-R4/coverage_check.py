from pathlib import Path
import re

root = Path(__file__).resolve().parents[2]
pkg = Path(__file__).resolve().parent

oes = (root / "OES-005_CANONICAL_DOMAIN_MODEL.md").read_text(encoding="utf-8")
state = (pkg / "STATE_MACHINE_MATRIX.md").read_text(encoding="utf-8")
cap = (pkg / "CAPABILITY_MATRIX.md").read_text(encoding="utf-8")
der = (pkg / "DERIVATION_MATRIX.md").read_text(encoding="utf-8")

errors = []

inventory = {}
ids = {}

for match in re.finditer(r"^### (Aggregate Roots|Entities|Value Objects|References)\n(.*?)(?=^### |\Z)", oes, re.M | re.S):
    section = match.group(1)
    body = match.group(2)
    default_type = {
        "Aggregate Roots": "Aggregate Root",
        "Entities": "Entity",
        "Value Objects": "Value Object",
        "References": "Reference",
    }[section]
    for line in body.splitlines():
        if not line.startswith("| DOM-"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        dom_id = parts[0]
        concept = parts[1]
        typ = default_type
        if len(parts) >= 3 and parts[2] in {"Aggregate Root", "Entity", "Value Object", "Reference"}:
            typ = parts[2]

        if dom_id in ids and ids[dom_id] != concept:
            errors.append(f"duplicate Domain ID: {dom_id} for {ids[dom_id]} and {concept}")
        ids[dom_id] = concept

        if concept in inventory:
            errors.append(f"duplicate concept in inventory: {concept}")
        inventory[concept] = {"id": dom_id, "type": typ}

def split_concepts(raw: str):
    raw = raw.strip()
    if raw.endswith("."):
        raw = raw[:-1]
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]

for label, expected_type in [
    ("Entities", "Entity"),
    ("Value Objects", "Value Object"),
    ("References", "Reference"),
]:
    for raw in re.findall(rf"\*\*{label}:\*\*([^\n]+)", oes):
        for concept in split_concepts(raw):
            if concept.lower() == "none":
                continue
            concept = re.split(r"\s+through\s+|\s+when\s+|\s+\(", concept)[0].strip()
            if concept not in inventory:
                errors.append(f"{label} concept not in inventory: {concept}")
                continue
            if inventory[concept]["type"] != expected_type:
                errors.append(
                    f"{label} concept has wrong type: {concept} is "
                    f"{inventory[concept]['type']} expected {expected_type}"
                )

for raw in state.splitlines():
    if not raw.startswith("|") or raw.startswith("|---") or "Aggregate" in raw:
        continue
    parts = [p.strip() for p in raw.strip("|").split("|")]
    if len(parts) != 6:
        continue
    contract = parts[2]
    if contract not in cap:
        errors.append(f"missing capability coverage: {contract}")
    if contract not in der:
        errors.append(f"missing derivation coverage: {contract}")

required = [
    "SuspendOrganization", "ArchiveOrganization", "SuspendMembership",
    "ArchiveAgent", "PauseConversation", "ResumeConversation",
    "SupersedePolicy", "RevokeDelegation", "PromoteArtifactToKnowledge"
]
for item in required:
    if item not in state and item not in cap:
        errors.append(f"missing required transition/capability: {item}")

if errors:
    raise SystemExit("COVERAGE CHECK FAIL\n" + "\n".join(errors))

print("COVERAGE CHECK PASS")
