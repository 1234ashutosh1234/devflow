#!/usr/bin/env python3
"""Wait for a specific Render commit and verify API + database readiness."""

from __future__ import annotations

import argparse
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def get_json(url: str, timeout: int) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "DevFlow-Production-Smoke-Test",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object from {url}")
    return payload


def verify(base_url: str, expected_commit: str, timeout: int) -> None:
    live = get_json(f"{base_url}/health", timeout)
    if live.get("status") != "ok":
        raise ValueError("Liveness endpoint did not return status=ok")

    ready = get_json(f"{base_url}/health/ready", timeout)
    if ready.get("status") != "ready" or ready.get("database") != "ok":
        raise ValueError("Readiness endpoint did not confirm database connectivity")

    actual_commit = ready.get("commit")
    if actual_commit != expected_commit:
        raise ValueError(
            "Render is not serving the expected commit yet "
            f"(expected {expected_commit[:12]}, received {str(actual_commit)[:12]})"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Backend base URL")
    parser.add_argument("--expected-commit", required=True, help="Full Git commit SHA")
    parser.add_argument("--attempts", type=int, default=30)
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--request-timeout", type=int, default=6)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    last_error = "No response received"

    for attempt in range(1, args.attempts + 1):
        try:
            verify(base_url, args.expected_commit, args.request_timeout)
            print(
                "PRODUCTION SMOKE TEST PASSED: API is live, PostgreSQL is reachable, "
                f"and Render serves commit {args.expected_commit}."
            )
            return 0
        except HTTPError as exc:
            last_error = f"HTTP {exc.code} while checking production endpoints"
        except (URLError, TimeoutError) as exc:
            last_error = f"Network/request error: {getattr(exc, 'reason', exc)}"
        except (ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)

        print(f"Attempt {attempt}/{args.attempts}: {last_error}", flush=True)
        if attempt < args.attempts:
            time.sleep(args.interval)

    print(
        "PRODUCTION SMOKE TEST FAILED: Render did not become ready on the expected "
        f"commit within the retry window. Last result: {last_error}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
