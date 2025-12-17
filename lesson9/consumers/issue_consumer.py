from schemas import PlatformEvent

def issue_consumer(event: PlatformEvent) -> None:
    if event.type != "deployment.failed":
        return

    print("\n🧾 ISSUE CONSUMER")
    print(f"- Creating issue for {event.service} ({event.environment})")
    print(f"- Title: Deploy failed: {event.service} {event.version} → {event.environment}")
    print(f"- Correlation: {event.correlation_id}")
    print(f"- Link: {event.payload.get('run_url','(none)')}")
    print(f"- Reason: {event.payload.get('reason','')}")
