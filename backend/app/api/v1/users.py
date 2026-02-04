"""User profile and API key endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db, require_permissions
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyResponse,
    OperationStatus,
    UserPasswordUpdateRequest,
    UserUpdateRequest,
)
from app.services.user import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user.",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """
    Get current user's profile.

    Requires authentication.
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user.",
)
async def update_me(
    data: UserUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    service = UserService(db)
    try:
        user = await service.update_profile(current_user, data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.put(
    "/me/password",
    response_model=OperationStatus,
    summary="Change current user password",
    description="Change the password for the currently authenticated user.",
)
async def change_password(
    data: UserPasswordUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> OperationStatus:
    service = UserService(db)
    try:
        await service.change_password(current_user, data)
        return OperationStatus(message="Password updated")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post(
    "/me/api-keys",
    response_model=ApiKeyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
    description="Create a new API key for the current user.",
)
async def create_api_key(
    data: ApiKeyCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ApiKeyCreateResponse:
    service = UserService(db)
    try:
        raw_key, api_key = await service.create_api_key(current_user, data)
        return ApiKeyCreateResponse(
            api_key=raw_key,
            key=ApiKeyResponse.model_validate(api_key),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/me/api-keys",
    response_model=list[ApiKeyResponse],
    summary="List API keys",
    description="List API keys for the current user.",
)
async def list_api_keys(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[ApiKeyResponse]:
    service = UserService(db)
    api_keys = await service.list_api_keys(current_user)
    return [ApiKeyResponse.model_validate(key) for key in api_keys]


@router.delete(
    "/me/api-keys/{key_id}",
    response_model=OperationStatus,
    summary="Delete API key",
    description="Delete an API key by ID for the current user.",
)
async def delete_api_key(
    key_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> OperationStatus:
    service = UserService(db)
    try:
        await service.delete_api_key(current_user, key_id)
        return OperationStatus(message="API key deleted")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get user profile by ID. Requires 'users:view' permission.",
    dependencies=[Depends(require_permissions("users:view"))],
)
async def get_user_by_id(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """
    Get user by ID.

    Requires 'users:view' permission.
    """
    import uuid

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        ) from e

    user = await db.get(User, user_uuid)

    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)
