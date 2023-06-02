from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from app.auth.auth import get_current_active_user
from app.models.combo import Combo, ComboInDB

from app.models.user import UserInDB
from app.services.combo import ComboService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()

#insert, delete, get, get_all
@router.post("", response_model=Combo)
async def insert_combo(combo: Combo, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    comboDB = ComboInDB(**combo.dict())
    inserted = ComboService.insert(comboDB)
    return inserted

@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_combo(id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = ComboService.get(id)
    if find is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Combo not found")
    ComboService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{id}", response_model=Combo)
async def get_combo(id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = ComboService.get(id)
    if find is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Combo not found")
    return find

@router.get("", response_model=List[Combo])
async def get_all_combo(current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    finds = ComboService.get_all()
    return finds
