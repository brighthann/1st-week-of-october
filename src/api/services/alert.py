# """Alerting service for API monitoring."""
import aiohttp
#import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.models.status_models import EndpointStatus, HealthStatus
from src.config.settings import settings

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self):
        self.alert_history: Dict[str, List[Dict[str, Any]]] = {}
        self.last_alerts: Dict[str, datetime] = {}
        self.consecutive_failures: Dict[str, int] = {}

    async def process_alerts(self, statuses: List[EndpointStatus]):
        """Process alerts for endpoint statuses."""
        for status in statuses:
            await self._check_downtime_alert(status)
            await self._check_performance_alert(status)
            await self._check_ssl_expiry_alert(status)

    async def _check_downtime_alert(self, status: EndpointStatus):
        """Check if downtime alert should be triggered."""
        endpoint_name = status.name

        if status.status != HealthStatus.HEALTHY:
            # Increment consecutive failures
            self.consecutive_failures[endpoint_name] = (
                self.consecutive_failures.get(endpoint_name, 0) + 1
            )

            # Trigger alert if threshold reached
            if self.consecutive_failures[endpoint_name] >= settings.ALERT_THRESHOLD:
                await self._send_alert(
                    {
                        "type": "downtime",
                        "endpoint": endpoint_name,
                        "status": status.status.value,
                        "error": status.error,
                        "consecutive_failures": self.consecutive_failures[
                            endpoint_name
                        ],
                        "timestamp": status.timestamp.isoformat(),
                    }
                )
        else:
            # Reset consecutive failures and send recovery alert if needed
            if (
                self.consecutive_failures.get(endpoint_name, 0)
                >= settings.ALERT_THRESHOLD
            ):
                await self._send_alert(
                    {
                        "type": "recovery",
                        "endpoint": endpoint_name,
                        "status": "healthy",
                        "response_time": status.response_time,
                        "timestamp": status.timestamp.isoformat(),
                    }
                )

            self.consecutive_failures[endpoint_name] = 0

    async def _check_performance_alert(self, status: EndpointStatus):
        """Check if performance alert should be triggered."""
        if status.response_time and status.response_time > (
            settings.TIMEOUT_THRESHOLD * 1000
        ):
            await self._send_alert(
                {
                    "type": "slow_response",
                    "endpoint": status.name,
                    "response_time": status.response_time,
                    "threshold": settings.TIMEOUT_THRESHOLD * 1000,
                    "timestamp": status.timestamp.isoformat(),
                }
            )

    async def _check_ssl_expiry_alert(self, status: EndpointStatus):
        """Check if SSL certificate expiry alert should be triggered."""
        if status.ssl_expires:
            days_until_expiry = (status.ssl_expires - datetime.utcnow()).days
            if days_until_expiry <= 30:  # Alert 30 days before expiry
                await self._send_alert(
                    {
                        "type": "ssl_expiry",
                        "endpoint": status.name,
                        "expires": status.ssl_expires.isoformat(),
                        "days_until_expiry": days_until_expiry,
                        "timestamp": status.timestamp.isoformat(),
                    }
                )

    async def _send_alert(self, alert_data: Dict[str, Any]):
        """Send alert via configured channels."""
        # Prevent spam - don't send same alert type for same endpoint within 5 minutes
        alert_key = f"{alert_data['endpoint']}_{alert_data['type']}"
        now = datetime.utcnow()

        if alert_key in self.last_alerts:
            time_diff = now - self.last_alerts[alert_key]
            if time_diff < timedelta(minutes=5):
                return

        self.last_alerts[alert_key] = now

        # Store in history
        if alert_data["endpoint"] not in self.alert_history:
            self.alert_history[alert_data["endpoint"]] = []

        self.alert_history[alert_data["endpoint"]].append(alert_data)

        # Send to Slack if configured
        if settings.SLACK_WEBHOOK_URL:
            await self._send_slack_alert(alert_data)

        logger.info(f"Alert sent: {alert_data}")

    async def _send_slack_alert(self, alert_data: Dict[str, Any]):
        """Send alert to Slack webhook."""
        try:
            color = {
                "downtime": "#ff0000",  # Red
                "recovery": "#00ff00",  # Green
                "slow_response": "#ffaa00",  # Orange
                "ssl_expiry": "#ff00ff",  # Purple
            }.get(alert_data["type"], "#000000")

            message = self._format_slack_message(alert_data, color)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.SLACK_WEBHOOK_URL,
                    json=message,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to send Slack alert: {response.status}")
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")

    def _format_slack_message(
        self, alert_data: Dict[str, Any], color: str
    ) -> Dict[str, Any]:
        """Format alert message for Slack."""
        title_map = {
            "downtime": f"{alert_data['endpoint']} is DOWN",
            "recovery": f"{alert_data['endpoint']} has RECOVERED",
            "slow_response": f"{alert_data['endpoint']} is SLOW",
            "ssl_expiry": f"{alert_data['endpoint']} SSL expires soon",
        }

        title = title_map.get(alert_data["type"], f"Alert for {alert_data['endpoint']}")

        fields = []
        if alert_data.get("status"):
            fields.append(
                {"title": "Status", "value": alert_data["status"], "short": True}
            )
        if alert_data.get("response_time"):
            fields.append(
                {
                    "title": "Response Time",
                    "value": f"{alert_data['response_time']}ms",
                    "short": True,
                }
            )
        if alert_data.get("error"):
            fields.append(
                {"title": "Error", "value": alert_data["error"], "short": False}
            )
        if alert_data.get("days_until_expiry"):
            fields.append(
                {
                    "title": "Days Until Expiry",
                    "value": str(alert_data["days_until_expiry"]),
                    "short": True,
                }
            )

        return {
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "fields": fields,
                    "timestamp": alert_data["timestamp"],
                }
            ]
        }

    def get_alert_history(self, endpoint_name: str = None) -> List[Dict[str, Any]]:
        """Get alert history for endpoint or all endpoints."""
        if endpoint_name:
            return self.alert_history.get(endpoint_name, [])

        all_alerts = []
        for alerts in self.alert_history.values():
            all_alerts.extend(alerts)

        return sorted(all_alerts, key=lambda x: x["timestamp"], reverse=True)


# Global alert service instance
alert_service = AlertService()
