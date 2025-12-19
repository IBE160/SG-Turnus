import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from backend.main import app
from backend.app.services.nlp_service import Intent, UserState
from backend.app.api.schemas import NextStep, ClarityResponse

def test_true():
    assert True