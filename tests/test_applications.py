from app.models import Application


def _set_auth(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})


def _make_candidate_with_profile(client, create_user, name, email):
    """
    Registers a candidate, logs them in on the SHARED `client`,
    creates a profile, and returns (client, user_payload_dict, profile_dict).
    The shared `client` will have its Authorization header set to this
    candidate's token on return; callers should restore it after use.
    """

    user = create_user(
        name=name,
        email=email,
        password="candidate123",
        role="candidate",
    )
    login = client.post(
        "/auth/login",
        data={
            "username": user["request"]["email"],
            "password": user["request"]["password"],
        },
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    original_auth = client.headers.get("Authorization")
    _set_auth(client, token)

    try:
        profile = client.post(
            "/candidate/profile",
            json={
                "phone": "+1-555-0100",
                "skills": "Python, SQL",
                "experience_years": 2,
                "education": "B.Tech",
            },
        )
        assert profile.status_code == 200, profile.text
    except Exception:
        if original_auth is None:
            client.headers.pop("Authorization", None)
        else:
            client.headers["Authorization"] = original_auth
        raise

    return user, profile.json(), original_auth


def _make_candidate_no_profile(client, create_user, name, email):
    """Same as _make_candidate_with_profile but skips the profile step."""

    user = create_user(
        name=name,
        email=email,
        password="candidate123",
        role="candidate",
    )
    login = client.post(
        "/auth/login",
        data={
            "username": user["request"]["email"],
            "password": user["request"]["password"],
        },
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    original_auth = client.headers.get("Authorization")
    _set_auth(client, token)
    return user, original_auth


def _make_recruiter_with_job(
    client, create_user, name, email, job_payload
):
    """Registers a recruiter, logs them in, posts a job, and
    returns the recruiter's user payload + the created job dict.
    Restores prior Authorization on caller cleanup."""

    user = create_user(
        name=name,
        email=email,
        password="recruiter123",
        role="recruiter",
    )
    login = client.post(
        "/auth/login",
        data={
            "username": user["request"]["email"],
            "password": user["request"]["password"],
        },
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    original_auth = client.headers.get("Authorization")
    _set_auth(client, token)

    try:
        job_resp = client.post("/jobs/", json=job_payload)
        assert job_resp.status_code == 200, job_resp.text
    except Exception:
        if original_auth is None:
            client.headers.pop("Authorization", None)
        else:
            client.headers["Authorization"] = original_auth
        raise

    return user, job_resp.json(), original_auth


def _restore_auth(client, original):
    if original is None:
        client.headers.pop("Authorization", None)
    else:
        client.headers["Authorization"] = original



def test_apply_for_job_as_candidate_success(client, create_user, session):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C1", email="c1-apply@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R1", email="r1-apply@example.com",
        job_payload={
            "title": "Backend Engineer",
            "description": "Build things.",
            "location": "Remote",
            "min_salary": 50000,
            "max_salary": 80000,
        },
    )
    try:
        _restore_auth(client, rec_orig)
        response = client.post(f"/applications/{job['id']}")

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["job_id"] == job["id"]
        assert body["candidate_id"] == profile["id"]
        assert body["status"] == "Applied"

        db_app = (
            session.query(Application)
            .filter(Application.id == body["id"])
            .first()
        )
        assert db_app is not None
        assert db_app.status == "Applied"
    finally:
        _restore_auth(client, rec_orig)


def test_apply_twice_returns_409(client, create_user):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C2", email="c2-twice@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R2", email="r2-twice@example.com",
        job_payload={
            "title": "Job Twice",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        _restore_auth(client, rec_orig)
        first = client.post(f"/applications/{job['id']}")
        assert first.status_code == 200, first.text

        second = client.post(f"/applications/{job['id']}")
        assert second.status_code == 409
        assert second.json()["detail"] == "Already applied for this job."
    finally:
        _restore_auth(client, rec_orig)


def test_apply_as_recruiter_forbidden(client, create_user):
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R3", email="r3-forbidden@example.com",
        job_payload={
            "title": "Recruiter Applies",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        response = client.post(f"/applications/{job['id']}")
        assert response.status_code == 403
        assert response.json()["detail"] == "Only candidates can apply."
    finally:
        _restore_auth(client, rec_orig)


def test_apply_to_missing_job_returns_404(client, create_user):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C3", email="c3-missing@example.com",
    )
    try:
        response = client.post("/applications/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found."
    finally:
        _restore_auth(client, cand_orig)


def test_apply_when_candidate_profile_missing_returns_404(client, create_user):
    cand_user, cand_orig = _make_candidate_no_profile(
        client, create_user,
        name="C4", email="c4-noprofile@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R4", email="r4-noprofile@example.com",
        job_payload={
            "title": "Job NoProfile",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        
        login = client.post(
            "/auth/login",
            data={
                "username": cand_user["request"]["email"],
                "password": cand_user["request"]["password"],
            },
        )
        assert login.status_code == 200
        cand_token = login.json()["access_token"]
        _set_auth(client, cand_token)

        response = client.post(f"/applications/{job['id']}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Candidate profile not found."
    finally:
        _restore_auth(client, rec_orig)



def test_my_applications_returns_candidates_apps(
    client, create_user, session
):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C5", email="c5-myapps@example.com",
    )
    rec_user1, job1, rec1_orig = _make_recruiter_with_job(
        client, create_user,
        name="R5a", email="r5a-myapps@example.com",
        job_payload={
            "title": "Job A",
            "description": "A",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    rec_user2, job2, rec2_orig = _make_recruiter_with_job(
        client, create_user,
        name="R5b", email="r5b-myapps@example.com",
        job_payload={
            "title": "Job B",
            "description": "B",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        
        login = client.post(
            "/auth/login",
            data={
                "username": cand_user["request"]["email"],
                "password": cand_user["request"]["password"],
            },
        )
        cand_token = login.json()["access_token"]
        _set_auth(client, cand_token)

        client.post(f"/applications/{job1['id']}")
        client.post(f"/applications/{job2['id']}")

        response = client.get("/applications/my")
        assert response.status_code == 200
        apps = response.json()
        assert len(apps) == 2
        job_ids = {app["job_id"] for app in apps}
        assert job_ids == {job1["id"], job2["id"]}
        for app in apps:
            assert app["candidate_id"] == profile["id"]
    finally:
        _restore_auth(client, rec1_orig)


def test_my_applications_as_recruiter_forbidden(client, create_user):
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R6", email="r6-myapps@example.com",
        job_payload={
            "title": "Job MyApps",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        response = client.get("/applications/my")
        assert response.status_code == 403
        assert response.json()["detail"] == "Only candidates can view applications."
    finally:
        _restore_auth(client, rec_orig)




def test_get_job_applicants_as_owner_recruiter_success(
    client, create_user
):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C7", email="c7-applicants@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R7", email="r7-applicants@example.com",
        job_payload={
            "title": "Job Applicants",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        
        login = client.post(
            "/auth/login",
            data={
                "username": cand_user["request"]["email"],
                "password": cand_user["request"]["password"],
            },
        )
        cand_token = login.json()["access_token"]
        _set_auth(client, cand_token)
        client.post(f"/applications/{job['id']}")

        
        login2 = client.post(
            "/auth/login",
            data={
                "username": rec_user["request"]["email"],
                "password": rec_user["request"]["password"],
            },
        )
        rec_token = login2.json()["access_token"]
        _set_auth(client, rec_token)

        response = client.get(f"/applications/job/{job['id']}/applicants")
        assert response.status_code == 200, response.text
        applicants = response.json()
        assert len(applicants) == 1
        applicant = applicants[0]
        assert applicant["candidate_id"] == profile["id"]
        assert applicant["name"] == cand_user["request"]["name"]
        assert applicant["email"] == cand_user["request"]["email"]
        assert applicant["phone"] == "+1-555-0100"
        assert applicant["skills"] == "Python, SQL"
        assert applicant["experience_years"] == 2
        assert applicant["education"] == "B.Tech"
        assert applicant["status"] == "Applied"
    finally:
        _restore_auth(client, rec_orig)


def test_get_job_applicants_as_other_recruiter_forbidden(
    client, create_user
):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C8", email="c8-other-rec@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R8a", email="r8a-other-rec@example.com",
        job_payload={
            "title": "Job OtherRec",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    other = create_user(
        name="R8b",
        email="r8b-other-rec@example.com",
        password="otherpass",
        role="recruiter",
    )
    try:
        
        login = client.post(
            "/auth/login",
            data={
                "username": cand_user["request"]["email"],
                "password": cand_user["request"]["password"],
            },
        )
        cand_token = login.json()["access_token"]
        _set_auth(client, cand_token)
        client.post(f"/applications/{job['id']}")

        
        login2 = client.post(
            "/auth/login",
            data={
                "username": other["request"]["email"],
                "password": other["request"]["password"],
            },
        )
        other_token = login2.json()["access_token"]
        _set_auth(client, other_token)

        response = client.get(f"/applications/job/{job['id']}/applicants")
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You can only view applicants for your own jobs."
        )
    finally:
        _restore_auth(client, rec_orig)


def test_get_job_applicants_as_candidate_forbidden(client, create_user):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C9", email="c9-cand-applicants@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R9", email="r9-cand-applicants@example.com",
        job_payload={
            "title": "Job CandApplicants",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        
        login = client.post(
            "/auth/login",
            data={
                "username": cand_user["request"]["email"],
                "password": cand_user["request"]["password"],
            },
        )
        cand_token = login.json()["access_token"]
        _set_auth(client, cand_token)

        response = client.get(f"/applications/job/{job['id']}/applicants")
        assert response.status_code == 403
        assert response.json()["detail"] == "Only recruiters can view applicants."
    finally:
        _restore_auth(client, rec_orig)


def test_get_job_applicants_for_missing_job_returns_404(authorized_recruiter_client):
    response = authorized_recruiter_client.get(
        "/applications/job/99999/applicants"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found."




def test_update_application_status_as_owner_recruiter_success(
    client, create_user, session
):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C10", email="c10-status@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R10", email="r10-status@example.com",
        job_payload={
            "title": "Job Status",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        
        login = client.post(
            "/auth/login",
            data={
                "username": cand_user["request"]["email"],
                "password": cand_user["request"]["password"],
            },
        )
        cand_token = login.json()["access_token"]
        _set_auth(client, cand_token)
        apply = client.post(f"/applications/{job['id']}")
        assert apply.status_code == 200, apply.text
        application_id = apply.json()["id"]

        # Recruiter updates status
        login2 = client.post(
            "/auth/login",
            data={
                "username": rec_user["request"]["email"],
                "password": rec_user["request"]["password"],
            },
        )
        rec_token = login2.json()["access_token"]
        _set_auth(client, rec_token)

        response = client.put(
            f"/applications/{application_id}/status",
            json={"status": "Shortlisted"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == application_id
        assert body["status"] == "Shortlisted"

        db_app = (
            session.query(Application)
            .filter(Application.id == application_id)
            .first()
        )
        assert db_app.status == "Shortlisted"
    finally:
        _restore_auth(client, rec_orig)


def test_update_application_status_as_other_recruiter_forbidden(
    client, create_user
):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C11", email="c11-other-status@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R11a", email="r11a-other-status@example.com",
        job_payload={
            "title": "Job OtherStatus",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    other = create_user(
        name="R11b",
        email="r11b-other-status@example.com",
        password="otherpass",
        role="recruiter",
    )
    try:
        # Candidate applies
        login = client.post(
            "/auth/login",
            data={
                "username": cand_user["request"]["email"],
                "password": cand_user["request"]["password"],
            },
        )
        cand_token = login.json()["access_token"]
        _set_auth(client, cand_token)
        apply = client.post(f"/applications/{job['id']}")
        application_id = apply.json()["id"]

        # Other recruiter attempts update
        login2 = client.post(
            "/auth/login",
            data={
                "username": other["request"]["email"],
                "password": other["request"]["password"],
            },
        )
        other_token = login2.json()["access_token"]
        _set_auth(client, other_token)

        response = client.put(
            f"/applications/{application_id}/status",
            json={"status": "Shortlisted"},
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You can only update applicants for your own jobs."
        )
    finally:
        _restore_auth(client, rec_orig)


def test_update_application_status_as_candidate_forbidden(
    client, create_user
):
    cand_user, profile, cand_orig = _make_candidate_with_profile(
        client, create_user,
        name="C12", email="c12-cand-status@example.com",
    )
    rec_user, job, rec_orig = _make_recruiter_with_job(
        client, create_user,
        name="R12", email="r12-cand-status@example.com",
        job_payload={
            "title": "Job CandStatus",
            "description": "x",
            "location": "Remote",
            "min_salary": 1,
            "max_salary": 2,
        },
    )
    try:
        # Apply as candidate
        login = client.post(
            "/auth/login",
            data={
                "username": cand_user["request"]["email"],
                "password": cand_user["request"]["password"],
            },
        )
        cand_token = login.json()["access_token"]
        _set_auth(client, cand_token)
        apply = client.post(f"/applications/{job['id']}")
        application_id = apply.json()["id"]

        # Candidate attempts to update own application's status
        response = client.put(
            f"/applications/{application_id}/status",
            json={"status": "Shortlisted"},
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "Only recruiters can update application status."
        )
    finally:
        _restore_auth(client, rec_orig)


def test_update_application_status_not_found_returns_404(
    authorized_recruiter_client
):
    response = authorized_recruiter_client.put(
        "/applications/99999/status",
        json={"status": "Shortlisted"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found."
