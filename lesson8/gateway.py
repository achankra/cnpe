# lesson8/ingress-demo/gateway.py

import random
import time
from typing import Dict, Any, Optional
import yaml

from policy import validate_config

#CONFIG_FILE = "config.yaml"

def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def print_banner(cfg: Dict[str, Any]) -> None:
    service = cfg["service"]
    host = cfg["host"]
    strategy = cfg["traffic"]["strategy"]

    print("==============================================")
    print("Lesson 8.5 Demo: Secure Ingress + Traffic Control")
    print("==============================================")
    print(f"Service:   {service}")
    print(f"Ingress:   https://{host}  (TLS enforced by platform)")
    print(f"Strategy:  {strategy}")
    if strategy == "canary":
        print(f"Canary %:  {cfg['traffic']['canary_percentage']}% (v2)")
    if strategy == "bluegreen":
        print(f"Active:    {cfg['traffic']['active_color']}")
    print("")

def secure_ingress_check(host: str, tls: bool) -> None:
    """
    This is a simulation of 'secure ingress'. In real life:
    - TLS termination (cert-manager)
    - host routing (ingress / gateway API)
    - WAF / rate limiting / authz at edge
    """
    if not tls:
        raise RuntimeError("SECURITY VIOLATION: TLS is required but disabled.")
    if not host.endswith(".platform.local"):
        raise RuntimeError("SECURITY VIOLATION: host is outside platform-owned DNS zone.")

def route_request(cfg: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> str:
    """
    Traffic control simulation:
    - canary: percentage routing to v2, with header override
    - bluegreen: all traffic to active color, with header override
    """
    headers = headers or {}
    traffic = cfg["traffic"]
    service = cfg["service"]
    strategy = traffic["strategy"]

    # Optional "secure override" headers for demos
    if strategy == "canary":
        # Header-based override: force canary for a single request
        if headers.get("X-Canary") == "true":
            return f"{service}-v2"
        pct = int(traffic["canary_percentage"])
        return f"{service}-v2" if random.randint(1, 100) <= pct else f"{service}-v1"

    if strategy == "bluegreen":
        # Optional header override to test inactive safely
        if traffic.get("allow_header_override", True):
            forced = headers.get("X-Force-Color")
            if forced in ("blue", "green"):
                return f"{service}-{forced}"
        active = traffic["active_color"]
        return f"{service}-{active}"

    # Fallback (should never hit due to policy validation)
    return f"{service}-v1"

def demo_before_after(cfg: Dict[str, Any]) -> None:
    """
    Make the concept extremely visible:
    BEFORE: no traffic control (everything -> v1)
    AFTER:  platform traffic control (canary OR blue/green)
    """
    service = cfg["service"]

    print("=== BEFORE (no platform traffic control) ===")
    for i in range(5):
        print(f"Request {i+1:02d} → routed to {service}-v1")
    print("")

    print("=== AFTER (platform-managed traffic control) ===")
    for i in range(12):
        backend = route_request(cfg)
        print(f"Request {i+1:02d} → routed to {backend}")
    print("")

    # A single "safe test" request using headers (very teachable)
    print("=== SAFE TEST (header override) ===")
    if cfg["traffic"]["strategy"] == "canary":
        print("Request → routed to", route_request(cfg, {"X-Canary": "true"}), "(forced canary via X-Canary: true)")
    else:
        inactive = "green" if cfg["traffic"]["active_color"] == "blue" else "blue"
        print("Request → routed to", route_request(cfg, {"X-Force-Color": inactive}), f"(forced {inactive} via X-Force-Color)")
    print("")

