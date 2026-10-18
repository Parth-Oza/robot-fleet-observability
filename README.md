# Robot Fleet Observability

[![Tests](https://github.com/Parth-Oza/robot-fleet-observability/actions/workflows/test.yml/badge.svg)](https://github.com/Parth-Oza/robot-fleet-observability/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A dependency-free Python reference for converting robot telemetry into explainable health scores and serving the result through a small read-only API. The project focuses on the operational questions behind a fleet dashboard: Which robots need attention, why, how severe is the issue, and what is the overall fleet condition?

> Every robot, metric, threshold, and timestamp is synthetic. This independent portfolio project contains no employer code, production endpoints, facility details, or operational data.

## Capabilities

- Validated, typed telemetry records for robot health snapshots.
- Explicit thresholds for battery, localization quality, CPU, and latency.
- Explainable per-robot scores, status, and alert codes.
- Fleet-level status counts, average health, and active-mission summary.
- Threaded, read-only HTTP service with stable JSON responses.
- Prometheus 0.0.4 exporter for availability, mission latency, faults, and safety stops.
- Zero third-party runtime dependencies.

```mermaid
flowchart LR
  A[Synthetic telemetry] --> B[Typed FleetSample]
  B --> C[Auditable health rules]
  C --> D[Robot score, status, alerts]
  D --> E[Fleet aggregation]
  E --> F[GET /robots]
  B --> G[GET /metrics]
  G --> H[Prometheus and dashboards]
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
fleet-observability --port 8080
```

Query the service:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/robots
curl http://127.0.0.1:8080/metrics
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## HTTP API

| Method | Path | Result |
|---|---|---|
| `GET` | `/health` | Service liveness document: `{"status": "ok"}` |
| `GET` | `/robots` | Fleet summary plus per-robot score, status, alerts, and original sample |
| `GET` | `/metrics` | Prometheus 0.0.4 text exposition for the current fleet snapshot |
| `GET` | any other path | `404` JSON with the available endpoints |

The exported metric contract is deliberately small and stable:

| Metric | Type | Labels | Meaning |
|---|---|---|---|
| `robot_fleet_robot_available` | gauge | `robot_id` | `1` when available for work, otherwise `0` |
| `robot_fleet_mission_latency_seconds` | gauge | `robot_id` | Latest end-to-end mission latency |
| `robot_fleet_faults_total` | counter | `robot_id` | Cumulative faults reported by the robot |
| `robot_fleet_safety_stops_total` | counter | `robot_id` | Cumulative safety-stop events |

Point Prometheus at the service with [`deploy/prometheus.yml`](deploy/prometheus.yml). When Prometheus runs directly on the host, replace `host.docker.internal` with `127.0.0.1`. The default API bind address is `127.0.0.1:8080`; use `--host` and `--port` to change it. The example has no authentication and should remain loopback-only unless it is placed behind an appropriate production gateway.

## Example dashboard

The dashboard below is an illustrative rendering of the repository's synthetic fleet snapshot, not a production capture.

![Synthetic fleet Prometheus dashboard](docs/prometheus-dashboard.svg)

## Project layout

```text
src/robot_fleet_observability/health.py     Health model, rules, and aggregation
src/robot_fleet_observability/synthetic.py  Safe demonstration fleet
src/robot_fleet_observability/metrics.py    Prometheus text exposition
src/robot_fleet_observability/api.py        Threaded read-only HTTP service
tests/test_health.py                        Scoring and aggregation tests
tests/test_metrics.py                       Exporter and HTTP integration tests
deploy/prometheus.yml                       Example scrape configuration
docs/ARCHITECTURE.md                        Design, contracts, and production path
```

## Engineering principles

- Keep every penalty and status transition auditable.
- Separate health evaluation from transport and data acquisition.
- Return deterministic, machine-readable output.
- Make demonstration data unmistakably synthetic.

See [Architecture](docs/ARCHITECTURE.md), [Contributing](CONTRIBUTING.md), and [Security](SECURITY.md).

## Contact

For professional opportunities and technical discussions: [ozaparthu055@gmail.com](mailto:ozaparthu055@gmail.com) · [Portfolio](https://parthoza.net) · [LinkedIn](https://www.linkedin.com/in/oza-parth)
