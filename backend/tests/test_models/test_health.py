import os
import requests
import pytest


BASE = os.environ.get("MODEL_BASE_URL", "http://localhost:8000")
RUN_LIVE = os.environ.get("RUN_LIVE_TESTS") == "1"


@pytest.mark.skipif(not RUN_LIVE, reason="Live services not started")
def test_health_ready_endpoints():
    r = requests.get(f"{BASE}/healthz")
    assert r.status_code == 200
    r2 = requests.get(f"{BASE}/readyz")
    assert r2.status_code == 200

