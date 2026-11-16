#!/usr/bin/env python3
"""Check DevFlow production API/database readiness and frontend availability."""

from __future__ import annotations

import argparse
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def get_response(url: str, timeout: int) -> tuple[int, bytes]:
    request = Request(
        url,
        headers={
            "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
            "User-Agent": "DevFlow-Production-Health-Monitor",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except (HTTPError, URLError):
        raise
    except OSError as exc:
        raise ConnectionError(f"Request to {url} failed: {exc}") from exc


def verify(api_url: str, frontend_url: str, timeout: int) -> None:
    api_base = api_url.rstrip("/")
    frontend_base = frontend_url.rstrip("/")

    health_status, health_body = get_response(f"{api_base}/health", timeout)
    if not 200 <= health_status < 300:
        raise ValueError(f"API liveness returned HTTP {health_status}")
    health_payload = json.loads(health_body.decode("utf-8"))
    if health_payload.get("status") != "ok":
        raise ValueError("API liveness did not return status=ok")

    ready_status, ready_body = get_response(f"{api_base}/health/ready", timeout)
    if not 200 <= ready_status < 300:
        raise ValueError(f"API readiness returned HTTP {ready_status}")
    ready_payload = json.loads(ready_body.decode("utf-8"))
    if ready_payload.get("status") != "ready" or ready_payload.get("database") != "ok":
        raise ValueError("API readiness did not confirm database connectivity")

    frontend_status, _ = get_response(frontend_base, timeout)
    if not 200 <= frontend_status < 300:
        raise ValueError(f"Frontend returned HTTP {frontend_status}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", required=True, help="Production API base URL")
    parser.add_argument("--frontend-url", required=True, help="Production frontend URL")
    parser.add_argument("--attempts", type=int, default=12)
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--request-timeout", type=int, default=12)
    args = parser.parse_args()

    if args.attempts < 1 or args.interval < 0 or args.request_timeout < 1:
        parser.error("attempts and request-timeout must be positive; interval cannot be negative")

    last_error = "No response received"
    for attempt in range(1, args.attempts + 1):
        try:
            verify(args.api_url, args.frontend_url, args.request_timeout)
            print(
                "PRODUCTION MONITOR PASSED: API liveness, PostgreSQL readiness, "
                "and frontend availability are all healthy."
            )
            return 0
        except HTTPError as exc:
            last_error = f"HTTP {exc.code} while checking {exc.url}"
        except URLError as exc:
            last_error = f"Network/request error: {getattr(exc, 'reason', exc)}"
        except (TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
        except OSError as exc:
            # ConnectionResetError and other socket-level failures can occur
            # while a hosted service is starting or briefly restarting. Treat
            # them as retryable checks instead of crashing the monitor.
            last_error = f"Connection/socket error: {exc}"

        print(f"Attempt {attempt}/{args.attempts}: {last_error}", flush=True)
        if attempt < args.attempts:
            time.sleep(args.interval)

    print(
        "PRODUCTION MONITOR FAILED: production checks did not pass after "
        f"{args.attempts} attempts. Last result: {last_error}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
