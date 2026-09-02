"""Auditable health rules for a heterogeneous robot fleet."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import fmean
from typing import Iterable


@dataclass(frozen=True, slots=True)
class FleetSample:
    robot_id: str
    timestamp: str
    battery_pct: float
    localization_quality: float
    cpu_pct: float
    latency_ms: float
    mission_active: bool


def score_sample(sample: FleetSample) -> dict[str, object]:
    alerts: list[dict[str, str]] = []
    penalty = 0.0

    if sample.battery_pct < 20:
        penalty += 25
        alerts.append({"code": "battery_low", "severity": "warning"})
    if sample.localization_quality < 0.7:
        penalty += 35
        alerts.append({"code": "localization_degraded", "severity": "critical"})
    if sample.cpu_pct > 90:
        penalty += 20
        alerts.append({"code": "cpu_saturated", "severity": "warning"})
    if sample.latency_ms > 150:
        penalty += 30
        alerts.append({"code": "control_latency_high", "severity": "critical"})

    score = max(0.0, 100.0 - penalty)
    status = "critical" if any(alert["severity"] == "critical" for alert in alerts) else "warning" if alerts else "healthy"
    return {"sample": asdict(sample), "score": score, "status": status, "alerts": alerts}


def summarize_fleet(samples: Iterable[FleetSample]) -> dict[str, object]:
    results = [score_sample(sample) for sample in samples]
    status_counts = {"healthy": 0, "warning": 0, "critical": 0}
    for result in results:
        status_counts[str(result["status"])] += 1
    scores = [float(result["score"]) for result in results]
    return {
        "summary": {
            "robots": len(results),
            "average_health_score": round(fmean(scores), 2) if scores else 0.0,
            "status_counts": status_counts,
            "active_missions": sum(bool(result["sample"]["mission_active"]) for result in results),
        },
        "robots": results,
    }
