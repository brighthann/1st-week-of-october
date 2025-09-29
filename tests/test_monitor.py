# Tests for monitoring service
import pytest
from src.api.services.monitor import APIMonitor
from src.config.settings import MONITORED_ENDPOINTS


@pytest.mark.asyncio
async def test_monitor_initialization():
    """Test monitor can be initialized."""
    async with APIMonitor() as monitor:
        assert monitor.session is not None
        assert monitor.status_history == {}


@pytest.mark.asyncio
async def test_check_endpoint():
    """Test checking a single endpoint."""
    async with APIMonitor() as monitor:
        # Use a reliable endpoint for testing
        test_endpoint = {
            "name": "Test API",
            "url": "https://api.github.com",
            "expected_status": 200,
            "timeout": 10,
            "check_ssl": False,
        }

        status = await monitor.check_endpoint(test_endpoint)

        assert status.name == "Test API"
        assert status.url == "https://api.github.com"
        assert status.status in ["healthy", "unhealthy", "timeout", "error"]
        assert status.timestamp is not None


@pytest.mark.asyncio
async def test_check_all_endpoints():
    """Test checking all configured endpoints."""
    async with APIMonitor() as monitor:
        statuses = await monitor.check_all_endpoints()

        assert len(statuses) == len(MONITORED_ENDPOINTS)
        assert all(hasattr(status, "name") for status in statuses)
        assert all(hasattr(status, "status") for status in statuses)


def test_uptime_calculation():
    """Test uptime percentage calculation."""
    monitor = APIMonitor()

    # With no history, uptime should be 100%
    uptime = monitor.calculate_uptime("test-endpoint")
    assert uptime == 100.0
