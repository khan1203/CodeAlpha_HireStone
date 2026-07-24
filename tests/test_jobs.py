from tests.conftest import auth_headers


def test_post_job(client, employer_token):
    r = client.post(
        "/jobs",
        json={"title": "Data Scientist", "description": "ML work", "location": "NYC"},
        headers=auth_headers(employer_token),
    )
    assert r.status_code == 201
    assert r.json()["title"] == "Data Scientist"
    assert r.json()["status"] == "open"


def test_candidate_cannot_post_job(client, candidate_token):
    r = client.post(
        "/jobs",
        json={"title": "x", "description": "y"},
        headers=auth_headers(candidate_token),
    )
    assert r.status_code == 403


def test_search_by_keyword(client, posted_job):
    r = client.get("/jobs/search", params={"q": "Backend"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Backend Engineer"


def test_search_no_match(client, posted_job):
    r = client.get("/jobs/search", params={"q": "Nonexistent Role"})
    assert r.json()["total"] == 0


def test_search_by_remote_flag(client, posted_job):
    r = client.get("/jobs/search", params={"remote": True})
    assert r.json()["total"] == 1

    r = client.get("/jobs/search", params={"remote": False})
    assert r.json()["total"] == 0


def test_search_pagination(client, employer_token):
    for i in range(5):
        client.post(
            "/jobs",
            json={"title": f"Job {i}", "description": "desc"},
            headers=auth_headers(employer_token),
        )
    r = client.get("/jobs/search", params={"page": 1, "page_size": 2})
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2


def test_closed_jobs_excluded_from_search(client, employer_token, posted_job):
    job_id = posted_job["id"]
    client.patch(f"/jobs/{job_id}", json={"status": "closed"}, headers=auth_headers(employer_token))
    r = client.get("/jobs/search", params={"q": "Backend"})
    assert r.json()["total"] == 0


def test_other_employer_cannot_edit_job(client, posted_job):
    from tests.conftest import register_employer

    other_token = register_employer(client, email="other@test.com", company="Other Co")
    job_id = posted_job["id"]
    r = client.patch(f"/jobs/{job_id}", json={"title": "Hijacked"}, headers=auth_headers(other_token))
    assert r.status_code == 403


def test_get_job_not_found(client):
    r = client.get("/jobs/999999")
    assert r.status_code == 404
