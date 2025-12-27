from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthcheck_ok():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    payload = r.json()
    assert payload["data"]["status"] == "ok"
    assert payload["data"]["service"] == "assistant-scolarite-backend"
