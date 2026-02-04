"""LLM Model management endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.llm_model import (
    LLMModelCreateRequest,
    LLMModelListResponse,
    LLMModelResponse,
    LLMModelTestRequest,
    LLMModelTestResponse,
    LLMModelUpdateRequest,
    OperationStatus,
)
from app.services.llm_model import LLMModelService

router = APIRouter()


@router.post(
    "",
    response_model=LLMModelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create LLM model configuration",
    description="Create a new LLM model configuration with encrypted API key storage.",
)
async def create_model(
    data: LLMModelCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LLMModelResponse:
    """
    Create a new LLM model configuration.

    The API key will be encrypted before storage.
    """
    service = LLMModelService(db)
    model = await service.create_model(current_user, data)
    return service.to_response(model)


@router.get(
    "",
    response_model=LLMModelListResponse,
    summary="List LLM model configurations",
    description="Get all LLM model configurations for the current user.",
)
async def list_models(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LLMModelListResponse:
    """
    List all LLM model configurations.

    Returns models sorted by default status and creation date.
    """
    service = LLMModelService(db)
    models = await service.list_models(current_user)
    return LLMModelListResponse(
        models=[service.to_response(m) for m in models],
        total=len(models),
    )


@router.get(
    "/{model_id}",
    response_model=LLMModelResponse,
    summary="Get LLM model configuration",
    description="Get a specific LLM model configuration by ID.",
)
async def get_model(
    model_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LLMModelResponse:
    """Get a specific LLM model configuration."""
    service = LLMModelService(db)
    model = await service.get_model(current_user, model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )
    return service.to_response(model)


@router.put(
    "/{model_id}",
    response_model=LLMModelResponse,
    summary="Update LLM model configuration",
    description="Update an existing LLM model configuration.",
)
async def update_model(
    model_id: UUID,
    data: LLMModelUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LLMModelResponse:
    """
    Update an LLM model configuration.

    If a new API key is provided, it will be re-encrypted.
    """
    service = LLMModelService(db)
    model = await service.update_model(current_user, model_id, data)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )
    return service.to_response(model)


@router.delete(
    "/{model_id}",
    response_model=OperationStatus,
    summary="Delete LLM model configuration",
    description="Soft delete an LLM model configuration.",
)
async def delete_model(
    model_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> OperationStatus:
    """Delete an LLM model configuration."""
    service = LLMModelService(db)
    deleted = await service.delete_model(current_user, model_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )
    return OperationStatus(message="Model deleted successfully")


@router.post(
    "/{model_id}/test",
    response_model=LLMModelTestResponse,
    summary="Test LLM model configuration",
    description="Test the connection and functionality of an LLM model configuration.",
)
async def test_model(
    model_id: UUID,
    data: LLMModelTestRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LLMModelTestResponse:
    """
    Test an LLM model configuration.

    Sends a test request to verify the model is working correctly.
    """
    service = LLMModelService(db)
    return await service.test_model(current_user, model_id, data.prompt)


@router.post(
    "/{model_id}/set-default",
    response_model=LLMModelResponse,
    summary="Set default LLM model",
    description="Set an LLM model as the default for the current user.",
)
async def set_default_model(
    model_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LLMModelResponse:
    """
    Set an LLM model as the default.

    This will unset any previously default model.
    """
    service = LLMModelService(db)
    model = await service.set_default_model(current_user, model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )
    return service.to_response(model)


@router.get(
    "/default",
    response_model=LLMModelResponse,
    summary="Get default LLM model",
    description="Get the default LLM model for the current user.",
)
async def get_default_model(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LLMModelResponse:
    """Get the user's default LLM model."""
    service = LLMModelService(db)
    model = await service.get_default_model(current_user)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default model configured",
        )
    return service.to_response(model)
