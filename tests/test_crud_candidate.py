from app.models import Candidate


def _profile_payload(**overrides):
    payload = {
        "phone": "+1-555-0100",
        "skills": "Python, SQL, FastAPI",
        "experience_years": 3,
        "education": "B.Tech Computer Science",
    }
    payload.update(overrides)
    return payload


def test_create_candidate_profile_success(client, authorized_client, session):
    response = authorized_client.post(
        "/candidate/profile",
        json=_profile_payload(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == "+1-555-0100"
    assert body["skills"] == "Python, SQL, FastAPI"
    assert body["experience_years"] == 3
    assert body["education"] == "B.Tech Computer Science"

    candidate = (
        session.query(Candidate)
        .filter(Candidate.user_id == body["user_id"])
        .first()
    )
    assert candidate is not None
    assert candidate.skills == "Python, SQL, FastAPI"


def test_create_profile_when_not_candidate_role_forbidden(
    client, create_user, authorized_recruiter_client
):
    response = authorized_recruiter_client.post(
        "/candidate/profile",
        json=_profile_payload(),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only candidates can create profiles."


def test_create_profile_when_already_exists_conflict(client, authorized_client):
    payload = _profile_payload()
    first = authorized_client.post("/candidate/profile", json=payload)
    assert first.status_code == 200

    second = authorized_client.post("/candidate/profile", json=payload)
    assert second.status_code == 400
    assert second.json()["detail"] == "Candidate profile already exists."


def test_get_my_profile_success(client, authorized_client):
    create = authorized_client.post(
        "/candidate/profile",
        json=_profile_payload(phone="+1-555-9999"),
    )
    assert create.status_code == 200

    response = authorized_client.get("/candidate/profile")

    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == "+1-555-9999"
    assert body["skills"] == "Python, SQL, FastAPI"


def test_get_profile_when_not_candidate_role_forbidden(
    client, authorized_recruiter_client
):
    response = authorized_recruiter_client.get("/candidate/profile")

    assert response.status_code == 403
    assert response.json()["detail"] == "Only candidates can view profiles."


def test_get_profile_when_none_returns_404(client, authorized_client):
    response = authorized_client.get("/candidate/profile")

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found."


def test_update_profile_success(client, authorized_client):
    authorized_client.post(
        "/candidate/profile",
        json=_profile_payload(),
    )

    response = authorized_client.put(
        "/candidate/profile",
        json=_profile_payload(
            phone="+1-555-1111",
            skills="Go, Kubernetes",
            experience_years=5,
            education="M.S. Computer Science",
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == "+1-555-1111"
    assert body["skills"] == "Go, Kubernetes"
    assert body["experience_years"] == 5
    assert body["education"] == "M.S. Computer Science"


def test_update_profile_when_not_found_returns_404(client, authorized_client):
    response = authorized_client.put(
        "/candidate/profile",
        json=_profile_payload(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found."


def test_update_profile_when_not_candidate_role_forbidden(
    client, authorized_recruiter_client
):
    response = authorized_recruiter_client.put(
        "/candidate/profile",
        json=_profile_payload(),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only candidates can update profiles."
