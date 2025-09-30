# Prometheus metrics endpoints
# import time
from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)

# Create custom registry to avoid conflicts
REGISTRY = CollectorRegistry()

# Metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
    registry=REGISTRY,
)

RESPONSE_TIME = Histogram(
    "api_response_time_seconds", "API response time in seconds", registry=REGISTRY
)

ENDPOINT_STATUS = Gauge(
    "endpoint_status",
    "Endpoint health status (1=healthy, 0=unhealthy)",
    ["name", "url"],
    registry=REGISTRY,
)

ENDPOINT_RESPONSE_TIME = Gauge(
    "endpoint_response_time_ms",
    "Endpoint response time in milliseconds",
    ["name", "url"],
    registry=REGISTRY,
)

ENDPOINT_UPTIME = Gauge(
    "endpoint_uptime_percentage",
    "Endpoint uptime percentage",
    ["name", "url"],
    registry=REGISTRY,
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


def update_endpoint_metrics(statuses):
    """Update Prometheus metrics with endpoint statuses."""
    for status in statuses:
        # Status metric (1 for healthy, 0 for unhealthy)
        status_value = 1 if status.status.value == "healthy" else 0
        ENDPOINT_STATUS.labels(name=status.name, url=status.url).set(status_value)

        # Response time metric
        if status.response_time:
            ENDPOINT_RESPONSE_TIME.labels(name=status.name, url=status.url).set(
                status.response_time
            )

        # Uptime percentage
        if status.uptime_percentage:
            ENDPOINT_UPTIME.labels(name=status.name, url=status.url).set(
                status.uptime_percentage
            )
