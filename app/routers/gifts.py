from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.gift import Gift, GiftInDB

from app.models.user import UserInDB
from app.services.gift import GiftService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()

#insert, delete, get, get_all
@router.post("", response_model=Gift)
async def insert_gift(gift: Gift, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    giftDB = GiftInDB(**gift.dict())
    inserted = GiftService.insert(giftDB)
    return inserted

@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_gift(id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = GiftService.get(id)
    if find is None:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND, content="Gift not found")
    GiftService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{id}", response_model=Gift)
async def get_gift(id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = GiftService.get(id)
    if find is None:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND, content="Gift not found")
    return find

@router.get("", response_model=List[Gift])
async def get_all_gift(current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    finds = GiftService.get_all()
    return finds
