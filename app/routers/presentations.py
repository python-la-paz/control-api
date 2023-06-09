from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.presentation import Presentation, PresentationInDB

from app.models.user import UserInDB
from app.services.presentation import PresentationService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Presentation)
async def insert_presentation(
    presentation: Presentation,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    presentationDB = PresentationInDB(**presentation.dict())
    presentationDB.username_insert = current_user.username
    inserted = PresentationService.insert(presentationDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_presentation(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = PresentationService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Presentation not found"
        )
    PresentationService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=Presentation)
async def get_presentation(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = PresentationService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Presentation not found"
        )
    return find


@router.get("", response_model=List[Presentation])
async def get_all_presentation(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = PresentationService.get_all()
    return finds

@router.get("/get/talks", response_model=List[Presentation])
async def get_all_presentation_talks(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = PresentationService.get_all_talks()
    return finds


@router.patch("/{id}/points", response_model=Presentation)
async def update_presentation(
    id: PyObjectId,
    points: int,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = PresentationService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Presentation not found"
        )
    updated = PresentationService.update_presentation(id, points)
    return updated
