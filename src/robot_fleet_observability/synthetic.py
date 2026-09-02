"""Clearly synthetic fleet snapshots for demos and tests."""

from .health import FleetSample


def sample_fleet() -> list[FleetSample]:
    timestamp = "2026-01-01T12:00:00Z"
    return [
        FleetSample("robot-01", timestamp, 87, 0.96, 42, 38, True),
        FleetSample("robot-02", timestamp, 18, 0.91, 64, 55, False),
        FleetSample("robot-03", timestamp, 66, 0.58, 93, 182, True),
    ]
