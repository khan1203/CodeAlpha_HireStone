from tests.conftest import auth_headers, register_candidate, register_employer


def test_apply_to_job(client, candidate_token, posted_job, uploaded_resume):
    r = client.post(
        "/applications",
        json={"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]},
        headers=auth_headers(candidate_token),
    )
    assert r.status_code == 201
    assert r.json()["status"] == "applied"


def test_duplicate_application_rejected(client, candidate_token, posted_job, uploaded_resume):
    payload = {"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]}
    client.post("/applications", json=payload, headers=auth_headers(candidate_token))
    r = client.post("/applications", json=payload, headers=auth_headers(candidate_token))
    assert r.status_code == 400


def test_apply_to_closed_job_rejected(client, employer_token, candidate_token, posted_job, uploaded_resume):
    job_id = posted_job["id"]
    client.patch(f"/jobs/{job_id}", json={"status": "closed"}, headers=auth_headers(employer_token))
    r = client.post(
        "/applications",
        json={"job_id": job_id, "resume_id": uploaded_resume["id"]},
        headers=auth_headers(candidate_token),
    )
    assert r.status_code == 404


def test_apply_with_others_resume_rejected(client, candidate_token, posted_job, uploaded_resume):
    other_token = register_candidate(client, email="c2@test.com", full_name="Other Candidate")
    r = client.post(
        "/applications",
        json={"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]},
        headers=auth_headers(other_token),
    )
    assert r.status_code == 404


def test_employer_views_applications_for_own_job(client, employer_token, candidate_token, posted_job, uploaded_resume):
    client.post(
        "/applications",
        json={"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]},
        headers=auth_headers(candidate_token),
    )
    r = client.get(f"/applications/job/{posted_job['id']}", headers=auth_headers(employer_token))
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_other_employer_cannot_view_applications(client, posted_job, candidate_token, uploaded_resume):
    client.post(
        "/applications",
        json={"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]},
        headers=auth_headers(candidate_token),
    )
    other_token = register_employer(client, email="other-emp@test.com", company="Other Co")
    r = client.get(f"/applications/job/{posted_job['id']}", headers=auth_headers(other_token))
    assert r.status_code == 403


def test_status_update_flow(client, employer_token, candidate_token, posted_job, uploaded_resume):
    r = client.post(
        "/applications",
        json={"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]},
        headers=auth_headers(candidate_token),
    )
    app_id = r.json()["id"]

    for new_status in ["reviewed", "interview", "hired"]:
        r = client.patch(
            f"/applications/{app_id}/status",
            json={"status": new_status},
            headers=auth_headers(employer_token),
        )
        assert r.status_code == 200
        assert r.json()["status"] == new_status


def test_candidate_cannot_update_status(client, candidate_token, posted_job, uploaded_resume):
    r = client.post(
        "/applications",
        json={"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]},
        headers=auth_headers(candidate_token),
    )
    app_id = r.json()["id"]
    r = client.patch(
        f"/applications/{app_id}/status",
        json={"status": "hired"},
        headers=auth_headers(candidate_token),
    )
    assert r.status_code == 403


def test_my_applications_list(client, candidate_token, posted_job, uploaded_resume):
    client.post(
        "/applications",
        json={"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]},
        headers=auth_headers(candidate_token),
    )
    r = client.get("/applications/mine", headers=auth_headers(candidate_token))
    assert r.status_code == 200
    assert len(r.json()) == 1
