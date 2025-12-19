import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from unittest.mock import patch, MagicMock
import datetime
import os

from backend.main import app
from backend.app.database import get_db, Base
from backend.app.models.user import User
from backend.app.models.study_material import StudyMaterial

def test_true():
    assert True
