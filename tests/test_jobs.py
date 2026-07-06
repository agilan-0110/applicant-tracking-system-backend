from app.models import Job


def _create_job(authorized_recruiter_client, **overrides):
    payload = {
        "title": "Backend Engineer",
        "description": "Build and maintain backend services.",
        "location": "Remote",
        "min_salary": 60000,
        "max_salary": 90000,
    }
    payload.update(overrides)
    response = authorized_recruiter_client.post("/jobs/", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_create_job_as_recruiter_success(authorized_recruiter_client):
    response = authorized_recruiter_client.post(
        "/jobs/",
        json={
            "title": "Senior Backend Engineer",
            "description": "Lead the platform team.",
            "location": "Remote",
            "min_salary": 100000,
            "max_salary": 150000,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Senior Backend Engineer"
    assert body["min_salary"] == 100000
    assert body["max_salary"] == 150000
    assert body["recruiter_id"] is not None


def test_create_job_as_candidate_forbidden(authorized_client):
    response = authorized_client.post(
        "/jobs/",
        json={
            "title": "Should not be created",
            "description": "n/a",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only recruiters can create jobs."


def test_get_job_by_id_success(authorized_recruiter_client):
    created = _create_job(authorized_recruiter_client, title="Findable Job")

    response = authorized_recruiter_client.get(f"/jobs/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["title"] == "Findable Job"


def test_get_job_by_id_not_found_returns_404(authorized_recruiter_client):
    response = authorized_recruiter_client.get("/jobs/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_my_jobs_returns_only_recruiter_jobs(
    authorized_recruiter_client, client, create_user
):
    _create_job(authorized_recruiter_client, title="Mine 1")
    _create_job(authorized_recruiter_client, title="Mine 2")

    # Create a second recruiter with their own job — should be excluded
    # from the first recruiter's `/jobs/my` listing.
    other = create_user(
        name="Other Recruiter",
        email="other-recruiter-my@example.com",
        password="otherpass",
        role="recruiter",
    )
    login_resp = client.post(
        "/auth/login",
        data={
            "username": other["request"]["email"],
            "password": other["request"]["password"],
        },
    )
    assert login_resp.status_code == 200
    other_token = login_resp.json()["access_token"]

    # The `client` fixture's headers are shared across tests, so save
    # the prior value, set the recruiter token for this test, then
    # restore it on teardown via a try/finally.
    original_auth = client.headers.get("Authorization")
    client.headers = {**client.headers, "Authorization": f"Bearer {other_token}"}
    try:
        _create_job(client, title="Not Mine")
    finally:
        if original_auth is None:
            client.headers.pop("Authorization", None)
        else:
            client.headers["Authorization"] = original_auth

    response = authorized_recruiter_client.get("/jobs/my")

    assert response.status_code == 200
    jobs = response.json()
    titles = [job["title"] for job in jobs]
    assert "Mine 1" in titles
    assert "Mine 2" in titles
    assert "Not Mine" not in titles
    for job in jobs:
        assert "applicant_count" in job


def test_my_jobs_as_candidate_forbidden(authorized_client):
    response = authorized_client.get("/jobs/my")

    assert response.status_code == 403
    assert response.json()["detail"] == "Only recruiters can access this endpoint."


def test_update_job_as_owner_success(authorized_recruiter_client, session):
    created = _create_job(authorized_recruiter_client, title="Old Title")

    response = authorized_recruiter_client.put(
        f"/jobs/{created['id']}",
        json={
            "title": "New Title",
            "description": "Updated description.",
            "location": "Hybrid",
            "min_salary": 70000,
            "max_salary": 110000,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New Title"
    assert body["description"] == "Updated description."
    assert body["location"] == "Hybrid"
    assert body["min_salary"] == 70000
    assert body["max_salary"] == 110000

    job = session.query(Job).filter(Job.id == created["id"]).first()
    assert job.title == "New Title"


def test_update_job_as_other_recruiter_forbidden(
    authorized_recruiter_client, client, create_user
):
    created = _create_job(authorized_recruiter_client, title="Not Yours")

    other = create_user(
        name="Other Recruiter",
        email="other-recruiter-update@example.com",
        password="otherpass",
        role="recruiter",
    )
    login_resp = client.post(
        "/auth/login",
        data={
            "username": other["request"]["email"],
            "password": other["request"]["password"],
        },
    )
    assert login_resp.status_code == 200
    other_token = login_resp.json()["access_token"]

    original_auth = client.headers.get("Authorization")
    client.headers = {**client.headers, "Authorization": f"Bearer {other_token}"}
    try:
        response = client.put(
            f"/jobs/{created['id']}",
            json={
                "title": "Hijacked",
                "description": "x",
                "location": "x",
                "min_salary": 1,
                "max_salary": 2,
            },
        )
    finally:
        if original_auth is None:
            client.headers.pop("Authorization", None)
        else:
            client.headers["Authorization"] = original_auth

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only update your own jobs."


def test_update_job_as_candidate_forbidden(
    authorized_recruiter_client, authorized_client
):
    created = _create_job(authorized_recruiter_client, title="Stay Put")

    response = authorized_client.put(
        f"/jobs/{created['id']}",
        json={
            "title": "Hacked",
            "description": "x",
            "location": "x",
            "min_salary": 1,
            "max_salary": 2,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only recruiters can update jobs."


def test_update_job_not_found_returns_404(authorized_recruiter_client):
    response = authorized_recruiter_client.put(
        "/jobs/99999",
        json={
            "title": "x",
            "description": "x",
            "location": "x",
            "min_salary": 1,
            "max_salary": 2,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_delete_job_as_owner_success(authorized_recruiter_client, session):
    created = _create_job(authorized_recruiter_client, title="Disposable")

    response = authorized_recruiter_client.delete(f"/jobs/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {"message": "Job deleted successfully"}

    job = session.query(Job).filter(Job.id == created["id"]).first()
    assert job is None


def test_delete_job_as_other_recruiter_forbidden(
    authorized_recruiter_client, client, create_user
):
    created = _create_job(authorized_recruiter_client, title="Stay Around")

    other = create_user(
        name="Other Recruiter",
        email="other-recruiter-delete@example.com",
        password="otherpass",
        role="recruiter",
    )
    login_resp = client.post(
        "/auth/login",
        data={
            "username": other["request"]["email"],
            "password": other["request"]["password"],
        },
    )
    assert login_resp.status_code == 200
    other_token = login_resp.json()["access_token"]

    original_auth = client.headers.get("Authorization")
    client.headers = {**client.headers, "Authorization": f"Bearer {other_token}"}
    try:
        response = client.delete(f"/jobs/{created['id']}")
    finally:
        if original_auth is None:
            client.headers.pop("Authorization", None)
        else:
            client.headers["Authorization"] = original_auth

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only delete your own jobs."


def test_delete_job_as_candidate_forbidden(
    authorized_recruiter_client, authorized_client
):
    created = _create_job(authorized_recruiter_client, title="Untouched")

    response = authorized_client.delete(f"/jobs/{created['id']}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Only recruiters can delete jobs."


def test_delete_job_not_found_returns_404(authorized_recruiter_client):
    response = authorized_recruiter_client.delete("/jobs/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
