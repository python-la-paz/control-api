from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.point import Point, PointInDB

from app.models.user import UserInDB
from app.services.point import PointService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()

#insert, delete, get, get_all
@router.post("", response_model=Point)
async def insert_point(point: Point, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    pointDB = PointInDB(**point.dict())
    inserted = PointService.insert(pointDB)
    return inserted

@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_point(id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = PointService.get(id)
    if find is None:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND, content="Point not found")
    PointService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{id}", response_model=Point)
async def get_point(id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = PointService.get(id)
    if find is None:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND, content="Point not found")
    return find

@router.get("", response_model=List[Point])
async def get_all_point(current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    finds = PointService.get_all()
    return finds

@router.patch("/{id}/value", response_model=Point)
async def update_point(id: PyObjectId, value: int, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    find = PointService.get(id)
    if find is None:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND, content="Point not found")
    updated = PointService.update_point(id, value)
    return updated
