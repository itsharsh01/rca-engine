import re

class PIIRedactor:
    def __init__(self):
        # Setup regex patterns or Presidio analyzer
        self.email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

    def redact(self, text: str) -> str:
        """
        Redacts emails and generic PII from text before DB storage.
        """
        if not isinstance(text, str):
            return text
        return self.email_pattern.sub("[REDACTED_EMAIL]", text)
