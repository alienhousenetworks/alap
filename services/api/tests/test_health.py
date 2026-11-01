from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_liveness() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_system_endpoint() -> None:
    response = client.get("/api/v1/system")
    assert response.status_code == 200
    assert response.json()["name"] == "ALAP"
