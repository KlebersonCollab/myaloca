import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_department_crud_and_referral_guard(client: AsyncClient):
    # 1. Register admin and regular user
    admin_reg = {
        "email": "admin_dept@myaloca.com",
        "full_name": "Admin Dept",
        "password": "pass",
        "role": "admin",
    }
    await client.post("/api/v1/auth/register", json=admin_reg)
    admin_login = await client.post(
        "/api/v1/auth/login", data={"username": "admin_dept@myaloca.com", "password": "pass"}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    user_reg = {
        "email": "user_dept@myaloca.com",
        "full_name": "User Dept",
        "password": "pass",
        "role": "colaborador",
    }
    await client.post("/api/v1/auth/register", json=user_reg)
    user_login = await client.post(
        "/api/v1/auth/login", data={"username": "user_dept@myaloca.com", "password": "pass"}
    )
    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 2. Regular user cannot create department
    forbidden_res = await client.post(
        "/api/v1/departments",
        json={"name": "Tecnologia", "code": "TEC"},
        headers=user_headers,
    )
    assert forbidden_res.status_code == 403

    # 3. Admin creates department
    create_res = await client.post(
        "/api/v1/departments",
        json={
            "name": "Tecnologia e Engenharia",
            "code": "TEC",
            "description": "Engenharia de software e infraestrutura",
        },
        headers=admin_headers,
    )
    assert create_res.status_code == 201
    dept_data = create_res.json()
    assert dept_data["name"] == "Tecnologia e Engenharia"
    assert dept_data["code"] == "TEC"
    dept_id = dept_data["id"]

    # 4. Duplicate name rejected
    dup_res = await client.post(
        "/api/v1/departments",
        json={"name": "Tecnologia e Engenharia", "code": "OUTRO"},
        headers=admin_headers,
    )
    assert dup_res.status_code == 400
    assert dup_res.json()["detail"]["code"] == "DEPARTMENT_NAME_EXISTS"

    # 5. List departments
    list_res = await client.get("/api/v1/departments", headers=user_headers)
    assert list_res.status_code == 200
    departments = list_res.json()
    assert any(d["id"] == dept_id for d in departments)

    # 6. Update user to belong to this department
    me_res = await client.put(
        "/api/v1/auth/me",
        json={"department": "Tecnologia e Engenharia"},
        headers=user_headers,
    )
    assert me_res.status_code == 200

    # 7. Check users_count is reflected in department
    get_res = await client.get(f"/api/v1/departments/{dept_id}", headers=user_headers)
    assert get_res.status_code == 200
    assert get_res.json()["users_count"] >= 1

    # 8. Deleting department with users should be blocked
    del_blocked = await client.delete(f"/api/v1/departments/{dept_id}", headers=admin_headers)
    assert del_blocked.status_code == 400
    assert del_blocked.json()["detail"]["code"] == "DEPARTMENT_HAS_USERS"

    # 9. Clear user's department
    await client.put(
        "/api/v1/auth/me",
        json={"department": ""},
        headers=user_headers,
    )

    # 10. Update department info
    update_res = await client.put(
        f"/api/v1/departments/{dept_id}",
        json={"name": "Engenharia de Software", "code": "ENG"},
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Engenharia de Software"
    assert update_res.json()["code"] == "ENG"

    # 11. Delete department successfully after users unlinked
    del_success = await client.delete(f"/api/v1/departments/{dept_id}", headers=admin_headers)
    assert del_success.status_code == 200
    assert del_success.json()["code"] == "DEPARTMENT_DELETED"
