from mcp_servers.auditor_readonly.sanitizers import (
    hash_identifier,
    runtime_value_for_public_flag,
    sanitize_filename,
    sanitize_mapping,
    sanitize_text,
)


def test_sanitize_text_redacts_email_tokens_cookie_password_and_jwt():
    raw = (
        "user chrisaires07@gmail.com "
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456 "
        "cookie=sessionid=secret-cookie-value "
        "password=example-secret-phrase "
        "token=super-secret-token "
        "jwt eyJabcde12345.eyJpayload67890.signature12345"
    )

    sanitized = sanitize_text(raw)

    assert "chrisaires07@gmail.com" not in sanitized
    assert "abcdefghijklmnopqrstuvwxyz123456" not in sanitized
    assert "secret-cookie-value" not in sanitized
    assert "example-secret-phrase" not in sanitized
    assert "super-secret-token" not in sanitized
    assert "eyJabcde12345" not in sanitized
    assert "email:" in sanitized
    assert "[redacted]" in sanitized


def test_sanitize_text_redacts_secret_query_params():
    raw = "https://example.test/callback?token=abc123&safe=value&password=secret"

    sanitized = sanitize_text(raw)

    assert "token=abc123" not in sanitized
    assert "password=secret" not in sanitized
    assert "safe=value" in sanitized


def test_hash_identifier_is_stable_and_not_raw():
    first = hash_identifier("thread-123")
    second = hash_identifier("thread-123")

    assert first == second
    assert first != "thread-123"
    assert first.startswith("sha256:")


def test_sanitize_filename_keeps_extension_and_hashes_stem():
    result = sanitize_filename("Projeto AmCham Confidencial.pdf")

    assert result["extension"] == ".pdf"
    assert result["filename_ref"].startswith("sha256:")
    assert "Projeto" not in result["filename_ref"]


def test_sanitize_mapping_redacts_content_like_fields():
    result = sanitize_mapping(
        {
            "content": "texto integral do documento",
            "safe": "ok",
            "nested": {"token": "abc", "count": 2},
        }
    )

    assert result["content"] == "[redacted]"
    assert result["safe"] == "ok"
    assert result["nested"]["token"] == "[redacted]"
    assert result["nested"]["count"] == 2


def test_runtime_value_for_public_flag_redacts_sensitive_names():
    assert runtime_value_for_public_flag("OPENAI_API_KEY", "secret", ("OPENAI_API_KEY",)) == "[redacted]"
    assert runtime_value_for_public_flag("FEATURE_CHAT_ENABLED", "true", ("FEATURE_CHAT_ENABLED",)) == "true"
    assert runtime_value_for_public_flag("FEATURE_COMPLEX", "non_boolean_value", ("FEATURE_COMPLEX",)) == "set"
