import re

class PIIRedactor:
    def __init__(self):
        # Setup regex patterns for email/phone PII
        self.email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

    def redact(self, text: str) -> str:
        """
        Redacts emails and PII from text before DB storage.
        """
        if not isinstance(text, str):
            return text
        return self.email_pattern.sub("[REDACTED_EMAIL]", text)

    def redact_dict(self, data: dict) -> dict:
        """
        Recursively redacts PII strings inside dictionaries or nested structures.
        """
        if not isinstance(data, dict):
            return data
        
        redacted = {}
        for key, val in data.items():
            if isinstance(val, str):
                redacted[key] = self.redact(val)
            elif isinstance(val, dict):
                redacted[key] = self.redact_dict(val)
            elif isinstance(val, list):
                redacted[key] = [self.redact(v) if isinstance(v, str) else v for v in val]
            else:
                redacted[key] = val
        return redacted
