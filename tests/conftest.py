import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("SECRET_KEY", "test-secret")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Fresh SQLite DB + app instance per test, via dependency override."""
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from app.database import Base, get_db
    from app import models  # noqa: F401 registers tables on Base.metadata
    from app.main import app

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def register_employer(client, email="employer@test.com", company="Acme Inc"):
    r = client.post(
        "/auth/register/employer",
        json={"email": email, "password": "password123", "company_name": company},
    )
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def register_candidate(client, email="candidate@test.com", full_name="Jane Doe"):
    r = client.post(
        "/auth/register/candidate",
        json={"email": email, "password": "password123", "full_name": full_name},
    )
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def employer_token(client):
    return register_employer(client)


@pytest.fixture()
def candidate_token(client):
    return register_candidate(client)


@pytest.fixture()
def posted_job(client, employer_token):
    r = client.post(
        "/jobs",
        json={"title": "Backend Engineer", "description": "Build APIs", "location": "Remote", "remote": True},
        headers=auth_headers(employer_token),
    )
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def uploaded_resume(client, candidate_token):
    r = client.post(
        "/resumes",
        files={"file": ("resume.pdf", b"%PDF-1.4 fake resume content", "application/pdf")},
        headers=auth_headers(candidate_token),
    )
    assert r.status_code == 201, r.text
    return r.json()
