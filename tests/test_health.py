import unittest

from robot_fleet_observability import FleetSample, score_sample, summarize_fleet


class HealthTests(unittest.TestCase):
    def test_healthy_robot_has_full_score(self) -> None:
        result = score_sample(FleetSample("r1", "now", 80, 0.95, 50, 40, True))
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["status"], "healthy")

    def test_degraded_localization_is_critical(self) -> None:
        result = score_sample(FleetSample("r2", "now", 80, 0.5, 50, 40, False))
        self.assertEqual(result["status"], "critical")
        self.assertIn("localization_degraded", [alert["code"] for alert in result["alerts"]])

    def test_empty_summary(self) -> None:
        result = summarize_fleet([])
        self.assertEqual(result["summary"]["robots"], 0)
        self.assertEqual(result["summary"]["average_health_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
