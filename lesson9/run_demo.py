import argparse
from bus import EventBus
from adapters.github_adapter import adapt_github_event
from consumers.issue_consumer import issue_consumer
from consumers.notify_consumer import notify_consumer
from consumers.deploy_marker_consumer import deploy_marker_consumer

def new_consumer(event):
    # demo-only: shows you can add a consumer later without touching producer/adapter
    print("\n🧩 NEW CONSUMER (added later)")
    print(f"- Doing something new with: {event.type} / {event.service}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("event_json", help="Path to sample GitHub event JSON")
    ap.add_argument("--enable", default="", help="Optional: enable 'new_consumer'")
    ap.add_argument("--fanout", action="store_true", help="Print a fan-out summary")
    args = ap.parse_args()

    print("==============================================")
    print("Lesson 9.5 Demo: Event-Driven Pipelines")
    print("Adapter → Normalized Event Stream → Consumers")
    print("==============================================\n")

    bus = EventBus()

    # Consumers subscribe to events (decoupled)
    bus.subscribe("*", notify_consumer)
    bus.subscribe("deployment.completed", deploy_marker_consumer)
    bus.subscribe("deployment.failed", deploy_marker_consumer)
    bus.subscribe("deployment.failed", issue_consumer)

    if args.enable == "new_consumer":
        bus.subscribe("*", new_consumer)

    # Adapter converts inbound GitHub event into platform schema
    evt = adapt_github_event(args.event_json)

    print("✅ ADAPTER OUTPUT (normalized event)")
    print(f"- type: {evt.type}")
    print(f"- service: {evt.service}")
    print(f"- env: {evt.environment}")
    print(f"- version: {evt.version}")
    print(f"- correlation_id: {evt.correlation_id}")

    print("\n➡️ Publishing event on bus...")
    bus.publish(evt)

    if args.fanout:
        print("\n🔁 FAN-OUT SUMMARY")
        print("- One event, multiple independent actions (notify / marker / issue).")

if __name__ == "__main__":
    main()
