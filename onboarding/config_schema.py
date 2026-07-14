from pydantic import BaseModel
from typing import Dict, Any, Optional

class PlatformCredentials(BaseModel):
    platform_name: str
    api_key: str
    base_url: Optional[str] = None

class AppConfig(BaseModel):
    project_name: str
    app_version: str
    debug: bool = False
    credentials: Dict[str, PlatformCredentials] = {}
