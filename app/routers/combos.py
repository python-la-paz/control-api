from datetime import datetime
from typing import Annotated, List, Union
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.combo import (
    Combo,
    ComboInDB,
    GiveCombo,
    GiveComboInDB,
    GiveComboRequest,
)

from app.models.user import UserInDB
from app.services.combo import ComboService, GiveComboService
from app.services.participant import ParticipantService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Combo)
async def insert_combo(
    combo: Combo, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    comboDB = ComboInDB(**combo.dict())
    inserted = ComboService.insert(comboDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
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


@router.get("/{id}", response_model=Combo)
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


# get gived combos
@router.get("/gived/{participant_control_code}", response_model=List[GiveCombo])
async def get_gived_combo(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participant = ParticipantService.get_by_control_code(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    finds = GiveComboService.search_by_participant(participant_control_code)
    return finds


# give combos
@router.post("/give", response_model=GiveCombo)
async def give_combo(
    give: GiveComboRequest,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participant = ParticipantService.get_by_control_code(give.participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    # exist combo
    combo = ComboService.get(give.combo_id)
    if combo is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Combo not found"
        )
    # exist combo in participant
    if give.combo_id not in participant.combos:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Combo not found in participant",
        )
    # participant already gived products in combo
    gived_products = GiveComboService.search_by_participant_and_combo(
        participant_control_code=give.participant_control_code, combo_id=give.combo_id
    )
    # exist products
    product_not_exist = []
    product_already_gived = []
    product_to_give = []
    products = list(dict.fromkeys(give.products_id))
    print(products)
    for product_id in products:
        if product_id not in combo.products:
            product_not_exist.append(product_id)
        else:
            gived_control = False
            for gived_product in gived_products:
                if product_id in gived_product.products:
                    gived_control = True
                    product_already_gived.append(product_id)
            if not gived_control:
                product_to_give.append(product_id)
    message = ""
    if len(product_not_exist) > 0:
        message += " Products not exist in combo."
    if len(product_already_gived) > 0:
        message += " Some Products already gived."
    if len(product_to_give) == 0:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="All Products already gived." + message,
        )
    give_combo = GiveComboInDB(
        participant_control_code=give.participant_control_code,
        combo=give.combo_id,
        products=product_to_give,
        username_insert=current_user.username,
        date=datetime.now(),
        user_control=current_user.username,
    )
    gived = GiveComboService.insert(give_combo)
    gived.message += message
    return gived
