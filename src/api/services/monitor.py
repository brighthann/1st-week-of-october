# """API monitoring service for health checks."""
import asyncio
import aiohttp
import ssl
import socket
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import logging

from src.models.status_models import EndpointStatus, HealthStatus, EndpointConfig
from src.config.settings import MONITORED_ENDPOINTS

logger = logging.getLogger(__name__)


class APIMonitor:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.status_history: Dict[str, List[EndpointStatus]] = {}

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=30, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "DashMonitor/1.0"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_ssl_certificate(
        self, hostname: str, port: int = 443
    ) -> Dict[str, Any]:
        """Check SSL certificate validity and expiration."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    # Parse expiration date
                    not_after = datetime.strptime(
                        cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                    )
                    days_until_expiry = (not_after - datetime.utcnow()).days

                    return {
                        "valid": True,
                        "expires": not_after,
                        "days_until_expiry": days_until_expiry,
                        "issuer": dict(x[0] for x in cert["issuer"]),
                        "subject": dict(x[0] for x in cert["subject"]),
                    }
        except Exception as e:
            logger.error(f"SSL check failed for {hostname}: {e}")
            return {
                "valid": False,
                "error": str(e),
                "expires": None,
                "days_until_expiry": None,
            }

    async def check_endpoint(self, endpoint: Dict[str, Any]) -> EndpointStatus:
        """Check health of a single endpoint."""
        start_time = datetime.utcnow()

        try:
            # Make HTTP request
            async with self.session.get(
                endpoint["url"],
                timeout=aiohttp.ClientTimeout(total=endpoint.get("timeout", 10)),
            ) as response:
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds() * 1000

                # Check SSL if HTTPS
                ssl_info = {}
                if endpoint.get("check_ssl", False) and endpoint["url"].startswith(
                    "https://"
                ):
                    parsed_url = urlparse(endpoint["url"])
                    ssl_info = await self.check_ssl_certificate(parsed_url.hostname)

                # Determine status
                expected_status = endpoint.get("expected_status", 200)
                is_healthy = response.status == expected_status

                status = EndpointStatus(
                    name=endpoint["name"],
                    url=endpoint["url"],
                    status=HealthStatus.HEALTHY
                    if is_healthy
                    else HealthStatus.UNHEALTHY,
                    status_code=response.status,
                    response_time=round(response_time, 2),
                    ssl_valid=ssl_info.get("valid"),
                    ssl_expires=ssl_info.get("expires"),
                    timestamp=start_time,
                    error=None
                    if is_healthy
                    else f"Expected {expected_status}, got {response.status}",
                )

                # Store in history
                self._store_status_history(status)

                return status

        except asyncio.TimeoutError:
            status = EndpointStatus(
                name=endpoint["name"],
                url=endpoint["url"],
                status=HealthStatus.TIMEOUT,
                timestamp=start_time,
                error="Request timeout",
            )
            self._store_status_history(status)
            return status

        except Exception as e:
            logger.error(f"Error checking {endpoint['name']}: {e}")
            status = EndpointStatus(
                name=endpoint["name"],
                url=endpoint["url"],
                status=HealthStatus.ERROR,
                timestamp=start_time,
                error=str(e),
            )
            self._store_status_history(status)
            return status

    def _store_status_history(self, status: EndpointStatus):
        """Store status in history for uptime calculations."""
        if status.name not in self.status_history:
            self.status_history[status.name] = []

        self.status_history[status.name].append(status)

        # Keep only last 24 hours of data
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.status_history[status.name] = [
            s for s in self.status_history[status.name] if s.timestamp > cutoff_time
        ]

    def calculate_uptime(self, endpoint_name: str) -> float:
        """Calculate uptime percentage for an endpoint."""
        if endpoint_name not in self.status_history:
            return 100.0

        history = self.status_history[endpoint_name]
        if not history:
            return 100.0

        total_checks = len(history)
        successful_checks = sum(
            1 for status in history if status.status == HealthStatus.HEALTHY
        )

        return round((successful_checks / total_checks) * 100, 2)

    async def check_all_endpoints(self) -> List[EndpointStatus]:
        """Check all configured endpoints."""
        if not self.session:
            raise RuntimeError(
                "Monitor session not initialized. Use async context manager."
            )

        tasks = []
        for endpoint in MONITORED_ENDPOINTS:
            task = asyncio.create_task(self.check_endpoint(endpoint))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and add uptime data
        statuses = []
        for result in results:
            if isinstance(result, EndpointStatus):
                result.uptime_percentage = self.calculate_uptime(result.name)
                statuses.append(result)
            else:
                logger.error(f"Endpoint check failed: {result}")

        return statuses


# Global monitor instance
monitor = APIMonitor()
