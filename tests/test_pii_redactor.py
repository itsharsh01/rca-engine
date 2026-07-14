from core.pii_redactor import PIIRedactor

def test_pii_redaction():
    redactor = PIIRedactor()
    test_email = "user@example.com"
    redacted = redactor.redact(test_email)
    assert "[REDACTED_EMAIL]" in redacted
