import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db_connect import SessionLocal, Base, engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield SessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
