# Application configuration settings
# import os
from typing import Any, Dict, List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    API_TITLE: str = "API Health Monitor"
    API_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/monitoring"

    # Monitoring
    CHECK_INTERVAL: int = 30  # seconds
    ALERT_THRESHOLD: int = 2  # consecutive failures
    TIMEOUT_THRESHOLD: int = 5  # seconds

    # Alerting
    SLACK_WEBHOOK_URL: str = ""
    EMAIL_ALERTS_ENABLED: bool = False

    # Dashboard
    DASHBOARD_PORT: int = 8501
    DASHBOARD_TITLE: str = "API Health Monitor"

    class Config:
        env_file = ".env"


# Monitored endpoints configuration
MONITORED_ENDPOINTS: List[Dict[str, Any]] = [
    {
        "name": "GitHub API",
        "url": "https://api.github.com",
        "expected_status": 200,
        "timeout": 10,
        "check_ssl": True,
    },
    {
        "name": "JSONPlaceholder",
        "url": "https://jsonplaceholder.typicode.com/posts",
        "expected_status": 200,
        "timeout": 5,
        "check_ssl": True,
    },
    {
        "name": "REST",
        "url": "https://restcountries.com/v3.1/all",
        "expected_status": 200,
        "timeout": 8,
        "check_ssl": True,
    },
]

settings = Settings()
