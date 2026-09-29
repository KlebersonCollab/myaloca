from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserResponse

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def list_users(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    role: str | None = None,
    department: str | None = None,
    search: str | None = None,
    is_active: bool | None = None,
) -> Sequence[User]:
    query = select(User)

    if role:
        query = query.where(User.role == role)
    if department:
        query = query.where(User.department == department)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.job_title.ilike(search_pattern),
            )
        )

    result = await db.execute(query.order_by(User.full_name))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "Usuário não encontrado."},
        )
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: AdminUserCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    existing = (
        await db.execute(select(User).where(User.email == user_in.email))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_ALREADY_REGISTERED",
                "message": "Este e-mail já está cadastrado no sistema.",
            },
        )

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        avatar_url=user_in.avatar_url,
        photo_url=user_in.photo_url,
        job_title=user_in.job_title,
        department=user_in.department,
        is_active=user_in.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: AdminUserUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "Usuário não encontrado."},
        )

    if user_in.email and user_in.email != user.email:
        existing = (
            await db.execute(select(User).where(User.email == user_in.email))
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_ALREADY_REGISTERED",
                    "message": "Este e-mail já está cadastrado.",
                },
            )
        user.email = user_in.email

    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.avatar_url is not None:
        user.avatar_url = user_in.avatar_url
    if user_in.photo_url is not None:
        user.photo_url = user_in.photo_url
    if user_in.job_title is not None:
        user.job_title = user_in.job_title
    if user_in.department is not None:
        user.department = user_in.department
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.password is not None:
        user.hashed_password = get_password_hash(user_in.password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CANNOT_DELETE_SELF",
                "message": "Você não pode excluir sua própria conta de administrador.",
            },
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "Usuário não encontrado."},
        )

    await db.delete(user)
    await db.commit()
    return {"code": "USER_DELETED", "message": "Usuário removido com sucesso."}
