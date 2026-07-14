from enum import Enum

class FaultClass(str, Enum):
    LATENCY_SPIKE = "latency_spike"
    LLM_API_ERROR = "llm_api_error"
    TOKEN_LIMIT_EXCEEDED = "token_limit_exceeded"
    PII_LEAKAGE = "pii_leakage"
    PROMPT_INJECTION = "prompt_injection"
    UNEXPECTED_OUTPUT = "unexpected_output"
