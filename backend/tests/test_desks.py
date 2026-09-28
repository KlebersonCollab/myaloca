import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient, email: str, role: str) -> str:
    reg_payload = {
        "email": email,
        "full_name": f"User {role}",
        "password": "password123",
        "role": role,
    }
    await client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"},
    )
    return login_res.json()["access_token"]


@pytest.mark.asyncio
async def test_create_zone_and_desk_success(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_desk@myaloca.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create Zone
    zone_payload = {
        "name": "Andar 2 - Engenharia & Produto",
        "floor": 2,
        "description": "Ala de tecnologia e desenvolvimento",
    }
    zone_res = await client.post("/api/v1/zones", json=zone_payload, headers=headers)
    assert zone_res.status_code == 201
    zone = zone_res.json()
    assert zone["name"] == zone_payload["name"]
    zone_id = zone["id"]

    # 2. Create Desk with 3D coordinates
    desk_payload = {
        "code": "BAIA-ENG-01",
        "zone_id": zone_id,
        "pos_x": 12.5,
        "pos_y": 0.0,
        "pos_z": -4.2,
        "rotation_y": 90.0,
        "has_monitor": True,
        "has_docking_station": True,
    }
    desk_res = await client.post("/api/v1/desks", json=desk_payload, headers=headers)
    assert desk_res.status_code == 201
    desk = desk_res.json()
    assert desk["code"] == "BAIA-ENG-01"
    assert desk["pos_x"] == 12.5
    assert desk["status"] == "DISPONIVEL"
    assert len(desk["qr_code_hash"]) > 20  # Cryptographic immutable token


@pytest.mark.asyncio
async def test_colaborador_forbidden_from_creating_desk(client: AsyncClient):
    user_token = await get_auth_token(client, "colab_desk@myaloca.com", "colaborador")
    headers = {"Authorization": f"Bearer {user_token}"}

    desk_payload = {
        "code": "BAIA-HACK",
        "zone_id": 1,
        "pos_x": 0.0,
        "pos_y": 0.0,
        "pos_z": 0.0,
    }
    res = await client.post("/api/v1/desks", json=desk_payload, headers=headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_get_desk_qr_code_png(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_qr@myaloca.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create Zone
    zone_res = await client.post(
        "/api/v1/zones",
        json={"name": "Zona Central", "floor": 1},
        headers=headers,
    )
    zone_id = zone_res.json()["id"]

    # Create Desk
    desk_res = await client.post(
        "/api/v1/desks",
        json={"code": "BAIA-QR-TEST", "zone_id": zone_id, "pos_x": 1.0, "pos_y": 0.0, "pos_z": 1.0},
        headers=headers,
    )
    desk_id = desk_res.json()["id"]

    # Fetch QR Code Image
    qr_res = await client.get(f"/api/v1/desks/{desk_id}/qrcode", headers=headers)
    assert qr_res.status_code == 200
    assert qr_res.headers["content-type"] == "image/png"
    assert len(qr_res.content) > 100
