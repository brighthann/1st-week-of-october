# Pytest configuration and fixtures
import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set testing environment variable
os.environ["TESTING"] = "true"


@pytest.fixture(scope="session")
def client():
    # Create test client
    from src.api.main import app

    return TestClient(app)
