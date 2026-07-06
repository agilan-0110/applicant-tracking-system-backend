import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.testclient import TestClient

from app.database import base, get_db
from app.main import app

DATABASE_URL = 'postgresql://postgres:password@localhost:5432/ats_test_db'

engine = create_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def _register_user(test_client, name, email, password, role):
    """
    Helper that POSTs to /auth/register and returns the registered
    user payload on success. Asserts 200 so callers don't have to.
    """

    user_data = {
        "name": name,
        "email": email,
        "password": password,
        "role": role,
    }

    response = test_client.post(
        "/auth/register",
        json=user_data,
    )

    assert response.status_code == 200, response.text

    return user_data


def _login(test_client, email, password):
    response = test_client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture()
def session():
    base.metadata.drop_all(bind=engine)
    base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def create_user(client):
    """
    Returns a callable that registers a user via the shared
    `client` and returns both the request payload and the
    JSON response body.
    """

    def _create_user(
        name="Test User",
        email="test@example.com",
        password="testpassword",
        role="candidate",
    ):
        user_data = {
            "name": name,
            "email": email,
            "password": password,
            "role": role,
        }

        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200, response.text

        return {
            "request": user_data,
            "response": response.json(),
        }

    return _create_user


@pytest.fixture()
def authorized_client(session):
    """
    Registers a candidate against a fresh TestClient, logs them
    in, and yields a NEW TestClient whose `Authorization` header
    carries the JWT. Using a fresh client (rather than mutating
    the shared `client.headers`) lets a test request both
    `client` and `authorized_client` without header collisions.
    """

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    register_client = TestClient(app)
    user = _register_user(
        register_client,
        name="Candidate",
        email="candidate@example.com",
        password="candidate123",
        role="candidate",
    )
    token = _login(register_client, user["email"], user["password"])
    register_client.close()

    with TestClient(app) as authorized:
        authorized.headers = {
            **authorized.headers,
            "Authorization": f"Bearer {token}",
        }
        yield authorized

    app.dependency_overrides.clear()


@pytest.fixture()
def authorized_recruiter_client(session):
    """
    Same pattern as `authorized_client` but for a recruiter.
    """

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    register_client = TestClient(app)
    user = _register_user(
        register_client,
        name="Recruiter",
        email="recruiter@example.com",
        password="recruiter123",
        role="recruiter",
    )
    token = _login(register_client, user["email"], user["password"])
    register_client.close()

    with TestClient(app) as authorized:
        authorized.headers = {
            **authorized.headers,
            "Authorization": f"Bearer {token}",
        }
        yield authorized

    app.dependency_overrides.clear()


@pytest.fixture()
def job_payload():
    """
    Returns a fresh dict matching `JobCreate`. Callers can
    override individual fields to keep tests independent.
    """
    return {
        "title": "Backend Engineer",
        "description": "Build and maintain backend services.",
        "location": "Remote",
        "min_salary": 60000,
        "max_salary": 90000,
    }
