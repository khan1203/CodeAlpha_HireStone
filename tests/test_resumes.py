from tests.conftest import auth_headers


def test_upload_resume(client, candidate_token):
    r = client.post(
        "/resumes",
        files={"file": ("cv.pdf", b"%PDF-1.4 content", "application/pdf")},
        headers=auth_headers(candidate_token),
    )
    assert r.status_code == 201
    body = r.json()
    assert body["filename"] == "cv.pdf"
    assert body["is_primary"] is True


def test_upload_rejects_bad_extension(client, candidate_token):
    r = client.post(
        "/resumes",
        files={"file": ("virus.exe", b"MZ...", "application/octet-stream")},
        headers=auth_headers(candidate_token),
    )
    assert r.status_code == 400


def test_second_resume_not_primary_by_default(client, candidate_token, uploaded_resume):
    r = client.post(
        "/resumes",
        files={"file": ("cv2.pdf", b"%PDF-1.4 v2", "application/pdf")},
        headers=auth_headers(candidate_token),
    )
    assert r.status_code == 201
    assert r.json()["is_primary"] is False


def test_set_primary_resume(client, candidate_token, uploaded_resume):
    r2 = client.post(
        "/resumes",
        files={"file": ("cv2.pdf", b"%PDF-1.4 v2", "application/pdf")},
        headers=auth_headers(candidate_token),
    )
    second_id = r2.json()["id"]

    r = client.patch(f"/resumes/{second_id}/primary", headers=auth_headers(candidate_token))
    assert r.status_code == 200
    assert r.json()["is_primary"] is True

    r = client.get("/resumes", headers=auth_headers(candidate_token))
    primaries = [res for res in r.json() if res["is_primary"]]
    assert len(primaries) == 1
    assert primaries[0]["id"] == second_id


def test_delete_resume(client, candidate_token, uploaded_resume):
    resume_id = uploaded_resume["id"]
    r = client.delete(f"/resumes/{resume_id}", headers=auth_headers(candidate_token))
    assert r.status_code == 204

    r = client.get("/resumes", headers=auth_headers(candidate_token))
    assert r.json() == []


def test_employer_cannot_upload_resume(client, employer_token):
    r = client.post(
        "/resumes",
        files={"file": ("cv.pdf", b"%PDF-1.4", "application/pdf")},
        headers=auth_headers(employer_token),
    )
    assert r.status_code == 403
