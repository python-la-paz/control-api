from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.core.roles import Roles
from app.models.gift import Gift, GiftInDB, RedeemGift, RedeemGiftInDB

from app.models.user import UserInDB
from app.services.gift import GiftService, RedeemGiftService
from app.services.participant import ParticipantService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Gift)
async def insert_gift(
    gift: Gift, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    giftDB = GiftInDB(**gift.dict())
    giftDB.username_insert = current_user.username
    inserted = GiftService.insert(giftDB)
    return inserted


@router.delete("/id/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_gift(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = GiftService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Gift not found"
        )
    GiftService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/id/{id}", response_model=Gift)
async def get_gift(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = GiftService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Gift not found"
        )
    return find


@router.get("", response_model=List[Gift])
async def get_all_gift(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = GiftService.get_all()
    return finds

@router.get("/products", response_model=List[Gift])
async def get_all_gift_and_products(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = GiftService.get_all_gift_and_products()
    return finds


@router.get("/redeem/user", response_model=List[RedeemGift])
async def get_all_redeem_gift(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
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
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    if Roles.SWAG not in current_user.roles:
        return HTMLResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content="User not authorized"
        )
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    # search gift
    gift = GiftService.get(gift_id)
    if gift is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Gift not found"
        )
    if gift.multiple:
        already = RedeemGiftService.get_redeem_gift_by_participant(participant_control_code, gift_id)
        if already is not None:
            return HTMLResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content="Gift already redeemed"
            )
        
    # check if participant has enough points
    if participant.points < gift.points:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=f"Not enough points, participant has {participant.points} points"
        )
    # subtract points to participant
    participant = ParticipantService.subtract_points(participant.id, gift.points)

    # insert redeem gift
    redeem = RedeemGiftInDB(
        participant_control_code=participant_control_code,
        gift=gift_id,
        date=datetime.now(),
        user_control=current_user.username,
        username_insert=current_user.username,
    )
    redeem = RedeemGiftService.insert(redeem)
    return redeem
