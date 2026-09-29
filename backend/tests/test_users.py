import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient, email: str, role: str) -> tuple[str, int]:
    reg_payload = {
        "email": email,
        "full_name": f"User {role}",
        "password": "password123",
        "role": role,
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    user_id = reg_res.json()["id"]

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"},
    )
    return login_res.json()["access_token"], user_id


@pytest.mark.asyncio
async def test_self_profile_update(client: AsyncClient):
    token, _ = await get_auth_token(client, "colab_self@myaloca.com", "colaborador")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Update own profile: cargo (job_title), department, avatar, name
    update_res = await client.put(
        "/api/v1/auth/me",
        json={
            "full_name": "Dev Sênior da Silva",
            "job_title": "Senior Staff Engineer",
            "department": "Arquitetura & Core",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=SeniorDev",
        },
        headers=headers,
    )
    assert update_res.status_code == 200
    user_data = update_res.json()
    assert user_data["full_name"] == "Dev Sênior da Silva"
    assert user_data["job_title"] == "Senior Staff Engineer"
    assert user_data["department"] == "Arquitetura & Core"
    assert "SeniorDev" in user_data["avatar_url"]

    # 2. Verify GET /me returns the updated profile
    get_me = await client.get("/api/v1/auth/me", headers=headers)
    assert get_me.status_code == 200
    assert get_me.json()["job_title"] == "Senior Staff Engineer"


@pytest.mark.asyncio
async def test_admin_user_crud_and_role_management(client: AsyncClient):
    admin_token, admin_id = await get_auth_token(client, "admin_roles@myaloca.com", "admin")
    colab_token, _ = await get_auth_token(client, "colab_test@myaloca.com", "colaborador")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    colab_headers = {"Authorization": f"Bearer {colab_token}"}

    # 1. Collaborator cannot list or modify users
    colab_list = await client.get("/api/v1/users", headers=colab_headers)
    assert colab_list.status_code == 403

    # 2. Admin lists users
    admin_list = await client.get("/api/v1/users", headers=admin_headers)
    assert admin_list.status_code == 200
    assert len(admin_list.json()) >= 2

    # 3. Admin creates new user with role 'gestor' and specific cargo
    create_res = await client.post(
        "/api/v1/users",
        json={
            "email": "gestor_novo@myaloca.com",
            "full_name": "Gestor de Facilities",
            "password": "securepassword123",
            "role": "gestor",
            "job_title": "Coordenador de Infraestrutura",
            "department": "Operações Prediais",
        },
        headers=admin_headers,
    )
    assert create_res.status_code == 201
    new_user = create_res.json()
    assert new_user["role"] == "gestor"
    assert new_user["job_title"] == "Coordenador de Infraestrutura"
    new_user_id = new_user["id"]

    # 4. Duplicate email returns 409
    dup_res = await client.post(
        "/api/v1/users",
        json={
            "email": "gestor_novo@myaloca.com",
            "full_name": "Duplicate",
            "password": "pass",
        },
        headers=admin_headers,
    )
    assert dup_res.status_code == 409
    assert dup_res.json()["detail"]["code"] == "EMAIL_ALREADY_REGISTERED"

    # 5. Admin updates role and cargo of user
    up_res = await client.put(
        f"/api/v1/users/{new_user_id}",
        json={
            "role": "admin",
            "job_title": "Diretor de Operações",
            "department": "Facilities Global",
        },
        headers=admin_headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["role"] == "admin"
    assert up_res.json()["job_title"] == "Diretor de Operações"

    # 6. Admin filters by search term
    search_res = await client.get("/api/v1/users?search=Diretor", headers=admin_headers)
    assert search_res.status_code == 200
    assert any(u["id"] == new_user_id for u in search_res.json())

    # 7. Self-deletion is guarded
    self_del = await client.delete(f"/api/v1/users/{admin_id}", headers=admin_headers)
    assert self_del.status_code == 400
    assert self_del.json()["detail"]["code"] == "CANNOT_DELETE_SELF"

    # 8. Delete user successfully
    del_res = await client.delete(f"/api/v1/users/{new_user_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["code"] == "USER_DELETED"
