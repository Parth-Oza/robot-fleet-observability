# Security and data handling

## Reporting a vulnerability

Please report suspected vulnerabilities privately through the email listed on the [maintainer's GitHub profile](https://github.com/Parth-Oza). Include reproduction steps and expected impact.

## Deployment warning

The bundled HTTP server is a local demonstration with no authentication or TLS. It binds to `127.0.0.1` by default. Do not expose it to an untrusted network without a production gateway, access control, TLS, validation, rate limiting, and operational monitoring.

## Data policy

Only synthetic fleet data belongs in this repository. Do not submit credentials, production endpoints, employer telemetry, customer information, facility identifiers, maps, missions, or other confidential material.
