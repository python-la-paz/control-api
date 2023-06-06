from datetime import datetime
from typing import Annotated, List, Union
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.combo import (
    Combo,
    ComboInDB,
    RedeemCombo,
    RedeemComboInDB,
    RedeemComboRequest,
)

from app.models.user import UserInDB
from app.services.combo import ComboService, RedeemComboService
from app.services.participant import ParticipantService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Combo)
async def insert_combo(
    combo: Combo, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    comboDB = ComboInDB(**combo.dict())
    comboDB.username_insert = current_user.username
    inserted = ComboService.insert(comboDB)
    return inserted


@router.delete("/id/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_combo(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ComboService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Combo not found"
        )
    ComboService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("", response_model=Combo)
async def update_combo(
    combo: Combo, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ComboService.get(combo.id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Combo not found"
        )
    comboDB = ComboInDB(**combo.dict())
    comboDB.username_update = current_user.username
    updated = ComboService.update(combo.id, comboDB)
    return updated


@router.get("/id/{id}", response_model=Combo)
async def get_combo(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ComboService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Combo not found"
        )
    return find


@router.get("", response_model=List[Combo])
async def get_all_combo(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = ComboService.get_all()
    return finds

@router.get("/products", response_model=List[Combo])
async def get_all_combo_and_products(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = ComboService.get_all_and_products()
    return finds
@router.post("/products", response_model=List[Combo])
async def get_all_combo_and_products_by_ids(
    combos: List[PyObjectId],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = ComboService.get_all_and_products_by_ids(combos)
    return finds


# get redeemd combos
@router.get("/redeem/user/code", response_model=List[RedeemCombo])
async def get_redeemed_combo(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    finds = RedeemComboService.search_by_participant(participant_control_code)
    return finds


@router.get("/redeem/user", response_model=List[RedeemCombo])
async def get_all_redeemed_combo(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = RedeemComboService.get_all()
    return finds


# redeem combos
@router.post("/redeem/user", response_model=RedeemCombo)
async def redeem_combo(
    redeem: RedeemComboRequest,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participant = ParticipantService.get_by_control_code(
        redeem.participant_control_code
    )
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    # exist combo
    combo = ComboService.get(redeem.combo_id)
    if combo is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Combo not found"
        )
    # exist combo in participant
    if redeem.combo_id not in participant.combos:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Combo not found in participant",
        )
    # participant already redeemd products in combo
    redeemd_products = RedeemComboService.search_by_participant_and_combo(
        participant_control_code=redeem.participant_control_code,
        combo_id=redeem.combo_id,
    )
    # exist products
    product_not_exist = []
    product_already_redeemed = []
    product_to_redeem = []
    products = list(dict.fromkeys(redeem.products_id))
    print(products)
    for product_id in combo.products:
        if product_id not in combo.products:
            product_not_exist.append(product_id)
        else:
            redeemd_control = False
            for redeemd_product in redeemd_products:
                if product_id in redeemd_product.products:
                    redeemd_control = True
                    product_already_redeemed.append(product_id)
            if not redeemd_control:
                product_to_redeem.append(product_id)
    message = ""
    if len(product_not_exist) > 0:
        message += " Products not exist in combo."
    if len(product_already_redeemed) > 0:
        message += " Some Products already redeemed."
    if len(product_to_redeem) == 0:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="All Products already redeemed." + message,
        )
    redeem_combo = RedeemComboInDB(
        participant_control_code=redeem.participant_control_code,
        combo=redeem.combo_id,
        products=product_to_redeem,
        username_insert=current_user.username,
        date=datetime.now(),
        user_control=current_user.username,
    )
    redeemd = RedeemComboService.insert(redeem_combo)
    redeemd.message += message
    return redeemd
