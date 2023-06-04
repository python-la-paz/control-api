from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.participant import Participant, ParticipantInDB

from app.models.user import UserInDB
from app.services.participant import ParticipantService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Participant)
async def insert_participant(
    participant: Participant,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participantDB = ParticipantInDB(**participant.dict())
    participantDB.username_insert = current_user.username
    inserted = ParticipantService.insert(participantDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_participant(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ParticipantService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    ParticipantService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=Participant)
async def get_participant(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ParticipantService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    return find


@router.get("", response_model=List[Participant])
async def get_all_participant(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = ParticipantService.get_all()
    return finds
