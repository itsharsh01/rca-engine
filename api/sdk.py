import httpx
from typing import Dict, Any

class MercuryClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1", api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(headers={"Authorization": f"Bearer {api_key}"} if api_key else {})

    def diagnose_trace(self, trace_id: str) -> Dict[str, Any]:
        """Call POST /rca/diagnose."""
        response = self.client.post(f"{self.base_url}/rca/diagnose", json={"trace_id": trace_id})
        return response.json()
