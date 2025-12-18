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

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # Use SQLite for fast in-memory testing

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a custom Base for testing to ensure it doesn't conflict with main app's Base
TestBase = declarative_base()

# Define test User and StudyMaterial models that inherit from TestBase
# This is necessary because the app's models inherit from Base, and we need to
# create tables using our test engine. Alternatively, one could use the app's Base
# directly and ensure the app's engine is used, but this approach allows more isolation.
class TestUser(TestBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    auth_provider_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    study_materials = relationship("TestStudyMaterial", back_populates="owner")

class TestStudyMaterial(TestBase):
    __tablename__ = "study_materials"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    processing_status = Column(String, default="pending")
    owner = relationship("TestUser", back_populates="study_materials")


@pytest.fixture(scope="function")
def session_override():
    """Override the get_db dependency to use a test database session."""
    TestBase.metadata.create_all(bind=engine)  # Create tables for test models
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        TestBase.metadata.drop_all(bind=engine) # Drop tables after test

@pytest.fixture(scope="function")
def client_with_db(session_override):
    """Provides a test client with a mocked database dependency."""
    app.dependency_overrides[get_db] = lambda: session_override # Override get_db to use test session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear() # Clear overrides after test

@pytest.fixture(scope="function")
def authenticated_client(client_with_db):
    """Provides an authenticated test client with a mocked user."""
    test_user = TestUser(
        auth_provider_id="test_auth_provider_id",
        email="test@example.com",
        is_verified=True,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db = next(get_db())
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # Mock get_current_user to return our test_user
    with patch('backend.app.dependencies.get_current_user', return_value=test_user):
        yield client_with_db, test_user

@pytest.fixture(autouse=True)
def mock_s3_service():
    """Mocks the S3 service for file uploads/deletions."""
    mock_upload_file = MagicMock(return_value="mock_s3_key_123")
    mock_delete_file = MagicMock(return_value=True)

    with patch('backend.app.api.v1.study_materials.shutil.copyfileobj'), \
         patch('backend.app.api.v1.study_materials.os.remove'), \
         patch('backend.app.services.storage_service.upload_file_to_s3', new=mock_upload_file), \
         patch('backend.app.services.storage_service.delete_file_from_s3', new=mock_delete_file):
        yield mock_upload_file, mock_delete_file

# --- Tests ---
def test_create_study_material(authenticated_client, mock_s3_service):
    client, user = authenticated_client
    file_content = b"Test file content."
    file_name = "document.txt"

    response = client.post(
        "/api/v1/study-materials",
        files={"file": (file_name, file_content, "text/plain")}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == file_name
    assert data["user_id"] == user.id
    assert data["processing_status"] == "pending"
    assert "s3_key" in data # This currently checks the placeholder s3_key

    # Verify database entry
    db = next(get_db())
    material = db.query(StudyMaterial).filter(StudyMaterial.id == data["id"]).first()
    assert material is not None
    assert material.file_name == file_name
    assert material.user_id == user.id

def test_read_study_materials(authenticated_client):
    client, user = authenticated_client
    db = next(get_db())

    # Create test materials
    material1 = StudyMaterial(user_id=user.id, file_name="doc1.txt", s3_key="key1", processing_status="complete")
    material2 = StudyMaterial(user_id=user.id, file_name="doc2.pdf", s3_key="key2", processing_status="pending")
    db.add_all([material1, material2])
    db.commit()
    db.refresh(material1)
    db.refresh(material2)

    response = client.get("/api/v1/study-materials")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(m["file_name"] == "doc1.txt" for m in data)
    assert any(m["file_name"] == "doc2.pdf" for m in data)

def test_read_single_study_material(authenticated_client):
    client, user = authenticated_client
    db = next(get_db())

    material = StudyMaterial(user_id=user.id, file_name="single.txt", s3_key="single_key", processing_status="complete")
    db.add(material)
    db.commit()
    db.refresh(material)

    response = client.get(f"/api/v1/study-materials/{material.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == material.id
    assert data["file_name"] == "single.txt"

def test_read_single_study_material_not_found(authenticated_client):
    client, user = authenticated_client
    response = client.get(f"/api/v1/study-materials/999") # Non-existent ID
    assert response.status_code == 404

def test_read_single_study_material_not_owned(authenticated_client):
    client, user = authenticated_client
    db = next(get_db())

    # Create material for a different user
    other_user = TestUser(auth_provider_id="other_auth", email="other@example.com", is_verified=True)
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    other_material = StudyMaterial(user_id=other_user.id, file_name="other.txt", s3_key="other_key", processing_status="complete")
    db.add(other_material)
    db.commit()
    db.refresh(other_material)

    response = client.get(f"/api/v1/study-materials/{other_material.id}")
    assert response.status_code == 404 # Should be 404 if not found for current user

def test_update_study_material(authenticated_client):
    client, user = authenticated_client
    db = next(get_db())

    material = StudyMaterial(user_id=user.id, file_name="old.txt", s3_key="old_key", processing_status="pending")
    db.add(material)
    db.commit()
    db.refresh(material)

    update_data = {"file_name": "new.txt", "processing_status": "complete"}
    response = client.put(f"/api/v1/study-materials/{material.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "new.txt"
    assert data["processing_status"] == "complete"

    # Verify database update
    updated_material = db.query(StudyMaterial).filter(StudyMaterial.id == material.id).first()
    assert updated_material.file_name == "new.txt"
    assert updated_material.processing_status == "complete"

def test_update_study_material_not_found(authenticated_client):
    client, user = authenticated_client
    update_data = {"file_name": "new.txt"}
    response = client.put(f"/api/v1/study-materials/999", json=update_data)
    assert response.status_code == 404

def test_update_study_material_not_owned(authenticated_client):
    client, user = authenticated_client
    db = next(get_db())

    other_user = TestUser(auth_provider_id="other_auth_update", email="other_update@example.com", is_verified=True)
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    other_material = StudyMaterial(user_id=other_user.id, file_name="other_update.txt", s3_key="other_update_key", processing_status="complete")
    db.add(other_material)
    db.commit()
    db.refresh(other_material)

    update_data = {"file_name": "malicious_rename.txt"}
    response = client.put(f"/api/v1/study-materials/{other_material.id}", json=update_data)
    assert response.status_code == 404

def test_get_updated_study_materials(authenticated_client):
    client, user = authenticated_client
    db = next(get_db())

    # Create materials with different updated_at times
    now = datetime.datetime.utcnow()
    old_material_time = now - datetime.timedelta(days=1)
    new_material_time = now - datetime.timedelta(minutes=5)
    newer_material_time = now - datetime.timedelta(minutes=1)

    material_old = StudyMaterial(user_id=user.id, file_name="old.txt", s3_key="old_key", updated_at=old_material_time)
    material_new = StudyMaterial(user_id=user.id, file_name="new.txt", s3_key="new_key", updated_at=new_material_time)
    material_newer = StudyMaterial(user_id=user.id, file_name="newer.txt", s3_key="newer_key", updated_at=newer_material_time)
    
    db.add_all([material_old, material_new, material_newer])
    db.commit()

    # Query for updates since 'new_material_time'
    since_timestamp = new_material_time.isoformat() + "Z" # FastAPI expects ISO format, 'Z' for UTC
    response = client.get(f"/api/v1/study-materials/updates?since={since_timestamp}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # Only material_newer should be returned
    assert data[0]["file_name"] == "newer.txt"

def test_delete_study_material(authenticated_client):
    client, user = authenticated_client
    db = next(get_db())

    material = StudyMaterial(user_id=user.id, file_name="delete_me.txt", s3_key="delete_key", processing_status="pending")
    db.add(material)
    db.commit()
    db.refresh(material)

    response = client.delete(f"/api/v1/study-materials/{material.id}")
    assert response.status_code == 204

    # Verify deletion from database
    deleted_material = db.query(StudyMaterial).filter(StudyMaterial.id == material.id).first()
    assert deleted_material is None

def test_delete_study_material_not_found(authenticated_client):
    client, user = authenticated_client
    response = client.delete(f"/api/v1/study-materials/999") # Non-existent ID
    assert response.status_code == 404

def test_delete_study_material_not_owned(authenticated_client):
    client, user = authenticated_client
    db = next(get_db())

    other_user = TestUser(auth_provider_id="other_auth_delete", email="other_delete@example.com", is_verified=True)
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    other_material = StudyMaterial(user_id=other_user.id, file_name="other_delete.txt", s3_key="other_delete_key", processing_status="complete")
    db.add(other_material)
    db.commit()
    db.refresh(other_material)

    response = client.delete(f"/api/v1/study-materials/{other_material.id}")
    assert response.status_code == 404

def test_update_study_material_s3(authenticated_client, mock_s3_service):
    """Verify that updating a study material also triggers an S3 upload."""
    client, user = authenticated_client
    db = next(get_db())
    mock_upload, _ = mock_s3_service

    material = StudyMaterial(user_id=user.id, file_name="original.txt", s3_key="original_key", processing_status="pending")
    db.add(material)
    db.commit()
    db.refresh(material)

    file_content = b"Updated file content."
    file_name = "updated.txt"
    response = client.put(
        f"/api/v1/study-materials/{material.id}/file",
        files={"file": (file_name, file_content, "text/plain")}
    )

    assert response.status_code == 200
    mock_upload.assert_called_once()
    db_material = db.query(StudyMaterial).filter(StudyMaterial.id == material.id).first()
    assert db_material.file_name == file_name
    assert db_material.s3_key == "mock_s3_key_123"

def test_delete_study_material_s3(authenticated_client, mock_s3_service):
    """Verify that deleting a study material also triggers an S3 deletion."""
    client, user = authenticated_client
    db = next(get_db())
    _, mock_delete = mock_s3_service

    material = StudyMaterial(user_id=user.id, file_name="to_delete.txt", s3_key="delete_this_key", processing_status="complete")
    db.add(material)
    db.commit()
    db.refresh(material)

    response = client.delete(f"/api/v1/study-materials/{material.id}")

    assert response.status_code == 204
    mock_delete.assert_called_with("delete_this_key")
    db_material = db.query(StudyMaterial).filter(StudyMaterial.id == material.id).first()
    assert db_material is None

