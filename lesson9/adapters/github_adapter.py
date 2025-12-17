import json
from schemas import PlatformEvent

def adapt_github_event(json_path: str) -> PlatformEvent:
    raw = json.loads(open(json_path, "r", encoding="utf-8").read())

    # Minimal mapping for demo purposes
    status = raw["deployment"]["status"]          # "success" | "failure"
    evt_type = "deployment.completed" if status == "success" else "deployment.failed"

    return PlatformEvent(
        type=evt_type,
        source="github",
        service=raw["deployment"]["service"],
        environment=raw["deployment"]["environment"],
        version=raw["deployment"]["version"],
        correlation_id=raw["deployment"]["id"],
        payload={
            "commit": raw["deployment"].get("commit"),
            "actor": raw["deployment"].get("actor"),
            "run_url": raw["deployment"].get("run_url"),
            "reason": raw["deployment"].get("reason", ""),
        },
    )
