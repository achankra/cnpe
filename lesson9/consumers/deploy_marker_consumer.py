from schemas import PlatformEvent

def deploy_marker_consumer(event: PlatformEvent) -> None:
    if event.type not in ("deployment.completed", "deployment.failed"):
        return
    print("\n OBSERVABILITY CONSUMER")
    print(f"- Emitting deploy marker: service={event.service} env={event.environment} version={event.version}")
