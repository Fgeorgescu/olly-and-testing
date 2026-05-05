from prometheus_client import Counter

item_events = Counter(
    "item_events_total",
    "Total item lifecycle events",
    ["event", "actor"],
)
