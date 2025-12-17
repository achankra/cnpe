from dataclasses import dataclass
from typing import Dict, Any

# platform event schema

@dataclass
class PlatformEvent:
    type: str                 # e.g., "deployment.completed", "deployment.failed"
    source: str               # e.g., "github"
    service: str              # e.g., "orders"
    environment: str          # e.g., "prod"
    version: str              # e.g., "1.2.3"
    correlation_id: str       # tie multiple events together
    payload: Dict[str, Any]   # flexible details (commit, actor, url, etc.)
