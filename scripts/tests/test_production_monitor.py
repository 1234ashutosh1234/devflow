"""Unit tests for the standard-library production monitor."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from scripts import production_monitor


class FakeResponse:
    def __init__(self, status: int, body: dict | str) -> None:
        self.status = status
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        if isinstance(self.body, dict):
            return json.dumps(self.body).encode("utf-8")
        return self.body.encode("utf-8")


class ProductionMonitorTests(unittest.TestCase):
    @patch("scripts.production_monitor.urlopen")
    def test_verify_checks_api_liveness_readiness_and_frontend(self, mocked_urlopen):
        mocked_urlopen.side_effect = [
            FakeResponse(200, {"status": "ok"}),
            FakeResponse(200, {"status": "ready", "database": "ok"}),
            FakeResponse(200, "<html>DevFlow</html>"),
        ]

        production_monitor.verify(
            "https://api.example.test/",
            "https://app.example.test/",
            timeout=5,
        )

        self.assertEqual(mocked_urlopen.call_count, 3)
        requested_urls = [call.args[0].full_url for call in mocked_urlopen.call_args_list]
        self.assertEqual(
            requested_urls,
            [
                "https://api.example.test/health",
                "https://api.example.test/health/ready",
                "https://app.example.test",
            ],
        )

    @patch("scripts.production_monitor.urlopen")
    def test_get_response_reports_url_when_connection_resets(self, mocked_urlopen):
        mocked_urlopen.side_effect = ConnectionResetError("peer reset")

        with self.assertRaisesRegex(
            ConnectionError, "https://api.example.test/health"
        ):
            production_monitor.get_response(
                "https://api.example.test/health", timeout=5
            )

    @patch("scripts.production_monitor.urlopen")
    def test_verify_rejects_database_not_ready(self, mocked_urlopen):
        mocked_urlopen.side_effect = [
            FakeResponse(200, {"status": "ok"}),
            FakeResponse(503, {"detail": "Database unavailable"}),
        ]

        with self.assertRaises(ValueError):
            production_monitor.verify(
                "https://api.example.test",
                "https://app.example.test",
                timeout=5,
            )

        self.assertEqual(mocked_urlopen.call_count, 2)

    @patch("scripts.production_monitor.urlopen")
    def test_verify_rejects_unexpected_liveness_body(self, mocked_urlopen):
        mocked_urlopen.side_effect = [FakeResponse(200, {"status": "degraded"})]

        with self.assertRaises(ValueError):
            production_monitor.verify(
                "https://api.example.test",
                "https://app.example.test",
                timeout=5,
            )

    @patch("scripts.production_monitor.time.sleep")
    @patch("scripts.production_monitor.verify")
    def test_main_retries_after_connection_reset(self, mocked_verify, mocked_sleep):
        mocked_verify.side_effect = [ConnectionResetError("peer reset"), None]

        with patch(
            "sys.argv",
            [
                "production_monitor.py",
                "--api-url",
                "https://api.example.test",
                "--frontend-url",
                "https://app.example.test",
                "--attempts",
                "2",
                "--interval",
                "0",
            ],
        ):
            self.assertEqual(production_monitor.main(), 0)

        self.assertEqual(mocked_verify.call_count, 2)
        mocked_sleep.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
