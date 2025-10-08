# Status and monitoring endpoints
from typing import List

from fastapi import APIRouter, HTTPException  # , BackgroundTasks

from src.api.endpoints.metrics import update_endpoint_metrics
from src.api.services.alert import alert_service
from src.api.services.monitor import monitor
from src.models.status_models import EndpointStatus, MetricsResponse

router = APIRouter(prefix="/api", tags=["monitoring"])


@router.get("/status", response_model=List[EndpointStatus])
async def get_endpoint_status():
    """Get current status of all monitored endpoints."""
    try:
        async with monitor:
            statuses = await monitor.check_all_endpoints()

        # Update Prometheus metrics
        update_endpoint_metrics(statuses)

        # Process alerts in background
        await alert_service.process_alerts(statuses)

        return statuses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/status/{endpoint_name}", response_model=EndpointStatus)
async def get_single_endpoint_status(endpoint_name: str):
    """Get status of a specific endpoint."""
    try:
        async with monitor:
            statuses = await monitor.check_all_endpoints()

        for status in statuses:
            if status.name.lower() == endpoint_name.lower():
                return status

        raise HTTPException(
            status_code=404, detail=f"Endpoint '{endpoint_name}' not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/metrics/{endpoint_name}", response_model=MetricsResponse)
async def get_endpoint_metrics(endpoint_name: str):
    """Get detailed metrics for a specific endpoint."""
    try:
        # Get current status
        async with monitor:
            statuses = await monitor.check_all_endpoints()

        target_status = None
        for status in statuses:
            if status.name.lower() == endpoint_name.lower():
                target_status = status
                break

        if not target_status:
            raise HTTPException(
                status_code=404, detail=f"Endpoint '{endpoint_name}' not found"
            )

        # Calculate metrics from history
        history = monitor.status_history.get(target_status.name, [])
        total_checks = len(history)
        successful_checks = sum(1 for s in history if s.status.value == "healthy")

        avg_response_time = 0.0
        if history:
            response_times = [s.response_time for s in history if s.response_time]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)

        return MetricsResponse(
            endpoint_name=target_status.name,
            avg_response_time=round(avg_response_time, 2),
            uptime_percentage=target_status.uptime_percentage or 100.0,
            total_checks=total_checks,
            successful_checks=successful_checks,
            last_check=target_status.timestamp,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/alerts")
async def get_alerts(endpoint_name: str = None):
    """Get alert history."""
    try:
        alerts = alert_service.get_alert_history(endpoint_name)
        return {"alerts": alerts, "total": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")
