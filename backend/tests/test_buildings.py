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
async def test_company_crud(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_co@myaloca.com", "admin")
    colab_token = await get_auth_token(client, "colab_co@myaloca.com", "colaborador")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    colab_headers = {"Authorization": f"Bearer {colab_token}"}

    # 1. Colaborador cannot create company
    resp = await client.post(
        "/api/v1/companies",
        json={"name": "Tech Corp", "code": "TECHCORP"},
        headers=colab_headers,
    )
    assert resp.status_code == 403

    # 2. Admin creates company
    resp = await client.post(
        "/api/v1/companies",
        json={
            "name": "Acme Global",
            "code": "ACME",
            "cnpj": "12.345.678/0001-90",
            "description": "Sede corporativa global",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    company = resp.json()
    assert company["name"] == "Acme Global"
    assert company["code"] == "ACME"
    company_id = company["id"]

    # 3. Duplicate code returns 400
    dup_resp = await client.post(
        "/api/v1/companies",
        json={"name": "Duplicate Acme", "code": "ACME"},
        headers=admin_headers,
    )
    assert dup_resp.status_code == 400
    assert dup_resp.json()["detail"]["code"] == "COMPANY_CODE_EXISTS"

    # 4. List companies (accessible by authenticated user)
    list_resp = await client.get("/api/v1/companies", headers=colab_headers)
    assert list_resp.status_code == 200
    companies = list_resp.json()
    assert any(c["id"] == company_id for c in companies)

    # 5. Get company by id
    get_resp = await client.get(f"/api/v1/companies/{company_id}", headers=colab_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["code"] == "ACME"

    # 6. Update company
    update_resp = await client.put(
        f"/api/v1/companies/{company_id}",
        json={"name": "Acme Corporation Inc"},
        headers=admin_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Acme Corporation Inc"


@pytest.mark.asyncio
async def test_building_crud_and_dependency_guard(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_bldg@myaloca.com", "admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create company
    c_resp = await client.post(
        "/api/v1/companies",
        json={"name": "Nexus Holding", "code": "NEXUS"},
        headers=admin_headers,
    )
    company_id = c_resp.json()["id"]

    # 2. Create building
    b_resp = await client.post(
        "/api/v1/buildings",
        json={
            "name": "Nexus Tower Matriz",
            "code": "NEXUS-TOWER",
            "company_id": company_id,
            "address": "Av. Paulista, 1000",
            "city": "São Paulo",
            "total_floors": 15,
        },
        headers=admin_headers,
    )
    assert b_resp.status_code == 201
    building = b_resp.json()
    building_id = building["id"]
    assert building["name"] == "Nexus Tower Matriz"
    assert building["company_id"] == company_id

    # 3. Duplicate building code -> 400
    b_dup = await client.post(
        "/api/v1/buildings",
        json={"name": "Another Tower", "code": "NEXUS-TOWER", "company_id": company_id},
        headers=admin_headers,
    )
    assert b_dup.status_code == 400
    assert b_dup.json()["detail"]["code"] == "BUILDING_CODE_EXISTS"

    # 4. Try deleting company with building -> 400 guard
    c_del = await client.delete(f"/api/v1/companies/{company_id}", headers=admin_headers)
    assert c_del.status_code == 400
    assert c_del.json()["detail"]["code"] == "COMPANY_HAS_BUILDINGS"

    # 5. List buildings with company_id filter
    b_list = await client.get(f"/api/v1/buildings?company_id={company_id}", headers=admin_headers)
    assert b_list.status_code == 200
    assert len(b_list.json()) == 1

    # 6. Update building
    b_up = await client.put(
        f"/api/v1/buildings/{building_id}",
        json={"name": "Nexus Corporate Center", "total_floors": 18},
        headers=admin_headers,
    )
    assert b_up.status_code == 200
    assert b_up.json()["name"] == "Nexus Corporate Center"
    assert b_up.json()["total_floors"] == 18


@pytest.mark.asyncio
async def test_full_hierarchy_deletion_guards_and_desk_update(client: AsyncClient):
    admin_token = await get_auth_token(client, "admin_hier@myaloca.com", "admin")
    colab_token = await get_auth_token(client, "colab_hier@myaloca.com", "colaborador")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    colab_headers = {"Authorization": f"Bearer {colab_token}"}

    # 1. Create Company -> Building -> Zone -> Desk
    c_resp = await client.post(
        "/api/v1/companies",
        json={"name": "Apex Group", "code": "APEX"},
        headers=admin_headers,
    )
    c_id = c_resp.json()["id"]

    b_resp = await client.post(
        "/api/v1/buildings",
        json={"name": "Apex One", "code": "APEX-ONE", "company_id": c_id},
        headers=admin_headers,
    )
    b_id = b_resp.json()["id"]

    z_resp = await client.post(
        "/api/v1/zones",
        json={"name": "Apex 5o Andar", "floor": 5, "building_id": b_id},
        headers=admin_headers,
    )
    assert z_resp.status_code == 201
    z_id = z_resp.json()["id"]

    # Test zone filter by building_id
    z_list = await client.get(f"/api/v1/zones?building_id={b_id}", headers=admin_headers)
    assert z_list.status_code == 200
    assert any(z["id"] == z_id for z in z_list.json())

    # Create Desk
    d_resp = await client.post(
        "/api/v1/desks",
        json={
            "code": "APX-D01",
            "zone_id": z_id,
            "pos_x": 5.0,
            "pos_z": 2.0,
            "space_type": "BAIA",
        },
        headers=admin_headers,
    )
    assert d_resp.status_code == 201
    d_id = d_resp.json()["id"]

    # 2. Update Desk
    up_desk = await client.put(
        f"/api/v1/desks/{d_id}",
        json={"has_monitor": True, "capacity": 2, "space_type": "SALA_REUNIAO"},
        headers=admin_headers,
    )
    assert up_desk.status_code == 200
    assert up_desk.json()["has_monitor"] is True
    assert up_desk.json()["space_type"] == "SALA_REUNIAO"

    # Collaborator cannot update desk
    colab_up = await client.put(
        f"/api/v1/desks/{d_id}",
        json={"capacity": 5},
        headers=colab_headers,
    )
    assert colab_up.status_code == 403

    # 3. Guard: Cannot delete building if zone exists
    b_del_guard = await client.delete(f"/api/v1/buildings/{b_id}", headers=admin_headers)
    assert b_del_guard.status_code == 400
    assert b_del_guard.json()["detail"]["code"] == "BUILDING_HAS_ZONES"

    # 4. Guard: Cannot delete zone if desk exists
    z_del_guard = await client.delete(f"/api/v1/zones/{z_id}", headers=admin_headers)
    assert z_del_guard.status_code == 400
    assert z_del_guard.json()["detail"]["code"] == "ZONE_HAS_DESKS"

    # 5. Clean teardown from bottom to top: Desk -> Zone -> Building -> Company
    del_desk = await client.delete(f"/api/v1/desks/{d_id}", headers=admin_headers)
    assert del_desk.status_code == 200

    del_zone = await client.delete(f"/api/v1/zones/{z_id}", headers=admin_headers)
    assert del_zone.status_code == 200

    del_bldg = await client.delete(f"/api/v1/buildings/{b_id}", headers=admin_headers)
    assert del_bldg.status_code == 200

    del_comp = await client.delete(f"/api/v1/companies/{c_id}", headers=admin_headers)
    assert del_comp.status_code == 200
