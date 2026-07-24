from tests.conftest import auth_headers


def _make_admin_token(client, email="admin@test.com"):
    """No public admin-registration endpoint by design; promote via DB directly,
    mirroring what app/scripts/create_admin.py does, then log in for a token."""
    from app.database import get_db
    from app.models.user import User, UserRole
    from app.security import hash_password

    override = client.app.dependency_overrides[get_db]
    db = next(override())
    user = User(email=email, hashed_password=hash_password("adminpass123"), role=UserRole.ADMIN)
    db.add(user)
    db.commit()
    db.close()

    r = client.post("/auth/login", data={"username": email, "password": "adminpass123"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_non_admin_cannot_reach_admin_routes(client, employer_token, candidate_token):
    r = client.get("/admin/stats", headers=auth_headers(employer_token))
    assert r.status_code == 403
    r = client.get("/admin/stats", headers=auth_headers(candidate_token))
    assert r.status_code == 403


def test_admin_can_list_users(client, employer_token, candidate_token):
    admin_token = _make_admin_token(client)
    r = client.get("/admin/users", headers=auth_headers(admin_token))
    assert r.status_code == 200
    emails = {u["email"] for u in r.json()}
    assert "employer@test.com" in emails
    assert "candidate@test.com" in emails


def test_admin_can_deactivate_and_reactivate_user(client, employer_token):
    admin_token = _make_admin_token(client)

    r = client.get("/admin/users", headers=auth_headers(admin_token))
    target = next(u for u in r.json() if u["email"] == "employer@test.com")

    r = client.patch(f"/admin/users/{target['id']}/deactivate", headers=auth_headers(admin_token))
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    # deactivated user can no longer authenticate
    r = client.post("/auth/login", data={"username": "employer@test.com", "password": "password123"})
    assert r.status_code == 403

    r = client.patch(f"/admin/users/{target['id']}/activate", headers=auth_headers(admin_token))
    assert r.status_code == 200
    assert r.json()["is_active"] is True

    r = client.post("/auth/login", data={"username": "employer@test.com", "password": "password123"})
    assert r.status_code == 200


def test_application_stats(client, employer_token, candidate_token, posted_job, uploaded_resume):
    admin_token = _make_admin_token(client)

    r = client.post(
        "/applications",
        json={"job_id": posted_job["id"], "resume_id": uploaded_resume["id"]},
        headers=auth_headers(candidate_token),
    )
    app_id = r.json()["id"]
    client.patch(f"/applications/{app_id}/status", json={"status": "reviewed"}, headers=auth_headers(employer_token))

    r = client.get("/admin/stats", headers=auth_headers(admin_token))
    assert r.status_code == 200
    body = r.json()
    assert body["total_applications"] == 1
    assert body["by_status"]["reviewed"] == 1
    assert body["by_status"]["applied"] == 0
    assert body["total_jobs"] == 1
    assert body["open_jobs"] == 1
    assert body["total_employers"] == 1
    assert body["total_candidates"] == 1
