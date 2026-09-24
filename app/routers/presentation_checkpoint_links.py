from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse

from app.auth.auth import get_current_active_user
from app.models.presentation_checkpoint_link import (
    PresentationCheckpointLink,
    PresentationCheckpointLinkInDB,
)
from app.models.user import UserInDB
from app.services.presentation import PresentationService
from app.services.presentation_checkpoint_link import PresentationCheckpointLinkService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=PresentationCheckpointLink)
async def insert_presentation_checkpoint_link(
    presentation: PresentationCheckpointLink,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    presentationDB = PresentationCheckpointLinkInDB(**presentation.dict())
    presentationDB.username_insert = current_user.username
    inserted = PresentationCheckpointLinkService.insert(presentationDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_presentation_checkpoint_link(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = PresentationCheckpointLinkService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="PresentationCheckpointLink not found",
        )
    PresentationCheckpointLinkService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=PresentationCheckpointLink)
async def get_presentation_checkpoint_link(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = PresentationCheckpointLinkService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="PresentationCheckpointLink not found",
        )
    return find


@router.get("", response_model=List[PresentationCheckpointLink])
async def get_all_presentation_checkpoint_links(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = PresentationCheckpointLinkService.get_all()
    return finds


@router.put("", response_model=PresentationCheckpointLink)
async def update_presentation_checkpoint_link(
    presentation: PresentationCheckpointLink,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = PresentationCheckpointLinkService.get(presentation.id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Product not found",
        )
    presentationDB = PresentationCheckpointLinkInDB(**presentation.dict())
    presentationDB.username_update = current_user.username
    updated = PresentationCheckpointLinkService.update(presentation.id, presentationDB)
    return updated


@router.get(
    "/{id_presentation}/generate-links",
    response_model=list[PresentationCheckpointLink],
)
async def generate_presentation_checkpoint_links(
    id_presentation: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = PresentationService.get(id_presentation)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Presentation not found",
        )
    generated_links = await PresentationCheckpointLinkService.generate_links(find)
    return generated_links


@router.get("/{id}/activate", response_model=PresentationCheckpointLink)
async def activate_presentation_checkpoint_link(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = PresentationCheckpointLinkService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="PresentationCheckpointLink not found",
        )
    now = datetime.utcnow()
    start = find.start_duration
    if start is None or start < now:
        start = now
    activated = PresentationCheckpointLinkService.active_link(id, start)
    if activated is None:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Failed to activate PresentationCheckpointLink",
        )
    return activated


@router.get("/{id}/deactivate", response_model=PresentationCheckpointLink)
async def deactivate_presentation_checkpoint_link(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = PresentationCheckpointLinkService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="PresentationCheckpointLink not found",
        )
    deactivated = PresentationCheckpointLinkService.deactivate_link(id)
    if deactivated is None:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Failed to deactivate PresentationCheckpointLink",
        )
    return deactivated
