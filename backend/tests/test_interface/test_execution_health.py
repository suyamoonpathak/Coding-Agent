import os
import requests
import pytest


BASE = os.environ.get("EXEC_BASE_URL", "http://localhost:5000")
RUNNER = os.environ.get("RUNNER_BASE_URL", "http://localhost:5100")
RUN_LIVE = os.environ.get("RUN_LIVE_TESTS") == "1"


@pytest.mark.skipif(not RUN_LIVE, reason="Live services not started")
def test_gateway_health_ready():
    r = requests.get(f"{BASE}/healthz")
    assert r.status_code == 200
    r2 = requests.get(f"{BASE}/readyz")
    assert r2.status_code == 200


@pytest.mark.skipif(not RUN_LIVE, reason="Live services not started")
def test_runner_health_ready():
    r = requests.get(f"{RUNNER}/healthz")
    assert r.status_code == 200 or r.status_code == 503
    r2 = requests.get(f"{RUNNER}/readyz")
    assert r2.status_code == 200

