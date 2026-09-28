import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    payload = {
        "email": "colaborador@myaloca.com",
        "full_name": "Ana Silva",
        "password": "strongpassword123",
        "role": "colaborador",
        "job_title": "Product Designer",
        "department": "Design",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=Ana",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert data["role"] == "colaborador"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "email": "dupe@myaloca.com",
        "full_name": "Dupe User",
        "password": "secretpassword",
        "role": "colaborador",
    }
    r1 = await client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409
    assert r2.json()["detail"]["code"] == "EMAIL_ALREADY_REGISTERED"


@pytest.mark.asyncio
async def test_login_and_get_me(client: AsyncClient):
    # Register
    reg_payload = {
        "email": "gestor@myaloca.com",
        "full_name": "Carlos Gestor",
        "password": "adminpassword123",
        "role": "admin",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # Login
    login_payload = {
        "username": "gestor@myaloca.com",
        "password": "adminpassword123",
    }
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # Get /me
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "gestor@myaloca.com"
    assert me_data["role"] == "admin"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    reg_payload = {
        "email": "user2@myaloca.com",
        "full_name": "User Two",
        "password": "correct_password",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "user2@myaloca.com", "password": "wrong_password"},
    )
    assert login_res.status_code == 401
    assert login_res.json()["detail"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
