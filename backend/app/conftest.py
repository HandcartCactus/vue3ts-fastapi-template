from fastapi.testclient import TestClient
from .main import app
from .db.schemas.auth import UserCreate
from .db.database import engine, get_db, Base
from .db import crud
from .core.security import create_access_token

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from string import digits, ascii_letters, punctuation


import random

# Set up a testing database (SQLite in-memory example)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def test_client():
    # Set up the database tables
    Base.metadata.create_all(bind=engine)
    
    # Provide the test client
    client = TestClient(app)
    
    # Run tests
    yield client
    
    # Drop tables and clean up after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()

def get_new_username(db):
    regenerate = True
    while regenerate:
        username = ''.join(random.choices(digits + ascii_letters, k=32))
        regenerate = crud.get_user(db, username=username) is not None
    
    return username

@pytest.fixture
def get_db_username_password_token(test_db):
    username = get_new_username(test_db)
    password = ''.join(random.choices(digits + ascii_letters + punctuation, k=32))
    user_create = UserCreate(username=username, password=password)
    crud.create_user(test_db, user=user_create)
    token = create_access_token(data={"sub": username})

    yield test_db, username, password, token

    crud.delete_user(test_db, username=username)
