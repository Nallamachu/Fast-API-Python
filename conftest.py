import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
import os
import tempfile

from app import app
import database as _database
import model as _model
import services as _service


# Create a temporary database for testing
@pytest.fixture(scope="session")
def test_db():
    """Create a test database."""
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False}
    )
    
    _database.Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Close engine before cleanup
    engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        pass  # File may still be in use on Windows


@pytest.fixture
def db_session(test_db):
    """Create a new database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = TestingSessionLocal()
    
    yield session
    
    # Clean up: delete all data and close
    session.query(_model.Post).delete()
    session.query(_model.User).delete()
    session.commit()
    session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with overridden dependencies."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[_service.get_db] = override_get_db
    
    test_client = TestClient(app)
    
    yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    import bcrypt
    # Hash the password "password"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw("password".encode('utf-8'), salt)
    
    user = _model.User(
        email="test@gmail.com",
        name="Test User",
        phone="1234567890",
        password=hashed_password.decode('utf-8')
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_post(db_session, test_user):
    """Create a test post."""
    post = _model.Post(
        title="Test Post",
        description="This is a test post",
        user_id=test_user.id
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


@pytest.fixture
def auth_token(test_user):
    """Generate a valid JWT token for test user."""
    from datetime import timedelta
    access_token_expires = timedelta(minutes=30)
    token = _service.create_access_token(
        data={"sub": test_user.email, "user_id": test_user.id},
        expires_delta=access_token_expires
    )
    return token
