from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from backend.app.models.user import Base # Import Base from where models are defined

# Get database URL from environment variable
# Use SQLite in-memory for E2E tests if E2E_TEST_MODE is set
if os.getenv("E2E_TEST_MODE") == "true":
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
