from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.department import Department
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)

router = APIRouter()


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    company_id: int | None = None,
    is_active: bool | None = None,
    search: str | None = Query(None, description="Busca por nome ou sigla"),
) -> list[DepartmentResponse]:
    query = (
        select(
            Department,
            func.count(User.id).label("users_count"),
        )
        .outerjoin(
            User,
            or_(User.department_id == Department.id, User.department == Department.name),
        )
        .group_by(Department.id)
        .order_by(Department.name.asc())
    )

    if company_id is not None:
        query = query.where(Department.company_id == company_id)
    if is_active is not None:
        query = query.where(Department.is_active == is_active)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Department.name.ilike(search_term),
                Department.code.ilike(search_term),
                Department.description.ilike(search_term),
            )
        )

    result = await db.execute(query)
    rows = result.all()

    output: list[DepartmentResponse] = []
    for dept, count in rows:
        dept_dict = {
            "id": dept.id,
            "name": dept.name,
            "code": dept.code,
            "description": dept.description,
            "company_id": dept.company_id,
            "is_active": dept.is_active,
            "created_at": dept.created_at,
            "users_count": count or 0,
        }
        output.append(DepartmentResponse.model_validate(dept_dict))
    return output


@router.get("/{id}", response_model=DepartmentResponse)
async def get_department(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DepartmentResponse:
    query = (
        select(
            Department,
            func.count(User.id).label("users_count"),
        )
        .outerjoin(
            User,
            or_(User.department_id == Department.id, User.department == Department.name),
        )
        .where(Department.id == id)
        .group_by(Department.id)
    )
    result = await db.execute(query)
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DEPARTMENT_NOT_FOUND", "message": "Departamento não encontrado."},
        )
    dept, count = row
    dept_dict = {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "description": dept.description,
        "company_id": dept.company_id,
        "is_active": dept.is_active,
        "created_at": dept.created_at,
        "users_count": count or 0,
    }
    return DepartmentResponse.model_validate(dept_dict)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_in: DepartmentCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DepartmentResponse:
    # Check if duplicate name or code within company
    dup_query = select(Department).where(
        Department.name.ilike(dept_in.name.strip()),
        Department.company_id == dept_in.company_id,
    )
    dup_res = await db.execute(dup_query)
    if dup_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "DEPARTMENT_NAME_EXISTS",
                "message": f"Já existe um departamento cadastrado com o nome '{dept_in.name}'.",
            },
        )

    dept = Department(
        name=dept_in.name.strip(),
        code=dept_in.code.strip().upper() if dept_in.code else None,
        description=dept_in.description.strip() if dept_in.description else None,
        company_id=dept_in.company_id,
        is_active=dept_in.is_active,
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)

    dept_dict = {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "description": dept.description,
        "company_id": dept.company_id,
        "is_active": dept.is_active,
        "created_at": dept.created_at,
        "users_count": 0,
    }
    return DepartmentResponse.model_validate(dept_dict)


@router.put("/{id}", response_model=DepartmentResponse)
async def update_department(
    id: int,
    dept_in: DepartmentUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DepartmentResponse:
    dept_res = await db.execute(select(Department).where(Department.id == id))
    dept = dept_res.scalar_one_or_none()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DEPARTMENT_NOT_FOUND", "message": "Departamento não encontrado."},
        )

    if dept_in.name is not None and dept_in.name.strip() != dept.name:
        target_company_id = (
            dept_in.company_id if dept_in.company_id is not None else dept.company_id
        )
        dup_query = select(Department).where(
            Department.name.ilike(dept_in.name.strip()),
            Department.company_id == target_company_id,
            Department.id != id,
        )
        if (await db.execute(dup_query)).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "DEPARTMENT_NAME_EXISTS",
                    "message": f"Já existe outro departamento com o nome '{dept_in.name}'.",
                },
            )
        dept.name = dept_in.name.strip()

    if dept_in.code is not None:
        dept.code = dept_in.code.strip().upper() if dept_in.code else None
    if dept_in.description is not None:
        dept.description = dept_in.description.strip() if dept_in.description else None
    if dept_in.company_id is not None:
        dept.company_id = dept_in.company_id
    if dept_in.is_active is not None:
        dept.is_active = dept_in.is_active

    db.add(dept)
    await db.commit()
    await db.refresh(dept)

    # Get users count
    cnt_query = select(func.count(User.id)).where(
        or_(User.department_id == dept.id, User.department == dept.name)
    )
    users_count = (await db.execute(cnt_query)).scalar() or 0

    dept_dict = {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "description": dept.description,
        "company_id": dept.company_id,
        "is_active": dept.is_active,
        "created_at": dept.created_at,
        "users_count": users_count,
    }
    return DepartmentResponse.model_validate(dept_dict)


@router.delete("/{id}")
async def delete_department(
    id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    dept_res = await db.execute(select(Department).where(Department.id == id))
    dept = dept_res.scalar_one_or_none()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DEPARTMENT_NOT_FOUND", "message": "Departamento não encontrado."},
        )

    # Referral protection: check if users belong to this department
    user_cnt = (
        await db.execute(
            select(func.count(User.id)).where(
                or_(User.department_id == dept.id, User.department == dept.name)
            )
        )
    ).scalar() or 0

    if user_cnt > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "DEPARTMENT_HAS_USERS",
                "message": (
                    f"Não é possível excluir o departamento '{dept.name}' pois existem "
                    f"{user_cnt} colaborador(es) vinculado(s). Remaneje-os primeiro."
                ),
            },
        )

    await db.delete(dept)
    await db.commit()
    return {
        "code": "DEPARTMENT_DELETED",
        "message": f"Departamento '{dept.name}' excluído com sucesso.",
    }
