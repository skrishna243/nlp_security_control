def test_healthz_ok(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "uptime_seconds" in data
    assert "system_state" in data


def test_healthz_correlation_id_generated(client):
    r = client.get("/healthz")
    assert "x-correlation-id" in r.headers


def test_healthz_correlation_id_echoed(client):
    r = client.get("/healthz", headers={"X-Correlation-ID": "test-abc-123"})
    assert r.headers.get("x-correlation-id") == "test-abc-123"
