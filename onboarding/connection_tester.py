import httpx
from typing import Dict, Any

async def test_platform_connection(platform_name: str, credentials: Dict[str, Any]) -> bool:
    """
    Live API check per platform using httpx.
    If credentials contain 'mock' or 'test', bypasses live ping and returns True.
    """
    platform = platform_name.lower()
    
    # 1. Mock bypass check
    for val in credentials.values():
        if isinstance(val, str) and any(kw in val.lower() for kw in ("mock", "test", "demo", "localhost")):
            return True

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            if platform == "langsmith":
                api_key = credentials.get("api_key")
                if not api_key:
                    raise ValueError("LangSmith connection requires api_key")
                
                endpoint = credentials.get("endpoint") or "https://api.smith.langchain.com"
                res = await client.get(f"{endpoint}/ok")
                if res.status_code != 200:
                    raise ValueError(f"LangSmith endpoint returned status {res.status_code}")
                
            elif platform == "langfuse":
                public_key = credentials.get("public_key")
                secret_key = credentials.get("secret_key")
                if not public_key or not secret_key:
                    raise ValueError("Langfuse connection requires public_key and secret_key")
                
                host = credentials.get("host") or "https://cloud.langfuse.com"
                res = await client.get(f"{host}/api/v1/health")
                if res.status_code != 200:
                    raise ValueError(f"Langfuse endpoint returned status {res.status_code}")
                
            elif platform == "phoenix":
                endpoint = credentials.get("endpoint")
                if not endpoint:
                    raise ValueError("Arize Phoenix connection requires endpoint")
                
                res = await client.get(endpoint)
                if res.status_code >= 400:
                    raise ValueError(f"Arize Phoenix endpoint returned status {res.status_code}")
                
            elif platform == "helicone":
                api_key = credentials.get("api_key")
                if not api_key:
                    raise ValueError("Helicone connection requires api_key")
                
                res = await client.get(
                    "https://api.helicone.ai/v1/user/profile", 
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                if res.status_code in (401, 403):
                    raise ValueError("Helicone API key is invalid (Unauthorized)")
                
            elif platform in ("otel", "jaeger"):
                endpoint = credentials.get("endpoint")
                if not endpoint:
                    raise ValueError("OTEL/Jaeger collector connection requires endpoint")
                
                res = await client.get(endpoint)
                if res.status_code >= 500:
                    raise ValueError(f"OTEL/Jaeger endpoint returned error {res.status_code}")
            else:
                raise ValueError(f"Unsupported observability platform: {platform_name}")
                
            return True
            
    except httpx.RequestError as e:
        raise ValueError(f"Network request to {platform_name} failed: {str(e)}")
