from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.core.roles import Roles
from app.models.meal import RedeemMeal, RedeemMealInDB

from app.models.user import UserInDB
from app.services.meal import RedeemMealService
from app.services.participant import ParticipantService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


@router.post("", response_model=RedeemMeal)
async def insert_redeem_meal(
    redeem_meal: RedeemMeal,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    redeem_mealDB = RedeemMealInDB(**redeem_meal.dict())
    redeem_mealDB.username_insert = current_user.username
    inserted = RedeemMealService.insert(redeem_mealDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_redeem_meal(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = RedeemMealService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="RedeemMeal not found"
        )
    RedeemMealService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=RedeemMeal)
async def get_redeem_meal(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = RedeemMealService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="RedeemMeal not found"
        )
    return find


@router.get("/redeem/user", response_model=List[RedeemMeal])
async def get_all_redeem_meal(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = RedeemMealService.get_all()
    return finds


@router.get("/redeem/user/code", response_model=List[RedeemMeal])
async def get_all_meal_by_participant(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    # search participant
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    finds = RedeemMealService.get_by_participant(participant_control_code)
    return finds


@router.post("/redeem/user", response_model=RedeemMeal)
async def redeem_meal(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    if Roles.LAUNCH not in current_user.roles:
        return HTMLResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content="User not authorized"
        )
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    finds = RedeemMealService.get_by_participant(participant_control_code)
    if len(finds) > 0:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant already redeemed meal",
        )
    redeem_meal = RedeemMealInDB(
        participant_control_code=participant_control_code,
        date=datetime.now(),
        user_control=current_user.username,
        username_insert=current_user.username,
    )
    inserted = RedeemMealService.insert(redeem_meal)
    return inserted
