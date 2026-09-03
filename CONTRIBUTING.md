# Contributing

Contributions that improve scoring clarity, validation, documentation, or tests are welcome.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
fleet-observability --port 8080
```

## Change requirements

- Add tests for every new threshold, penalty, alert, or aggregate field.
- Keep health logic explicit and explainable.
- Preserve the separation between scoring, sample generation, and HTTP transport.
- Use synthetic samples only; never submit operational telemetry or private identifiers.
- Document API or response-contract changes in the README and architecture notes.

Pull requests should state the operational question being addressed and show how the result was verified.
