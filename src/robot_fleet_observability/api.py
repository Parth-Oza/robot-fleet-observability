"""Tiny read-only HTTP API around the synthetic fleet snapshot."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .health import summarize_fleet
from .metrics import render_prometheus
from .synthetic import sample_fleet


class FleetHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path == "/health":
            self._write_json({"status": "ok"})
        elif self.path == "/robots":
            self._write_json(summarize_fleet(sample_fleet()))
        elif self.path == "/metrics":
            self._write_response(
                render_prometheus(sample_fleet()).encode("utf-8"),
                content_type="text/plain; version=0.0.4; charset=utf-8",
            )
        else:
            self._write_json(
                {"error": "not_found", "available": ["/health", "/robots", "/metrics"]},
                status=404,
            )

    def _write_json(self, payload: object, status: int = 200) -> None:
        encoded = json.dumps(payload, indent=2).encode("utf-8")
        self._write_response(encoded, status=status, content_type="application/json; charset=utf-8")

    def _write_response(
        self,
        encoded: bytes,
        *,
        status: int = 200,
        content_type: str,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a synthetic robot fleet health API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), FleetHandler)
    print(f"Serving fleet API at http://{args.host}:{args.port} (/robots, /metrics)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
