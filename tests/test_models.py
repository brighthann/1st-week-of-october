# Tests for data models
#import pytest
from datetime import datetime
from src.models.status_models import (
    EndpointStatus,
    HealthStatus,
    EndpointConfig,
    HealthCheckResponse,
)


def test_health_status_enum():
    """Test HealthStatus enum values."""
    assert HealthStatus.HEALTHY == "healthy"
    assert HealthStatus.UNHEALTHY == "unhealthy"
    assert HealthStatus.TIMEOUT == "timeout"
    assert HealthStatus.ERROR == "error"


def test_endpoint_config_model():
    #"""Test EndpointConfig model."""
    config = EndpointConfig(
        name="Test API", url="https://api.example.com", expected_status=200, timeout=10
    )

    assert config.name == "Test API"
    assert str(config.url) == "https://api.example.com/"
    assert config.expected_status == 200
    assert config.timeout == 10


def test_endpoint_status_model():
    """Test EndpointStatus model."""
    status = EndpointStatus(
        name="Test API",
        url="https://api.example.com",
        status=HealthStatus.HEALTHY,
        status_code=200,
        response_time=150.5,
        timestamp=datetime.utcnow(),
    )

    assert status.name == "Test API"
    assert status.status == HealthStatus.HEALTHY
    assert status.status_code == 200
    assert status.response_time == 150.5


def test_health_check_response_model():
    """Test HealthCheckResponse model."""
    endpoints = [
        EndpointStatus(
            name="API 1",
            url="https://api1.example.com",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow(),
        ),
        EndpointStatus(
            name="API 2",
            url="https://api2.example.com",
            status=HealthStatus.UNHEALTHY,
            timestamp=datetime.utcnow(),
        ),
    ]

    response = HealthCheckResponse(
        status="degraded",
        timestamp=datetime.utcnow(),
        endpoints=endpoints,
        total_endpoints=2,
        healthy_endpoints=1,
        unhealthy_endpoints=1,
    )

    assert response.status == "degraded"
    assert response.total_endpoints == 2
    assert response.healthy_endpoints == 1
    assert response.unhealthy_endpoints == 1
    assert len(response.endpoints) == 2
