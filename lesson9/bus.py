from typing import Callable, Dict, List
from schemas import PlatformEvent

Handler = Callable[[PlatformEvent], None]

# in-memory event bus

class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[str, List[Handler]] = {}

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._subs.setdefault(event_type, []).append(handler)

    def publish(self, event: PlatformEvent) -> None:
        # exact match + wildcard "*" for “all events”
        for h in self._subs.get(event.type, []):
            h(event)
        for h in self._subs.get("*", []):
            h(event)
