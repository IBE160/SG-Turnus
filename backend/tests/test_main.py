import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_read_root():
    """Test the health check endpoint."""
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}