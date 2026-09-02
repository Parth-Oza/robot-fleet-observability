"""Tiny read-only HTTP API around the synthetic fleet snapshot."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .health import summarize_fleet
from .synthetic import sample_fleet


class FleetHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path == "/health":
            self._write_json({"status": "ok"})
        elif self.path == "/robots":
            self._write_json(summarize_fleet(sample_fleet()))
        else:
            self._write_json({"error": "not_found", "available": ["/health", "/robots"]}, status=404)

    def _write_json(self, payload: object, status: int = 200) -> None:
        encoded = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
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
    print(f"Serving http://{args.host}:{args.port}/robots")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
