from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.point import Point, PointInDB

from app.models.user import UserInDB
from app.services.participant import ParticipantService
from app.services.point import PointService
from app.services.presentation import PresentationService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()

#insert, delete, get, get_all
@router.post("", response_model=Point)
async def insert_point(point: Point, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    pointDB = PointInDB(**point.dict())
    pointDB.username_insert = current_user.username
    inserted = PointService.insert(pointDB)
    return inserted

@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_point(id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = PointService.get(id)
    if find is None:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND, content="Point not found")
    PointService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{id}", response_model=Point)
async def get_point(id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = PointService.get(id)
    if find is None:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND, content="Point not found")
    return find

@router.get("", response_model=List[Point])
async def get_all_point(current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    finds = PointService.get_all()
    return finds

#redeem points
@router.post("/obtain", response_model=Point)
async def redeem_point(
    participant_control_code: str,
    presentation_id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    #search participant
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    #search presentation
    presentation = PresentationService.get(presentation_id)
    if presentation is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Presentation not found"
        )
    
    #participant enable to location
    if presentation.location not in participant.locations:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Participant not enable to this presentation"
        )
    
    #already change points in this presentation
    points = PointService.get_by_participant_and_presentation(participant_control_code, presentation_id)
    if points is not None:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Participant already change points in this presentation"
        )
    
    #add points to participant
    participant = ParticipantService.add_points(participant.id, presentation.points)

    #insert point
    point = PointInDB(
        participant_control_code= participant_control_code,
        presentation= presentation_id,
        points= presentation.points,
        date=datetime.now(),
        user_control=current_user.username
    )
    inserted = PointService.insert(point)
    return inserted