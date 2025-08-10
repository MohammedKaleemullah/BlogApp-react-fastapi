import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db_connect import SessionLocal, Base, engine
from sqlalchemy.orm import sessionmaker

# Use a separate test DB URL or use SQLite in-memory for tests
# For simplicity, assume you use the same DB but drop tables before each test (not recommended for prod)

@pytest.fixture(scope="session")
def db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield SessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
