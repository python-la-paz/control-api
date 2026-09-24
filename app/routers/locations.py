from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse

from app.auth.auth import get_current_active_user
from app.models.location import Location, LocationInDB
from app.models.user import UserInDB
from app.services.location import LocationService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Location)
async def insert_location(
    location: Location,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    locationDB = LocationInDB(**location.dict())
    locationDB.username_insert = current_user.username
    inserted = LocationService.insert(locationDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_location(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = LocationService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Location not found",
        )
    LocationService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=Location)
async def get_location(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = LocationService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Location not found",
        )
    return find


@router.get("", response_model=List[Location])
async def get_all_location(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = LocationService.get_all()
    return finds
