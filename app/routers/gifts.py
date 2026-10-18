from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from fastapi.responses import HTMLResponse

from app.auth.auth import get_current_active_user
from app.core.roles import Roles
from app.models.gift import Gift, GiftInDB, RedeemGift
from app.models.user import UserInDB
from app.services.gift import GiftService, RedeemGiftService
from app.services.participant import ParticipantService
from app.services.redemption import RedemptionError, redeem_reward, send_redeem_email
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Gift)
async def insert_gift(
    gift: Gift,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    giftDB = GiftInDB(**gift.dict())
    giftDB.username_insert = current_user.username
    inserted = GiftService.insert(giftDB)
    return inserted


@router.delete("/id/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_gift(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = GiftService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Gift not found",
        )
    GiftService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/id/{id}", response_model=Gift)
async def get_gift(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = GiftService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Gift not found",
        )
    return find


@router.get("", response_model=List[Gift])
async def get_all_gift(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = GiftService.get_all()
    return finds


@router.get("/products", response_model=List[Gift])
async def get_all_gift_and_products(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = GiftService.get_all_gift_and_products()
    return finds


@router.get("/redeem/user", response_model=List[RedeemGift])
async def get_all_redeem_gift(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = RedeemGiftService.get_all()
    return finds


@router.get("/redeem/user/code", response_model=List[RedeemGift])
async def get_all_redeem_gift_by_participant(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = RedeemGiftService.get_all_by_participant(participant_control_code)
    return finds


@router.post("/redeem/user", response_model=RedeemGift)
async def redeem_point(
    participant_control_code: str,
    gift_id: PyObjectId,
    background_tasks: BackgroundTasks,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    if Roles.SWAG not in current_user.roles:
        return HTMLResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="User not authorized",
        )
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    try:
        redeem, product = redeem_reward(participant, gift_id, current_user.username)
    except RedemptionError as error:
        return HTMLResponse(status_code=error.status_code, content=error.message)
    background_tasks.add_task(
        send_redeem_email,
        participant,
        product,
        redeem.discount_code,
        redeem.download_url,
    )
    return redeem
