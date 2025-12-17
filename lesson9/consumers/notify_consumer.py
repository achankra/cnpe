from schemas import PlatformEvent

def notify_consumer(event: PlatformEvent) -> None:
    print("\n NOTIFY CONSUMER")
    print(f"- [{event.type}] {event.service} {event.version} → {event.environment} (source={event.source})")
