# Tests for API endpoints
# import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics/")
    assert response.status_code == 200
    # Prometheus metrics in plain text format
    assert response.headers["content-type"].startswith("text/plain")
