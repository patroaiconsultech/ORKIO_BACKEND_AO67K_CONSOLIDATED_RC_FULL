from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine, insert

from mcp_servers.auditor_readonly import queries
from mcp_servers.auditor_readonly.config import reload_config


def build_sqlite_schema(engine):
    metadata = MetaData()
    threads = Table(
        "threads",
        metadata,
        Column("id", String, primary_key=True),
        Column("organization_id", String),
        Column("user_id", String),
        Column("title", String),
        Column("content", String),
        Column("status", String),
        Column("created_at", DateTime),
    )
    messages = Table(
        "messages",
        metadata,
        Column("id", String, primary_key=True),
        Column("thread_id", String),
        Column("organization_id", String),
        Column("role", String),
        Column("status", String),
        Column("content", String),
        Column("created_at", DateTime),
    )
    files = Table(
        "files",
        metadata,
        Column("id", String, primary_key=True),
        Column("thread_id", String),
        Column("organization_id", String),
        Column("filename", String),
        Column("status", String),
        Column("size", Integer),
        Column("extracted_text", String),
    )
    metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(
            insert(threads),
            [
                {
                    "id": "thread-1",
                    "organization_id": "org-1",
                    "user_id": "user-1",
                    "title": "Documento Secreto",
                    "content": "mensagem integral proibida",
                    "status": "active",
                }
            ],
        )
        conn.execute(
            insert(messages),
            [
                {
                    "id": "message-1",
                    "thread_id": "thread-1",
                    "organization_id": "org-1",
                    "role": "user",
                    "status": "completed",
                    "content": "conteudo bruto da mensagem",
                },
                {
                    "id": "message-2",
                    "thread_id": "thread-1",
                    "organization_id": "org-1",
                    "role": "assistant",
                    "status": "completed",
                    "content": "conteudo bruto do assistente",
                },
            ],
        )
        conn.execute(
            insert(files),
            [
                {
                    "id": "file-1",
                    "thread_id": "thread-1",
                    "organization_id": "org-1",
                    "filename": "Contrato Confidencial.pdf",
                    "status": "indexed",
                    "size": 1234,
                    "extracted_text": "texto integral extraido do PDF",
                }
            ],
        )


def configure(monkeypatch):
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ENABLED", "true")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ALLOWED_ORG_IDS", "org-1")
    reload_config()


def test_thread_metadata_does_not_return_raw_content(monkeypatch):
    configure(monkeypatch)
    engine = create_engine("sqlite:///:memory:")
    build_sqlite_schema(engine)
    monkeypatch.setattr(queries, "get_engine", lambda: engine)

    result = queries.fetch_thread_metadata(thread_id="thread-1", org_id="org-1")

    assert result is not None
    serialized = str(result)
    assert "mensagem integral proibida" not in serialized
    assert "Documento Secreto" not in serialized
    assert "content" not in result
    assert "title" not in result
    assert "title_ref" in result


def test_message_counts_do_not_return_message_content(monkeypatch):
    configure(monkeypatch)
    engine = create_engine("sqlite:///:memory:")
    build_sqlite_schema(engine)
    monkeypatch.setattr(queries, "get_engine", lambda: engine)

    result = queries.fetch_message_counts(thread_id="thread-1", org_id="org-1")

    serialized = str(result)
    assert result["total"] == 2
    assert result["by_role"]["user"] == 1
    assert "conteudo bruto" not in serialized
    assert "content" not in result


def test_file_refs_do_not_return_filename_or_extracted_text(monkeypatch):
    configure(monkeypatch)
    engine = create_engine("sqlite:///:memory:")
    build_sqlite_schema(engine)
    monkeypatch.setattr(queries, "get_engine", lambda: engine)

    result = queries.fetch_file_refs(thread_id="thread-1", org_id="org-1")

    serialized = str(result)
    assert len(result) == 1
    assert "Contrato Confidencial" not in serialized
    assert "texto integral extraido" not in serialized
    assert "extracted_text" not in result[0]
    assert result[0]["extension"] == ".pdf"
    assert result[0]["filename_ref"].startswith("sha256:")
