from datetime import datetime, timedelta, timezone

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


@pytest.mark.asyncio
async def test_batch_create_desks_and_floor_filter(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_batch@myaloca.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create Zone on Floor 3
    zone_res = await client.post(
        "/api/v1/zones",
        json={
            "name": "3º Andar - Inovação",
            "floor": 3,
            "description": "Lab de Inteligência Artificial",
        },
        headers=headers,
    )
    assert zone_res.status_code == 201
    zone_id = zone_res.json()["id"]

    # 2. Create Batch of 4 Desks
    batch_payload = [
        {
            "code": f"AI-0{i}",
            "zone_id": zone_id,
            "pos_x": (i - 2.5) * 2.2,
            "pos_y": 0.0,
            "pos_z": 0.0,
            "rotation_y": 0.0,
            "has_monitor": True,
            "has_docking_station": True,
        }
        for i in range(1, 5)
    ]
    batch_res = await client.post("/api/v1/desks/batch", json=batch_payload, headers=headers)
    assert batch_res.status_code == 201
    desks = batch_res.json()
    assert len(desks) == 4
    assert {d["code"] for d in desks} == {"AI-01", "AI-02", "AI-03", "AI-04"}

    # 3. Filter Desks by Floor 3
    floor_desks_res = await client.get("/api/v1/desks?floor=3", headers=headers)
    assert floor_desks_res.status_code == 200
    floor_desks = floor_desks_res.json()
    assert len(floor_desks) >= 4
    for d in floor_desks:
        assert d["zone_id"] == zone_id

    # 4. Filter Zones by Floor 3
    floor_zones_res = await client.get("/api/v1/zones?floor=3", headers=headers)
    assert floor_zones_res.status_code == 200
    floor_zones = floor_zones_res.json()
    assert len(floor_zones) >= 1
    assert all(z["floor"] == 3 for z in floor_zones)

    # 5. Filter 3D Office by Floor 3
    office_3d_res = await client.get("/api/v1/bookings/3d-office?floor=3", headers=headers)
    assert office_3d_res.status_code == 200
    office_desks = office_3d_res.json()
    assert len(office_desks) >= 4


@pytest.mark.asyncio
async def test_delete_desk_success(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_del@myaloca.com", "admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create Zone and Desk
    z_res = await client.post(
        "/api/v1/zones",
        json={"name": "Zona Deleção", "floor": 1},
        headers=admin_headers,
    )
    zone_id = z_res.json()["id"]

    d_res = await client.post(
        "/api/v1/desks",
        json={
            "code": "BAIA-TO-DELETE",
            "zone_id": zone_id,
            "pos_x": 0.0,
            "pos_y": 0.0,
            "pos_z": 0.0,
        },
        headers=admin_headers,
    )
    desk_id = d_res.json()["id"]

    # 2. Delete Desk -> Should succeed
    del_res = await client.delete(f"/api/v1/desks/{desk_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["code"] == "DESK_DELETED"

    # 3. Verify desk no longer exists
    get_res = await client.get(f"/api/v1/desks/{desk_id}", headers=admin_headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_delete_desk_forbidden_for_colaborador(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_del2@myaloca.com", "admin")
    colab_token = await get_auth_token(client, "colab_del@myaloca.com", "colaborador")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    colab_headers = {"Authorization": f"Bearer {colab_token}"}

    z_res = await client.post(
        "/api/v1/zones",
        json={"name": "Zona Protegida", "floor": 1},
        headers=admin_headers,
    )
    zone_id = z_res.json()["id"]

    d_res = await client.post(
        "/api/v1/desks",
        json={"code": "BAIA-SECURE", "zone_id": zone_id, "pos_x": 0.0, "pos_y": 0.0, "pos_z": 0.0},
        headers=admin_headers,
    )
    desk_id = d_res.json()["id"]

    # Colaborador attempts deletion -> 403 Forbidden
    del_res = await client.delete(f"/api/v1/desks/{desk_id}", headers=colab_headers)
    assert del_res.status_code == 403
    assert del_res.json()["detail"]["code"] == "PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_delete_desk_with_active_booking_rejected(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_del3@myaloca.com", "admin")
    colab_token = await get_auth_token(client, "colab_del3@myaloca.com", "colaborador")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    colab_headers = {"Authorization": f"Bearer {colab_token}"}

    z_res = await client.post(
        "/api/v1/zones",
        json={"name": "Zona Com Reserva", "floor": 2},
        headers=admin_headers,
    )
    zone_id = z_res.json()["id"]

    d_res = await client.post(
        "/api/v1/desks",
        json={
            "code": "BAIA-ACTIVE-BOOKING",
            "zone_id": zone_id,
            "pos_x": 0.0,
            "pos_y": 0.0,
            "pos_z": 0.0,
        },
        headers=admin_headers,
    )
    desk_id = d_res.json()["id"]

    # Create active booking
    now = datetime.now(timezone.utc)
    book_res = await client.post(
        "/api/v1/bookings",
        json={
            "desk_id": desk_id,
            "start_time": (now + timedelta(hours=1)).isoformat(),
            "end_time": (now + timedelta(hours=4)).isoformat(),
        },
        headers=colab_headers,
    )
    assert book_res.status_code == 201
    booking_id = book_res.json()["id"]

    # 1. Admin tries to delete desk with active booking -> 400 Bad Request
    del_res = await client.delete(f"/api/v1/desks/{desk_id}", headers=admin_headers)
    assert del_res.status_code == 400
    assert del_res.json()["detail"]["code"] == "ACTIVE_BOOKINGS_EXIST"

    # 2. User cancels booking
    cancel_res = await client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=colab_headers)
    assert cancel_res.status_code == 200

    # 3. Now deletion succeeds
    del_ok = await client.delete(f"/api/v1/desks/{desk_id}", headers=admin_headers)
    assert del_ok.status_code == 200
    assert del_ok.json()["code"] == "DESK_DELETED"


@pytest.mark.asyncio
async def test_admin_release_desk_with_active_booking(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_rel@myaloca.com", "admin")
    colab_token = await get_auth_token(client, "colab_rel@myaloca.com", "colaborador")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    colab_headers = {"Authorization": f"Bearer {colab_token}"}

    z_res = await client.post(
        "/api/v1/zones",
        json={"name": "Zona Release Test", "floor": 1},
        headers=admin_headers,
    )
    zone_id = z_res.json()["id"]

    d_res = await client.post(
        "/api/v1/desks",
        json={
            "code": "BAIA-ADMIN-RELEASE",
            "zone_id": zone_id,
            "pos_x": 0.0,
            "pos_y": 0.0,
            "pos_z": 0.0,
        },
        headers=admin_headers,
    )
    desk_id = d_res.json()["id"]

    # Colaborador creates booking
    now = datetime.now(timezone.utc)
    b_res = await client.post(
        "/api/v1/bookings",
        json={
            "desk_id": desk_id,
            "start_time": (now - timedelta(minutes=5)).isoformat(),
            "end_time": (now + timedelta(hours=4)).isoformat(),
        },
        headers=colab_headers,
    )
    assert b_res.status_code == 201

    # Admin administratively releases the desk
    rel_res = await client.post(f"/api/v1/desks/{desk_id}/release", headers=admin_headers)
    assert rel_res.status_code == 200
    assert rel_res.json()["status"] == "DISPONIVEL"

    # Now another collaborator can book the same desk immediately without overlap error
    colab2_token = await get_auth_token(client, "colab2_rel@myaloca.com", "colaborador")
    colab2_headers = {"Authorization": f"Bearer {colab2_token}"}
    rebook_res = await client.post(
        "/api/v1/bookings",
        json={
            "desk_id": desk_id,
            "start_time": (now + timedelta(hours=1)).isoformat(),
            "end_time": (now + timedelta(hours=3)).isoformat(),
        },
        headers=colab2_headers,
    )
    assert rebook_res.status_code == 201


@pytest.mark.asyncio
async def test_colaborador_forbidden_from_releasing_desk(client: AsyncClient):
    colab_token = await get_auth_token(client, "colab_rel_forbid@myaloca.com", "colaborador")
    colab_headers = {"Authorization": f"Bearer {colab_token}"}

    forbidden_res = await client.post("/api/v1/desks/1/release", headers=colab_headers)
    assert forbidden_res.status_code == 403


@pytest.mark.asyncio
async def test_create_and_update_zone_grid_dimensions(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_grid@myaloca.com", "admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create zone with custom grid dimensions
    create_res = await client.post(
        "/api/v1/zones",
        json={
            "name": "Zona Custom Grid 8x5",
            "floor": 4,
            "description": "Pavimento com particionamento flexivel",
            "grid_cols": 8,
            "grid_rows": 5,
        },
        headers=admin_headers,
    )
    assert create_res.status_code == 201
    zone_data = create_res.json()
    assert zone_data["grid_cols"] == 8
    assert zone_data["grid_rows"] == 5
    zone_id = zone_data["id"]

    # 2. Update grid dimensions
    update_res = await client.put(
        f"/api/v1/zones/{zone_id}",
        json={"grid_cols": 12, "grid_rows": 6},
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["grid_cols"] == 12
    assert updated_data["grid_rows"] == 6

    # 3. Fetch zone and verify persistence
    get_res = await client.get(f"/api/v1/zones/{zone_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["grid_cols"] == 12
    assert get_res.json()["grid_rows"] == 6


@pytest.mark.asyncio
async def test_desk_equipment_editing_and_repositioning(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_equip@myaloca.com", "admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Create Zone
    z_res = await client.post(
        "/api/v1/zones",
        json={"name": "Zona Equipamentos", "floor": 1, "grid_cols": 8, "grid_rows": 4},
        headers=admin_headers,
    )
    zone_id = z_res.json()["id"]

    # 1. Create desk with 2 monitors, docking station and extra equipment
    d_res = await client.post(
        "/api/v1/desks",
        json={
            "code": "DESK-EQ-01",
            "zone_id": zone_id,
            "pos_x": 0.0,
            "pos_y": 0.0,
            "pos_z": 0.0,
            "monitors_count": 2,
            "has_docking_station": True,
            "is_standing_desk": True,
            "extra_equipment": "Câmera 4K & Headset ANC",
        },
        headers=admin_headers,
    )
    assert d_res.status_code == 201
    desk_data = d_res.json()
    assert desk_data["monitors_count"] == 2
    assert desk_data["has_monitor"] is True
    assert desk_data["has_docking_station"] is True
    assert desk_data["is_standing_desk"] is True
    assert desk_data["extra_equipment"] == "Câmera 4K & Headset ANC"
    desk_id = desk_data["id"]

    # 2. Reposition desk via Drag & Drop coordinates and edit equipment to 1 monitor
    up_res = await client.put(
        f"/api/v1/desks/{desk_id}",
        json={
            "pos_x": 4.8,
            "pos_z": -1.2,
            "monitors_count": 1,
            "extra_equipment": "Monitor Ultrawide 34",
        },
        headers=admin_headers,
    )
    assert up_res.status_code == 200
    updated = up_res.json()
    assert updated["pos_x"] == 4.8
    assert updated["pos_z"] == -1.2
    assert updated["monitors_count"] == 1
    assert updated["has_monitor"] is True
    assert updated["extra_equipment"] == "Monitor Ultrawide 34"

    # 3. Change to 0 monitors
    zero_res = await client.put(
        f"/api/v1/desks/{desk_id}",
        json={"monitors_count": 0},
        headers=admin_headers,
    )
    assert zero_res.status_code == 200
    assert zero_res.json()["monitors_count"] == 0
    assert zero_res.json()["has_monitor"] is False





