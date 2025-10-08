# "Health check endpoints."""
from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.api.services.monitor import monitor
from src.models.status_models import HealthCheckResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=dict)
async def health_check():
    """Basic health check for the API itself."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "API Health Monitor",
        "version": "1.0.0",
    }


@router.get("/endpoints", response_model=HealthCheckResponse)
async def check_all_endpoints():
    """Check health of all monitored endpoints."""
    try:
        async with monitor:
            statuses = await monitor.check_all_endpoints()

        healthy_count = sum(1 for s in statuses if s.status.value == "healthy")

        return HealthCheckResponse(
            status="healthy" if healthy_count == len(statuses) else "degraded",
            timestamp=datetime.utcnow(),
            endpoints=statuses,
            total_endpoints=len(statuses),
            healthy_endpoints=healthy_count,
            unhealthy_endpoints=len(statuses) - healthy_count,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
