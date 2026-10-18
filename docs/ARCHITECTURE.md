# Architecture

## Components

- `FleetSample` defines the telemetry contract.
- `score_sample` evaluates one robot using explicit thresholds and penalties.
- `summarize_fleet` aggregates status counts, average health, and active missions.
- `sample_fleet` provides clearly synthetic demonstration input.
- `render_prometheus` converts a snapshot into deterministic Prometheus 0.0.4 text.
- `FleetHandler` exposes the current snapshot through a read-only HTTP API.

## Metrics contract

The `/metrics` endpoint exposes four per-robot metric families. Each uses only the bounded `robot_id` label to avoid accidental high-cardinality dimensions such as timestamps or mission IDs.

| Metric | Type | Unit |
|---|---|---|
| `robot_fleet_robot_available` | Gauge | Boolean (`0` or `1`) |
| `robot_fleet_mission_latency_seconds` | Gauge | Seconds |
| `robot_fleet_faults_total` | Counter | Events |
| `robot_fleet_safety_stops_total` | Counter | Events |

Samples are sorted by robot ID so snapshots and tests remain reproducible. Label values follow Prometheus escaping rules. Invalid negative counters, negative or non-finite latency, and malformed field types are rejected rather than silently publishing corrupt telemetry.

## Health model

The score starts at 100 and subtracts documented penalties:

| Condition | Penalty | Alert severity |
|---|---:|---|
| Battery below 20% | 25 | Warning |
| Localization quality below 0.70 | 35 | Critical |
| CPU above 90% | 20 | Warning |
| Latency above 150 ms | 30 | Critical |

Scores are clamped to zero. Any critical alert produces critical status; otherwise any alert produces warning status. Because the model is explicit, an operator can understand exactly why a robot changed state.

## Current boundaries

- In-memory synthetic snapshot only.
- Read-only JSON and Prometheus endpoints.
- No authentication, persistence, or external integrations.
- No proprietary metrics, thresholds, identifiers, or operational data.

## Production-oriented extension path

1. Add a transport adapter for ROS2, MQTT, a time-series store, or a fleet service.
2. Validate units, timestamps, freshness, and schema versions before scoring.
3. Move thresholds into reviewed configuration with change control.
4. Add authentication, authorization, TLS, rate limiting, and structured request logs.
5. Publish metrics and traces to an observability backend.
6. Add stale-data, flapping, hysteresis, and alert-deduplication policies.
7. Load-test the API and define service-level objectives.

The scoring module should remain independent so rules can be tested without a server or live fleet.
