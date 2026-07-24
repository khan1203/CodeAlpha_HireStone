from tests.conftest import auth_headers, register_employer, register_candidate


def test_register_and_login_employer(client):
    token = register_employer(client, email="e1@test.com")
    assert token

    r = client.post("/auth/login", data={"username": "e1@test.com", "password": "password123"})
    assert r.status_code == 200
    assert r.json()["role"] == "employer"


def test_register_and_login_candidate(client):
    register_candidate(client, email="c1@test.com")

    r = client.post("/auth/login", data={"username": "c1@test.com", "password": "password123"})
    assert r.status_code == 200
    assert r.json()["role"] == "candidate"


def test_duplicate_email_rejected(client):
    register_employer(client, email="dup@test.com")
    r = client.post(
        "/auth/register/employer",
        json={"email": "dup@test.com", "password": "password123", "company_name": "Other Co"},
    )
    assert r.status_code == 400


def test_wrong_password_rejected(client):
    register_employer(client, email="e2@test.com")
    r = client.post("/auth/login", data={"username": "e2@test.com", "password": "wrongpass"})
    assert r.status_code == 401


def test_unauthenticated_request_rejected(client):
    r = client.get("/employers/me")
    assert r.status_code == 401


def test_employer_profile_get_update(client, employer_token):
    r = client.get("/employers/me", headers=auth_headers(employer_token))
    assert r.status_code == 200
    assert r.json()["company_name"] == "Acme Inc"

    r = client.patch(
        "/employers/me",
        json={"description": "We build things"},
        headers=auth_headers(employer_token),
    )
    assert r.status_code == 200
    assert r.json()["description"] == "We build things"


def test_candidate_profile_get_update(client, candidate_token):
    r = client.get("/candidates/me", headers=auth_headers(candidate_token))
    assert r.status_code == 200
    assert r.json()["full_name"] == "Jane Doe"

    r = client.patch("/candidates/me", json={"headline": "Senior Dev"}, headers=auth_headers(candidate_token))
    assert r.status_code == 200
    assert r.json()["headline"] == "Senior Dev"
