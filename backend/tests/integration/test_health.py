import pytest
from fastapi.testclient import TestClient

from evidencerag.interfaces.api.app import create_app
from evidencerag.settings import Settings


@pytest.mark.integration
def test_health_ok_when_database_is_up() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_503_with_error_envelope_when_database_is_down() -> None:
    settings = Settings(database_url="postgresql://x:x@localhost:1/x", db_timeout_s=0.5)
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "service_unavailable"
    assert error["retryable"] is True
