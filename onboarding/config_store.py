import os
import json
from typing import Dict, Any

CONFIG_FILE_PATH = "mercury_config.json"

def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_FILE_PATH):
        return {}
    with open(CONFIG_FILE_PATH, "r") as f:
        return json.load(f)

def save_config(config_data: Dict[str, Any]) -> None:
    with open(CONFIG_FILE_PATH, "w") as f:
        json.dump(config_data, f, indent=2)
