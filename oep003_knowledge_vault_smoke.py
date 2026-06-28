from pathlib import Path
from tempfile import TemporaryDirectory

from evolution.knowledge_vault import KnowledgeVault


def main() -> None:
    with TemporaryDirectory() as tmp:
        storage_path = Path(tmp) / "knowledge_vault.json"

        vault = KnowledgeVault(storage_path=storage_path, chunk_size=40, chunk_overlap=5)
        doc = vault.add_document(
            title="OEP-003 Knowledge Vault",
            content=(
                "O Knowledge Vault preserva conhecimento organizacional do ORKIO, "
                "indexa documentos, prepara busca semântica futura e mantém "
                "governança humana com proposal_only ativo."
            ),
            source="manual_smoke",
            scope="evolution",
            tags=["oep-003", "knowledge"],
            metadata={"marker": "OEP003_KNOWLEDGE_VAULT_BACKEND_FOUNDATION"},
        )

        results = vault.search("conhecimento organizacional ORKIO", scope="evolution")

        assert doc.document_id
        assert doc.proposal_only is True
        assert doc.write_executed is False
        assert doc.human_approval_required is True
        assert results
        assert results[0].document_id == doc.document_id

        snapshot = vault.snapshot()
        assert snapshot["proposal_only"] is True
        assert snapshot["write_executed"] is False
        assert snapshot["human_approval_required"] is True
        assert snapshot["documents"]
        assert snapshot["chunks"]

        vault.save()
        reloaded = KnowledgeVault(storage_path=storage_path)
        reloaded_results = reloaded.search("busca semântica futura")
        assert reloaded_results

    print("OEP003_KNOWLEDGE_VAULT_SMOKE_PASS")


if __name__ == "__main__":
    main()
