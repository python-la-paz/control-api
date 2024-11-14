from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user, get_current_username_admin
from app.core.roles import Roles
from app.models.special_point import SpecialPoint, SpecialPointInDB, SpecialPointRedeemInDB
from app.models.user import UserInDB
from app.services.participant import ParticipantService
from app.services.special_point import SpecialPointService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=SpecialPoint)
async def insert_special_point(
    point: SpecialPoint, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    pointDB = SpecialPointInDB(**point.dict())
    pointDB.username_insert = current_user.username
    inserted = SpecialPointService.insert(pointDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_special_point(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = SpecialPointService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Special Point not found"
        )
    SpecialPointService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=SpecialPoint)
async def get_special_point(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = SpecialPointService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Point not found"
        )
    return find


@router.get("", response_model=List[SpecialPoint])
async def get_all_special_point(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = SpecialPointService.get_all()
    return finds

@router.get("/redeem/special", response_model=SpecialPoint)
async def insert_special_point_redeem(
    participant_control_code: str,
    special_point: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    if Roles.SPECIAL_POINT not in current_user.roles:
        return HTMLResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content="Unauthorized"
        )
    point = SpecialPointService.get(special_point)
    if point is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Special Point not found"
        )
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    
    if point.limit > 0:
        already_redeemed = SpecialPointService.get_redeems(participant_control_code, special_point)
        size_redeemed = len(already_redeemed)
        if size_redeemed >= point.limit:
            return HTMLResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content="Limit reached"
            )
    
    redeem = SpecialPointRedeemInDB(
        special_point=special_point,
        points=point.points,
        participant_control_code=participant_control_code,
        date=datetime.now(),
        user_control=current_user.username,
    )
    redeem.username_insert = current_user.username
    inserted = SpecialPointService.insert_redeem(redeem)
    participant = ParticipantService.add_points(participant.id, point.points)
    return inserted
