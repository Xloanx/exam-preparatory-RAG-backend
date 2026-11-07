import uuid

import httpx
from httpx import AsyncClient


def _unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@example.com"


async def _register_and_token(client: AsyncClient, prefix: str):
    email = _unique_email(prefix)
    password = "Passw0rd!"
    r = await client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "Test User"})
    assert r.status_code == 201
    body = r.json()
    token = body["access_token"]
    return email, token


async def test_health(client: AsyncClient) -> None:
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_auth_register_login_me(client: AsyncClient) -> None:
    email, token = await _register_and_token(client, "phase1user")

    r = await client.post("/api/v1/auth/login", json={"email": email, "password": "Passw0rd!"})
    assert r.status_code == 200
    assert r.json()["access_token"]

    r = await client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPass1!"})
    assert r.status_code == 401

    r = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["user"]["email"] == email

    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401


async def test_auth_register_duplicate_email_conflict(client: AsyncClient) -> None:
    email, _ = await _register_and_token(client, "phase1dup")
    r = await client.post("/api/v1/auth/register", json={"email": email, "password": "Passw0rd!"})
    assert r.status_code == 409


async def test_user_category_change_unknown_category(client: AsyncClient) -> None:
    _, token = await _register_and_token(client, "phase1cat")
    r = await client.put(
        "/api/v1/users/me/category",
        json={"category_id": 999999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


async def test_exam_session_requires_auth(client: AsyncClient) -> None:
    r = await client.post("/api/v1/exams/sessions", json={"scopes": ["GENERAL"], "question_count": 10})
    assert r.status_code == 401


async def test_exam_session_general_scope(client: AsyncClient) -> None:
    _, token = await _register_and_token(client, "phase1exam")
    r = await client.post(
        "/api/v1/exams/sessions",
        json={"scopes": ["GENERAL"], "question_count": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "attempt_id" in body
    assert body["questions"] == []


async def test_exam_session_specific_scope_requires_category(client: AsyncClient) -> None:
    _, token = await _register_and_token(client, "phase1exam2")
    r = await client.post(
        "/api/v1/exams/sessions",
        json={"scopes": ["CAT_1"], "question_count": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


async def test_admin_endpoints_require_admin(client: AsyncClient) -> None:
    r = await client.get("/api/v1/admin/categories")
    assert r.status_code == 401

    r = await client.post("/api/v1/admin/categories", json={"name": "Phase One Category"})
    assert r.status_code == 401
