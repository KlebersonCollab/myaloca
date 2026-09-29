from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.booking_service import BookingService


async def setup_test_desk(
    client: AsyncClient, code: str = "BAIA-BK-01"
) -> tuple[str, str, int, str]:
    # Register Admin & Colaborador
    reg_admin = {
        "email": f"admin_{code}@myaloca.com",
        "full_name": "Admin User",
        "password": "password123",
        "role": "admin",
    }
    await client.post("/api/v1/auth/register", json=reg_admin)
    login_adm = await client.post(
        "/api/v1/auth/login",
        data={"username": reg_admin["email"], "password": "password123"},
    )
    admin_token = login_adm.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    reg_colab = {
        "email": f"user_{code}@myaloca.com",
        "full_name": "Colab User",
        "password": "password123",
        "role": "colaborador",
    }
    await client.post("/api/v1/auth/register", json=reg_colab)
    login_colab = await client.post(
        "/api/v1/auth/login",
        data={"username": reg_colab["email"], "password": "password123"},
    )
    user_token = login_colab.json()["access_token"]

    # Create Zone & Desk
    z_res = await client.post(
        "/api/v1/zones",
        json={"name": f"Zona {code}", "floor": 1},
        headers=admin_headers,
    )
    zone_id = z_res.json()["id"]

    d_res = await client.post(
        "/api/v1/desks",
        json={"code": code, "zone_id": zone_id, "pos_x": 0.0, "pos_y": 0.0, "pos_z": 0.0},
        headers=admin_headers,
    )
    desk = d_res.json()
    return admin_token, user_token, desk["id"], desk["qr_code_hash"]


@pytest.mark.asyncio
async def test_create_booking_success(client: AsyncClient):
    _, user_token, desk_id, _ = await setup_test_desk(client, "BAIA-BK-101")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    now = datetime.now(timezone.utc)
    start_time = now + timedelta(hours=2)
    end_time = start_time + timedelta(hours=6)

    payload = {
        "desk_id": desk_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }
    response = await client.post("/api/v1/bookings", json=payload, headers=user_headers)
    assert response.status_code == 201
    booking = response.json()
    assert booking["desk_id"] == desk_id
    assert booking["status"] == "PENDENTE_CHECKIN"
    assert "checkin_deadline" in booking


@pytest.mark.asyncio
async def test_booking_time_overlap_conflict(client: AsyncClient):
    _, user1_token, desk_id, _ = await setup_test_desk(client, "BAIA-BK-OVERLAP")
    user1_headers = {"Authorization": f"Bearer {user1_token}"}

    # Register second user
    reg2_payload = {
        "email": "user2_bk@myaloca.com",
        "full_name": "User 2",
        "password": "pwd",
        "role": "colaborador",
    }
    await client.post("/api/v1/auth/register", json=reg2_payload)
    login2 = await client.post(
        "/api/v1/auth/login", data={"username": "user2_bk@myaloca.com", "password": "pwd"}
    )
    user2_token = login2.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    base = datetime.now(timezone.utc) + timedelta(days=1)
    # Booking 1: 10:00 to 14:00
    b1_payload = {
        "desk_id": desk_id,
        "start_time": (base.replace(hour=10, minute=0, second=0)).isoformat(),
        "end_time": (base.replace(hour=14, minute=0, second=0)).isoformat(),
    }
    res1 = await client.post("/api/v1/bookings", json=b1_payload, headers=user1_headers)
    assert res1.status_code == 201

    # Booking 2: 12:00 to 16:00 (overlaps with Booking 1)
    b2_payload = {
        "desk_id": desk_id,
        "start_time": (base.replace(hour=12, minute=0, second=0)).isoformat(),
        "end_time": (base.replace(hour=16, minute=0, second=0)).isoformat(),
    }
    res2 = await client.post("/api/v1/bookings", json=b2_payload, headers=user2_headers)
    assert res2.status_code == 409
    assert res2.json()["detail"]["code"] == "BOOKING_OVERLAP"


@pytest.mark.asyncio
async def test_qr_checkin_success_and_invalid_hash(client: AsyncClient):
    _, user_token, desk_id, qr_hash = await setup_test_desk(client, "BAIA-BK-CHECKIN")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Create a booking valid around now
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=5)
    end_time = now + timedelta(hours=4)

    payload = {
        "desk_id": desk_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }
    b_res = await client.post("/api/v1/bookings", json=payload, headers=user_headers)
    assert b_res.status_code == 201
    booking_id = b_res.json()["id"]

    # 1. Invalid QR Hash check-in
    bad_checkin = await client.post(
        f"/api/v1/bookings/{booking_id}/checkin",
        json={"qr_code_hash": "wrong_invalid_hash_123"},
        headers=user_headers,
    )
    assert bad_checkin.status_code == 400
    assert bad_checkin.json()["detail"]["code"] == "INVALID_QR_CODE"

    # 2. Valid QR Hash check-in
    good_checkin = await client.post(
        f"/api/v1/bookings/{booking_id}/checkin",
        json={"qr_code_hash": qr_hash},
        headers=user_headers,
    )
    assert good_checkin.status_code == 200
    checked_booking = good_checkin.json()
    assert checked_booking["status"] == "CHECKED_IN"
    assert checked_booking["checked_in_at"] is not None


@pytest.mark.asyncio
async def test_auto_release_no_show_logic(client: AsyncClient, db_session: AsyncSession):
    _, user_token, desk_id, _ = await setup_test_desk(client, "BAIA-BK-NOSHOW")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Booking with start_time 45 minutes in the past
    now = datetime.now(timezone.utc)
    past_start = now - timedelta(minutes=45)
    past_end = now + timedelta(hours=3)

    payload = {
        "desk_id": desk_id,
        "start_time": past_start.isoformat(),
        "end_time": past_end.isoformat(),
    }
    b_res = await client.post("/api/v1/bookings", json=payload, headers=user_headers)
    assert b_res.status_code == 201
    booking_id = b_res.json()["id"]

    # Run auto-release processing directly on database
    expired_count = await BookingService.process_no_shows(db_session)
    assert expired_count >= 1

    # Verify status changed to EXPIRADA_NO_SHOW
    booking = await BookingService.get_booking_by_id(db_session, booking_id)
    assert booking is not None
    assert booking.status == "EXPIRADA_NO_SHOW"


@pytest.mark.asyncio
async def test_3d_office_layout_projection(client: AsyncClient):
    _, user_token, desk_id, qr_hash = await setup_test_desk(client, "BAIA-3D-LAYOUT")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Create active booking and check in
    now = datetime.now(timezone.utc)
    payload = {
        "desk_id": desk_id,
        "start_time": (now - timedelta(minutes=5)).isoformat(),
        "end_time": (now + timedelta(hours=3)).isoformat(),
    }
    b_res = await client.post("/api/v1/bookings", json=payload, headers=user_headers)
    booking_id = b_res.json()["id"]

    await client.post(
        f"/api/v1/bookings/{booking_id}/checkin",
        json={"qr_code_hash": qr_hash},
        headers=user_headers,
    )

    # Fetch 3D office layout projection
    layout_res = await client.get("/api/v1/bookings/3d-office", headers=user_headers)
    assert layout_res.status_code == 200
    desks_3d = layout_res.json()
    assert len(desks_3d) >= 1

    target_desk = next((d for d in desks_3d if d["id"] == desk_id), None)
    assert target_desk is not None
    assert target_desk["status"] == "OCUPADA"
    assert target_desk["occupant_name"] is not None
    assert "pos_x" in target_desk
    assert "pos_y" in target_desk
    assert "pos_z" in target_desk


@pytest.mark.asyncio
async def test_booking_meeting_room_max_duration_exceeded(client: AsyncClient):
    admin_token, user_token, _, _ = await setup_test_desk(client, "ROOM-DUR-01")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Create Meeting Room with 60 min max duration
    zone_res = await client.post(
        "/api/v1/zones",
        json={"name": "Zona Reuniões Rápidas", "floor": 2},
        headers=admin_headers,
    )
    zone_id = zone_res.json()["id"]

    room_res = await client.post(
        "/api/v1/desks",
        json={
            "code": "SALA-RAPIDA-01",
            "zone_id": zone_id,
            "space_type": "SALA_REUNIAO",
            "capacity": 6,
            "max_duration_minutes": 60,
        },
        headers=admin_headers,
    )
    assert room_res.status_code == 201
    room_id = room_res.json()["id"]

    now = datetime.now(timezone.utc)
    base_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(days=2)

    # 1. Try booking for 90 minutes -> Should fail
    fail_payload = {
        "desk_id": room_id,
        "start_time": base_time.isoformat(),
        "end_time": (base_time + timedelta(minutes=90)).isoformat(),
    }
    fail_res = await client.post("/api/v1/bookings", json=fail_payload, headers=user_headers)
    assert fail_res.status_code == 400
    assert fail_res.json()["detail"]["code"] == "MAX_DURATION_EXCEEDED"

    # 2. Book for 45 minutes -> Should succeed
    ok_payload = {
        "desk_id": room_id,
        "start_time": base_time.isoformat(),
        "end_time": (base_time + timedelta(minutes=45)).isoformat(),
    }
    ok_res = await client.post("/api/v1/bookings", json=ok_payload, headers=user_headers)
    assert ok_res.status_code == 201


@pytest.mark.asyncio
async def test_booking_restricted_room_by_colaborador_forbidden(client: AsyncClient):
    admin_token, user_token, _, _ = await setup_test_desk(client, "ROOM-ROLE-01")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Create Executive Room restricted to gestores
    zone_res = await client.post(
        "/api/v1/zones",
        json={"name": "Zona Executiva", "floor": 3},
        headers=admin_headers,
    )
    zone_id = zone_res.json()["id"]

    room_res = await client.post(
        "/api/v1/desks",
        json={
            "code": "SALA-BOARD-01",
            "zone_id": zone_id,
            "space_type": "SALA_REUNIAO",
            "capacity": 12,
            "required_role": "gestor",
            "max_duration_minutes": 120,
        },
        headers=admin_headers,
    )
    assert room_res.status_code == 201
    room_id = room_res.json()["id"]

    now = datetime.now(timezone.utc)
    base_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(days=3)
    booking_payload = {
        "desk_id": room_id,
        "start_time": base_time.isoformat(),
        "end_time": (base_time + timedelta(minutes=60)).isoformat(),
    }

    # 1. Colaborador attempt -> 403 Forbidden
    forbidden_res = await client.post(
        "/api/v1/bookings", json=booking_payload, headers=user_headers
    )
    assert forbidden_res.status_code == 403
    assert forbidden_res.json()["detail"]["code"] == "RESERVATION_RESTRICTED_ROLE"

    # 2. Admin attempt -> 201 Created
    admin_booking_res = await client.post(
        "/api/v1/bookings", json=booking_payload, headers=admin_headers
    )
    assert admin_booking_res.status_code == 201


@pytest.mark.asyncio
async def test_booking_cancel_pending(client: AsyncClient):
    _, user_token, desk_id, _ = await setup_test_desk(client, "BAIA-CANCEL-TEST")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    tomorrow = datetime.now(timezone.utc) + timedelta(days=2)
    b_res = await client.post(
        "/api/v1/bookings",
        json={
            "desk_id": desk_id,
            "start_time": (tomorrow.replace(hour=9, minute=0)).isoformat(),
            "end_time": (tomorrow.replace(hour=18, minute=0)).isoformat(),
        },
        headers=user_headers,
    )
    assert b_res.status_code == 201
    b_id = b_res.json()["id"]

    # Cancel pending booking
    cancel_res = await client.post(f"/api/v1/bookings/{b_id}/cancel", headers=user_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELADA_USUARIO"


@pytest.mark.asyncio
async def test_early_checkout_and_desk_rebooking(client: AsyncClient):
    _, user1_token, desk_id, qr_hash = await setup_test_desk(client, "BAIA-CHECKOUT-TEST")
    user1_headers = {"Authorization": f"Bearer {user1_token}"}

    # Register user 2
    reg2_payload = {
        "email": "user2_checkout@myaloca.com",
        "full_name": "User 2 Checkout",
        "password": "pwd",
        "role": "colaborador",
    }
    await client.post("/api/v1/auth/register", json=reg2_payload)
    login2 = await client.post(
        "/api/v1/auth/login", data={"username": "user2_checkout@myaloca.com", "password": "pwd"}
    )
    user2_token = login2.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 1 books desk from now to now + 5h
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=5)
    end_time = now + timedelta(hours=5)

    b1_res = await client.post(
        "/api/v1/bookings",
        json={
            "desk_id": desk_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
        headers=user1_headers,
    )
    assert b1_res.status_code == 201
    b1_id = b1_res.json()["id"]

    # User 1 checks in
    checkin_res = await client.post(
        f"/api/v1/bookings/{b1_id}/checkin",
        json={"qr_code_hash": qr_hash},
        headers=user1_headers,
    )
    assert checkin_res.status_code == 200
    assert checkin_res.json()["status"] == "CHECKED_IN"

    # User 2 tries to book desk during User 1's scheduled time -> 409 Conflict
    overlap_res = await client.post(
        "/api/v1/bookings",
        json={
            "desk_id": desk_id,
            "start_time": (now + timedelta(hours=1)).isoformat(),
            "end_time": (now + timedelta(hours=3)).isoformat(),
        },
        headers=user2_headers,
    )
    assert overlap_res.status_code == 409
    assert overlap_res.json()["detail"]["code"] == "BOOKING_OVERLAP"

    # User 1 leaves early -> performs early checkout
    checkout_res = await client.post(f"/api/v1/bookings/{b1_id}/checkout", headers=user1_headers)
    assert checkout_res.status_code == 200
    checked_out_data = checkout_res.json()
    assert checked_out_data["status"] == "FINALIZADA"

    # Now User 2 tries again to book the newly freed desk -> 201 Created!
    rebook_res = await client.post(
        "/api/v1/bookings",
        json={
            "desk_id": desk_id,
            "start_time": (now + timedelta(hours=1)).isoformat(),
            "end_time": (now + timedelta(hours=3)).isoformat(),
        },
        headers=user2_headers,
    )
    assert rebook_res.status_code == 201



