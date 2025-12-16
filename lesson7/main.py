from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from uuid import uuid4
from datetime import datetime, timezone
import time

app = FastAPI(
    title="CNPE Platform API",
    description="Lesson 7 demo: Self-service resource provisioning via Platform API",
    version="1.0.0",
)

# --- In-memory store for demo purposes ---
JOBS: Dict[str, Dict[str, Any]] = {}

# --- Models (contract-first mindset) ---
class ProvisionRequest(BaseModel):
    team: str = Field(..., min_length=2, description="Owning team name")
    env: Literal["dev", "staging", "prod"] = Field(..., description="Target environment")
    resource_type: Literal["k8s-namespace", "s3-bucket"] = Field(..., description="Provisionable resource type")

    # 80/20: simple defaults for 80%, optional advanced knobs for 20%
    name: Optional[str] = Field(None, description="Optional name override; otherwise generated")
    advanced: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional advanced controls (e.g., annotations, quotas). Avoid exposing raw kubectl complexity.",
    )

class ProvisionResponse(BaseModel):
    request_id: str
    status: Literal["PENDING", "PROVISIONING", "READY", "FAILED"]
    resource: Optional[Dict[str, Any]] = None
    message: str
    created_at: str

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def validate_request(req: ProvisionRequest):
    # Give actionable errors (hide complexity, expose value)
    if req.env == "prod" and req.team.lower() in {"guest", "unknown"}:
        raise HTTPException(
            status_code=400,
            detail="Prod provisioning requires a valid owning team (not 'guest'/'unknown').",
        )

    if req.advanced:
        # Keep the demo guardrail-ish, without going deep into policy tooling here
        if "kubectl" in (str(req.advanced).lower()):
            raise HTTPException(
                status_code=400,
                detail="Do not pass kubectl/implementation details. Use high-level 'advanced' fields only.",
            )

def simulate_provisioning(job_id: str):
    """Fake orchestration. In real life this is where you'd call Terraform, Crossplane, or Kubernetes APIs."""
    JOBS[job_id]["status"] = "PROVISIONING"
    time.sleep(1.0)  # simulate work

    req = JOBS[job_id]["request"]
    resource_name = req.get("name") or f"{req['team']}-{req['env']}-{req['resource_type']}-{job_id[:6]}"

    # A tiny chance of failure for teaching "status + actionable error"
    if req["team"].lower() == "failme":
        JOBS[job_id]["status"] = "FAILED"
        JOBS[job_id]["message"] = "Provisioning failed: upstream quota exceeded. Try a smaller quota or contact platform-team."
        return

    JOBS[job_id]["status"] = "READY"
    JOBS[job_id]["message"] = "Provisioned successfully."

    # Return a clean “value-facing” result (not raw kubectl output)
    if req["resource_type"] == "k8s-namespace":
        JOBS[job_id]["resource"] = {
            "type": "k8s-namespace",
            "name": resource_name,
            "annotations": (req.get("advanced") or {}).get("annotations", {}),
            "next_steps": [
                "Use your CI/CD to deploy into this namespace",
                "Check status via GET /provision-requests/{request_id}",
            ],
        }
    else:
        JOBS[job_id]["resource"] = {
            "type": "s3-bucket",
            "name": resource_name,
            "encryption": "AES256",
            "public_access": "blocked",
            "next_steps": [
                "Request app credentials via your platform workflow",
                "Attach bucket policy via platform-approved template",
            ],
        }

@app.post("/provision-requests", response_model=ProvisionResponse, status_code=201)
def create_provision_request(req: ProvisionRequest):
    """
    7.5 Demo endpoint: self-service resource provisioning.

    This represents the “API-driven future”: developer -> API call -> instant feedback.
    """
    validate_request(req)

    job_id = str(uuid4())
    JOBS[job_id] = {
        "request_id": job_id,
        "status": "PENDING",
        "resource": None,
        "message": "Accepted. Provisioning will start shortly.",
        "created_at": now_iso(),
        "request": req.model_dump(),
    }

    # For simplicity in a local demo: do sync "background" simulation.
    # In a real platform API: queue + worker + async callbacks.
    simulate_provisioning(job_id)

    return ProvisionResponse(
        request_id=job_id,
        status=JOBS[job_id]["status"],
        resource=JOBS[job_id]["resource"],
        message=JOBS[job_id]["message"],
        created_at=JOBS[job_id]["created_at"],
    )

@app.get("/provision-requests/{request_id}", response_model=ProvisionResponse)
def get_provision_request(request_id: str):
    job = JOBS.get(request_id)
    if not job:
        raise HTTPException(status_code=404, detail="Request not found.")
    return ProvisionResponse(
        request_id=job["request_id"],
        status=job["status"],
        resource=job["resource"],
        message=job["message"],
        created_at=job["created_at"],
    )

@app.get("/provision-requests")
def list_provision_requests():
    return [
        {
            "request_id": j["request_id"],
            "status": j["status"],
            "created_at": j["created_at"],
            "team": j["request"]["team"],
            "env": j["request"]["env"],
            "resource_type": j["request"]["resource_type"],
        }
        for j in JOBS.values()
    ]

@app.get("/healthz")
def healthz():
    return {"ok": True}
