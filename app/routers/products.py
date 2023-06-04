from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.product import Product, ProductInDB

from app.models.user import UserInDB
from app.services.product import ProductService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Product)
async def insert_product(
    product: Product,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    productDB = ProductInDB(**product.dict())
    productDB.username_insert = current_user.username
    inserted = ProductService.insert(productDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_product(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ProductService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Product not found"
        )
    ProductService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("", response_model=Product)
async def update_product(
    product: Product,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = ProductService.get(product.id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Product not found"
        )
    productDB = ProductInDB(**product.dict())
    productDB.username_update = current_user.username
    updated = ProductService.update(product.id, productDB)
    return updated


@router.get("/{id}", response_model=Product)
async def get_product(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ProductService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Product not found"
        )
    return find


@router.get("", response_model=List[Product])
async def get_all_product(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = ProductService.get_all()
    return finds
