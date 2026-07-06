from app.models import User


def test_register_candidate(client, session):
    user_data = {
        "name": "Candidate",
        "email": "candidate@example.com",
        "password": "candidate123",
        "role": "candidate"
    }

    response = client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == 200
    assert response.json()["name"] == user_data["name"]
    assert response.json()["email"] == user_data["email"]

    user = session.query(User).filter(
        User.email == user_data["email"]
    ).first()

    assert user is not None
    assert user.email == user_data["email"]
    assert user.role == user_data["role"]


def test_candidate_login(client, create_user):

    candidate = create_user(
        name="Candidate",
        email="candidate@example.com",
        password="candidate123",
        role="candidate"
    )

    response = client.post(
        "/auth/login",
        data={
            "username": candidate["request"]["email"],
            "password": candidate["request"]["password"]
        }
    )

    assert response.status_code == 200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"


def test_recruiter_login(client, create_user):

    recruiter = create_user(
        name="Recruiter",
        email="recruiter@example.com",
        password="recruiter123",
        role="recruiter"
    )

    response = client.post(
        "/auth/login",
        data={
            "username": recruiter["request"]["email"],
            "password": recruiter["request"]["password"]
        }
    )

    assert response.status_code == 200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"