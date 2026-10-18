from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse

from app.auth.auth import get_current_active_user
from app.models.buy import BuyProduct, BuyProductInDB
from app.models.user import UserInDB
from app.services.buy import BuyService
from app.services.participant import ParticipantService
from app.services.product import ProductService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


@router.post("", response_model=BuyProduct)
async def insert_buy(
    buy: BuyProduct,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    buyDB = BuyProductInDB(**buy.dict())
    buyDB.username_insert = current_user.username
    inserted = BuyService.insert(buyDB)
    return inserted


@router.delete("/id/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_buy(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = BuyService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Buy not found",
        )
    BuyService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/id/{id}", response_model=BuyProduct)
async def get_buy(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = BuyService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Buy not found",
        )
    return find


@router.get("", response_model=List[BuyProduct])
async def get_all_buy(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = BuyService.get_all()
    return finds


@router.get("/participant", response_model=List[BuyProduct])
async def get_all_buy_by_participant_control_code(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = BuyService.get_by_participant_control_code(participant_control_code)
    return finds


@router.post("/participant", response_model=BuyProduct)
async def insert_buy_by_participant_control_code(
    participant_control_code: str,
    product_id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participant = ParticipantService.get(participant_control_code)
    if participant is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )

    product = ProductService.get_enable_to_buy(product_id)
    if product is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Product not found",
        )

    buyDB = BuyProductInDB(
        participant_control_code=participant_control_code,
        product=product.id,
        points=participant.points,
        username_insert=current_user.username,
        date_insert=datetime.utcnow(),
    )
    inserted = BuyService.insert(buyDB)
    return inserted
