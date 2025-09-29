# Main FastAPI application
import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.config.settings import settings
from src.api.endpoints import health, status, metrics
from src.api.services.monitor import monitor
from src.api.services.alert import alert_service
from src.api.endpoints.metrics import REQUEST_COUNT, RESPONSE_TIME
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Background monitoring task
async def background_monitor():
    """Background task to continuously monitor endpoints."""
    logger.info("Starting background monitoring...")

    while True:
        try:
            async with monitor:
                statuses = await monitor.check_all_endpoints()
                await alert_service.process_alerts(statuses)
                metrics.update_endpoint_metrics(statuses)

            logger.info(f"Monitored {len(statuses)} endpoints")

        except Exception as e:
            logger.error(f"Background monitoring error: {e}")

        await asyncio.sleep(settings.CHECK_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting API Health Monitor...")

    # Start background monitoring task
    monitor_task = asyncio.create_task(background_monitor())

    yield

    # Shutdown
    logger.info("Shutting down API Health Monitor...")
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Monitor API endpoints for health, performance, and availability",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:3000",
    ],  # Streamlit and React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus metrics middleware
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    """Middleware to collect Prometheus metrics."""
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
    ).inc()

    RESPONSE_TIME.observe(time.time() - start_time)

    return response


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Include routers
app.include_router(health.router)
app.include_router(status.router)
app.include_router(metrics.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow(),
        "endpoints": {
            "health": "/health",
            "endpoint_status": "/api/status",
            "metrics": "/metrics",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_level="info",
    )
