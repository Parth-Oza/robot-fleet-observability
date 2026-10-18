"""Prometheus text exposition for a robot fleet snapshot."""

from __future__ import annotations

import math
from collections.abc import Iterable

from .health import FleetSample


_METRIC_HEADERS = (
    (
        "robot_fleet_robot_available",
        "Whether the robot is available for work (1 available, 0 unavailable).",
        "gauge",
    ),
    (
        "robot_fleet_mission_latency_seconds",
        "Latest end-to-end mission latency in seconds.",
        "gauge",
    ),
    (
        "robot_fleet_faults_total",
        "Cumulative faults reported by the robot.",
        "counter",
    ),
    (
        "robot_fleet_safety_stops_total",
        "Cumulative safety stops reported by the robot.",
        "counter",
    ),
)


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def _validate_sample(sample: FleetSample) -> None:
    if not sample.robot_id:
        raise ValueError("robot_id must not be empty")
    if not isinstance(sample.available, bool):
        raise ValueError("available must be a boolean")
    if not math.isfinite(sample.mission_latency_ms) or sample.mission_latency_ms < 0:
        raise ValueError("mission_latency_ms must be finite and non-negative")
    for field_name in ("fault_count", "safety_stop_count"):
        value = getattr(sample, field_name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{field_name} must be a non-negative integer")


def render_prometheus(samples: Iterable[FleetSample]) -> str:
    """Render a deterministic Prometheus 0.0.4 snapshot for *samples*."""

    ordered_samples = sorted(samples, key=lambda sample: sample.robot_id)
    for sample in ordered_samples:
        _validate_sample(sample)

    lines: list[str] = []
    for metric_name, help_text, metric_type in _METRIC_HEADERS:
        lines.extend((f"# HELP {metric_name} {help_text}", f"# TYPE {metric_name} {metric_type}"))
        for sample in ordered_samples:
            label = f'robot_id="{_escape_label(sample.robot_id)}"'
            if metric_name == "robot_fleet_robot_available":
                value: int | float = int(sample.available)
            elif metric_name == "robot_fleet_mission_latency_seconds":
                value = sample.mission_latency_ms / 1000.0
            elif metric_name == "robot_fleet_faults_total":
                value = sample.fault_count
            else:
                value = sample.safety_stop_count
            lines.append(f"{metric_name}{{{label}}} {value:g}")

    return "\n".join(lines) + "\n"
