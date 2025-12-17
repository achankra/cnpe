# lesson8/ingress-demo/policy.py

from typing import Dict, Any, List

ALLOWED_HOST_SUFFIX = ".platform.local"
ALLOWED_ENVS = {"dev", "staging", "prod"}
ALLOWED_STRATEGIES = {"canary", "bluegreen"}

def validate_config(cfg: Dict[str, Any]) -> List[str]:
    """
    Platform guardrails (intentionally simple):
    - TLS must be enabled
    - Host must be under *.platform.local
    - Traffic strategy must be canary or bluegreen
    - Canary % must be 1..99
    - Blue/Green active_color must be blue/green
    """
    errors: List[str] = []

    # Basic schema-ish checks
    for required_key in ("service", "host", "security", "traffic"):
        if required_key not in cfg:
            errors.append(f"missing required key: {required_key}")

    if errors:
        return errors

    # Security guardrail: TLS is mandatory
    tls_enabled = bool(cfg.get("security", {}).get("tls"))
    if not tls_enabled:
        errors.append("TLS must be enabled (security.tls: true)")

    # Host guardrail: platform-owned DNS space
    host = str(cfg.get("host", ""))
    if not host.endswith(ALLOWED_HOST_SUFFIX):
        errors.append(f"Host must be under *{ALLOWED_HOST_SUFFIX} (got: {host})")

    # Traffic strategy guardrails
    traffic = cfg.get("traffic", {})
    strategy = traffic.get("strategy")
    if strategy not in ALLOWED_STRATEGIES:
        errors.append(f"traffic.strategy must be one of {sorted(ALLOWED_STRATEGIES)} (got: {strategy})")
        return errors

    if strategy == "canary":
        pct = traffic.get("canary_percentage", None)
        if pct is None:
            errors.append("canary strategy requires traffic.canary_percentage")
        else:
            try:
                pct_i = int(pct)
                if pct_i < 1 or pct_i > 99:
                    errors.append("canary_percentage must be between 1 and 99")
            except ValueError:
                errors.append("canary_percentage must be an integer")

    if strategy == "bluegreen":
        active = traffic.get("active_color")
        if active not in ("blue", "green"):
            errors.append("bluegreen strategy requires traffic.active_color: 'blue' or 'green'")

    # Optional: env sanity check if present
    env = cfg.get("env")
    if env is not None and env not in ALLOWED_ENVS:
        errors.append(f"env must be one of {sorted(ALLOWED_ENVS)} (got: {env})")

    return errors
