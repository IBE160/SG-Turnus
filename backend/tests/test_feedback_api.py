import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.app.database import Base, get_db
from backend.app.models.user import User
from backend.app.models.study_material import StudyMaterial
from backend.app.dependencies import get_current_user
import datetime
import os

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture(scope="module")
def test_user():
    user = User(
        auth_provider_id="test_user_auth_id",
        email="test@example.com",
        is_verified=True,
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture(scope="module")
def test_study_material(test_user):
    study_material = StudyMaterial(
        user_id=test_user.id,
        file_name="test.pdf",
        s3_key="test_key",
        processing_status="completed"
    )
    db = TestingSessionLocal()
    db.add(study_material)
    db.commit()
    db.refresh(study_material)
    db.close()
    return study_material

def get_current_user_override():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "test@example.com").first()
    db.close()
    return user

app.dependency_overrides[get_current_user] = get_current_user_override

# --- Tests ---

def test_create_feedback(test_study_material):
    response = client.post(
        "/api/v1/feedback/",
        json={
            "material_id": test_study_material.id,
            "material_type": "summary",
            "rating": 5,
            "comments": "Great summary!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["material_id"] == test_study_material.id
    assert data["rating"] == 5
    assert data["comments"] == "Great summary!"
    assert "id" in data
    
    # Clean up test database file
    os.remove("./test.db")
