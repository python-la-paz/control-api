from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.control import Control, ControlInDB

from app.models.user import UserInDB
from app.services.control import ControlService
from app.services.location import LocationService
from app.services.participant import ParticipantService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


@router.post("", response_model=Control)
async def check(
    participant_control_code: str,
    location_id: PyObjectId,
    check: bool,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    if participant == False:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participants with same control code found",
        )

    location = LocationService.get(location_id)
    if location is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Location not found"
        )
    # check if participant is enable to enter in location
    if location_id not in participant.locations:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant is not enable to enter in this location",
        )

    # count check_in
    ins = ControlService.count_checks(participant_control_code, location_id, "in")
    outs = ControlService.count_checks(participant_control_code, location_id, "out")

    if ins == outs:
        if check:
            control = ControlInDB(
                participant_control_code=participant_control_code,
                location=location_id,
                location_name=location.name,
                control="in",
                date=datetime.now(),
                user_control=current_user.username,
            )
            control.username_insert = current_user.username
            inserted = ControlService.insert(control)
            return inserted
        else:
            return HTMLResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="Check in first before check out",
            )
    elif ins > outs:
        if check:
            return HTMLResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="Check in already done",
            )
        else:
            control = ControlInDB(
                participant_control_code=participant_control_code,
                location=location_id,
                location_name=location.name,
                control="out",
                date=datetime.now(),
                user_control=current_user.username,
            )
            control.username_insert = current_user.username
            inserted = ControlService.insert(control)
            return inserted
    else:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Check out inconsistent with check in",
        )


@router.get("", response_model=List[Control])
async def get_all_control(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = ControlService.get_all()
    return finds


@router.get("/code", response_model=List[Control])
async def get_all_control_by_participant(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = ControlService.get_all_by_participant(participant_control_code)
    return finds
