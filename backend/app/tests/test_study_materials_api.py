import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.app.database import Base, get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.study_material import StudyMaterial
from backend.app.models.generated_summary import GeneratedSummary
from backend.app.models.generated_flashcard_set import GeneratedFlashcardSet
from backend.app.core.ai.summarization_module import SummarizationModule
from backend.app.core.ai.flashcard_generation_module import FlashcardGenerationModule, Flashcard
from backend.app.core.ai.quiz_generation_module import QuizGenerationModule, QuizQuestion # New import
from unittest.mock import MagicMock, patch

# Setup for test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency for testing
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_current_user dependency for testing
@pytest.fixture()
def mock_current_user(session):
    user = User(email="test@example.com", auth_provider_id="test_auth_id", is_verified=True)
    session.add(user)
    session.commit()
    session.refresh(user)
    app.dependency_overrides[get_current_user] = lambda: user
    return user

@pytest.fixture()
def client(session, mock_current_user):
    app.dependency_overrides[get_db] = lambda: session
    yield TestClient(app)
    app.dependency_overrides = {} # Clear overrides

@pytest.fixture
def mock_summarization_module():
    with patch('backend.app.core.ai.summarization_module.SummarizationModule') as mock:
        instance = mock.return_value
        instance.generate_summary.return_value = "This is a test summary."
        yield instance

@pytest.fixture
def mock_flashcard_generation_module():
    with patch('backend.app.core.ai.flashcard_generation_module.FlashcardGenerationModule') as mock:
        instance = mock.return_value
        instance.generate_flashcards.return_value = [
            Flashcard(question="Q1", answer="A1"),
            Flashcard(question="Q2", answer="A2")
        ]
        yield instance

@pytest.fixture
def mock_quiz_generation_module(): # New fixture
    with patch('backend.app.core.ai.quiz_generation_module.QuizGenerationModule') as mock:
        instance = mock.return_value
        instance.generate_quiz.return_value = [
            QuizQuestion(question="Quiz Q1", options=["A", "B", "C"], correct_answer="A"),
            QuizQuestion(question="Quiz Q2", options=["X", "Y", "Z"], correct_answer="Y")
        ]
        yield instance

def test_create_study_material(client, mock_current_user, session):
    file_content = b"This is some test content for a study material."
    response = client.post(
        "/api/v1/study-materials/",
        files={"file": ("test_material.txt", file_content, "text/plain")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == "test_material.txt"
    assert data["user_id"] == mock_current_user.id
    assert data["processing_status"] == "pending"

    # Verify material is in DB
    material = session.query(StudyMaterial).filter_by(id=data["id"]).first()
    assert material is not None
    assert material.file_name == "test_material.txt"

def test_get_study_materials(client, mock_current_user, session):
    # Add a study material for the user
    material = StudyMaterial(user_id=mock_current_user.id, file_name="lecture.pdf", s3_key="key", processing_status="completed")
    session.add(material)
    session.commit()

    response = client.get("/api/v1/study-materials/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["file_name"] == "lecture.pdf"

def test_summarize_study_material_api(client, mock_current_user, session, mock_summarization_module):
    # Create a study material
    material = StudyMaterial(user_id=mock_current_user.id, file_name="article.txt", s3_key="key", processing_status="completed")
    session.add(material)
    session.commit()
    session.refresh(material)

    request_payload = {"text": "This is the text to summarize.", "detail_level": "normal"}
    response = client.post(
        f"/api/v1/study-materials/{material.id}/summarize",
        json=request_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "This is a test summary."
    assert data["study_material_id"] == material.id
    mock_summarization_module.generate_summary.assert_called_once_with(request_payload["text"], request_payload["detail_level"])

    # Verify summary is in DB
    summary = session.query(GeneratedSummary).filter_by(study_material_id=material.id).first()
    assert summary is not None
    assert summary.content == "This is a test summary."

def test_generate_flashcards_api(client, mock_current_user, session, mock_flashcard_generation_module):
    # Create a study material
    material = StudyMaterial(user_id=mock_current_user.id, file_name="notes.txt", s3_key="key", processing_status="completed")
    session.add(material)
    session.commit()
    session.refresh(material)

    request_payload = {"text": "Text for flashcard generation."}
    response = client.post(
        f"/api/v1/study-materials/{material.id}/flashcards",
        json=request_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["content"]) == 2
    assert data["content"][0]["question"] == "Q1"
    assert data["content"][0]["answer"] == "A1"
    assert data["study_material_id"] == material.id
    mock_flashcard_generation_module.generate_flashcards.assert_called_once_with(request_payload["text"])

    # Verify flashcard set is in DB
    flashcard_set = session.query(GeneratedFlashcardSet).filter_by(study_material_id=material.id).first()
    assert flashcard_set is not None
    assert len(flashcard_set.content) == 2
    assert flashcard_set.content[0]["question"] == "Q1"

def test_generate_quiz_api(client, mock_current_user, session, mock_quiz_generation_module): # New test function
    # Create a study material
    material = StudyMaterial(user_id=mock_current_user.id, file_name="quiz_source.txt", s3_key="key", processing_status="completed")
    session.add(material)
    session.commit()
    session.refresh(material)

    request_payload = {"text": "Text for quiz generation."}
    response = client.post(
        f"/api/v1/study-materials/{material.id}/quiz",
        json=request_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["content"]) == 2
    assert data["content"][0]["question"] == "Quiz Q1"
    assert data["content"][0]["options"] == ["A", "B", "C"]
    assert data["content"][0]["correct_answer"] == "A"
    assert data["study_material_id"] == material.id
    mock_quiz_generation_module.generate_quiz.assert_called_once_with(request_payload["text"])

    # Verify quiz is in DB
    quiz = session.query(GeneratedQuiz).filter_by(study_material_id=material.id).first()
    assert quiz is not None
    assert len(quiz.content) == 2
    assert quiz.content[0]["question"] == "Quiz Q1"


def test_get_summaries_for_study_material(client, mock_current_user, session, mock_summarization_module):
    material = StudyMaterial(user_id=mock_current_user.id, file_name="history.doc", s3_key="key", processing_status="completed")
    session.add(material)
    session.commit()
    session.refresh(material)

    # Generate a summary
    summary = GeneratedSummary(study_material_id=material.id, content="History summary", detail_level="normal")
    session.add(summary)
    session.commit()

    response = client.get(f"/api/v1/study-materials/{material.id}/summaries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["content"] == "History summary"

def test_get_flashcard_sets_for_study_material(client, mock_current_user, session, mock_flashcard_generation_module):
    material = StudyMaterial(user_id=mock_current_user.id, file_name="physics.doc", s3_key="key", processing_status="completed")
    session.add(material)
    session.commit()
    session.refresh(material)

    # Generate a flashcard set
    flashcard_set = GeneratedFlashcardSet(study_material_id=material.id, content=[{"question": "What is gravity?", "answer": "A force."}])
    session.add(flashcard_set)
    session.commit()

    response = client.get(f"/api/v1/study-materials/{material.id}/flashcard-sets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["content"][0]["question"] == "What is gravity?"