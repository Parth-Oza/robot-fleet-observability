import math
import threading
import unittest
from dataclasses import replace
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from robot_fleet_observability.api import FleetHandler
from robot_fleet_observability.health import FleetSample
from robot_fleet_observability.metrics import render_prometheus


def sample(robot_id: str = "robot-01", **overrides: object) -> FleetSample:
    base = FleetSample(
        robot_id=robot_id,
        timestamp="2026-01-01T12:00:00Z",
        battery_pct=80,
        localization_quality=0.95,
        cpu_pct=40,
        latency_ms=30,
        mission_active=True,
        available=True,
        mission_latency_ms=125,
        fault_count=2,
        safety_stop_count=1,
    )
    return replace(base, **overrides)


class PrometheusMetricsTests(unittest.TestCase):
    def test_renders_stable_metric_families(self) -> None:
        payload = render_prometheus([sample()])

        self.assertIn("# TYPE robot_fleet_robot_available gauge", payload)
        self.assertIn('robot_fleet_robot_available{robot_id="robot-01"} 1', payload)
        self.assertIn('robot_fleet_mission_latency_seconds{robot_id="robot-01"} 0.125', payload)
        self.assertIn('robot_fleet_faults_total{robot_id="robot-01"} 2', payload)
        self.assertIn('robot_fleet_safety_stops_total{robot_id="robot-01"} 1', payload)

    def test_output_is_sorted_and_label_values_are_escaped(self) -> None:
        payload = render_prometheus([sample("z-robot"), sample('a\\robot\n"quoted"')])
        escaped = 'robot_id="a\\\\robot\\n\\"quoted\\""'

        self.assertLess(payload.index(escaped), payload.index('robot_id="z-robot"'))

    def test_rejects_invalid_values(self) -> None:
        invalid_samples = (
            sample(mission_latency_ms=-1),
            sample(mission_latency_ms=math.inf),
            sample(fault_count=-1),
            sample(safety_stop_count=1.5),
        )

        for invalid in invalid_samples:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    render_prometheus([invalid])

    def test_metrics_endpoint_uses_prometheus_content_type(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), FleetHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = server.server_address
            with urlopen(f"http://{host}:{port}/metrics", timeout=2) as response:
                payload = response.read().decode("utf-8")
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers.get_content_type(), "text/plain")
                self.assertEqual(response.headers.get_param("version"), "0.0.4")
                self.assertIn("robot_fleet_safety_stops_total", payload)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
