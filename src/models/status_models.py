# """Data models for API status and metrics."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    TIMEOUT = "timeout"
    ERROR = "error"


class EndpointConfig(BaseModel):
    name: str
    url: HttpUrl
    expected_status: int = 200
    timeout: int = 10
    check_ssl: bool = True


class EndpointStatus(BaseModel):
    name: str
    url: str
    status: HealthStatus
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    ssl_valid: Optional[bool] = None
    ssl_expires: Optional[datetime] = None
    error: Optional[str] = None
    timestamp: datetime
    uptime_percentage: Optional[float] = None


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    endpoints: List[EndpointStatus]
    total_endpoints: int
    healthy_endpoints: int
    unhealthy_endpoints: int


class MetricsResponse(BaseModel):
    endpoint_name: str
    avg_response_time: float
    uptime_percentage: float
    total_checks: int
    successful_checks: int
    last_check: datetime


class AlertRule(BaseModel):
    endpoint_name: str
    rule_type: str  # "downtime", "slow_response", "ssl_expiry"
    threshold: float
    consecutive_failures: int = 2
    enabled: bool = True
