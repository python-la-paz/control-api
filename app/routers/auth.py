from datetime import timedelta
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Response, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.models.token import Token
from app.models.user import User, UserInDB
from app.services.user import UserService
from app.auth.auth import create_access_token, get_current_active_user, get_current_username_admin, get_password_hash, verify_password
from app.core import configuration
ACCESS_TOKEN_EXPIRE_MINUTES = configuration.APP_ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=User)
async def register(username: str, password:str, confirm_password:str, email:str, given_name:str="", family_name:str=""):
    user = UserService.get_user(username)
    if user is not None:
        raise HTTPException(status_code=400, detail="Username already exists")
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Password and confirm password not match")
    hashed_password = get_password_hash(password)
    user = UserInDB(username=username, given_name=given_name, family_name=family_name, email=email, hashed_password=hashed_password)
    inserted = UserService.create_user(user)
    return inserted

@router.patch("/users/admin", response_model=User)
async def update_user_admin(username: str, admin: bool, current_user: Optional[dict] = Depends(get_current_username_admin)):
    user = UserService.get_user_active(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated = UserService.set_admin(user.username, admin)
    return updated

@router.patch("/users/editor", response_model=User)
async def update_user_admin(username: str, editor: bool, current_user: Optional[dict] = Depends(get_current_username_admin)):
    user = UserService.get_user_active(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated = UserService.set_editor(user.username, editor)
    return updated

@router.patch("/users/password/admin", response_model=User)
async def update_user_password_admin(username: str, password:str, confirm_password:str, current_user: Optional[dict] = Depends(get_current_username_admin)):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Password and confirm password not match")

    user = UserService.get_user_active(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    hashed_password = get_password_hash(password)
    updated = UserService.set_password(user.username, hashed_password)
    return updated

@router.patch("/users/password", response_model=User)
async def update_user_password(old_password:str, password:str, confirm_password:str, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Password and confirm password not match")
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    hashed_password = get_password_hash(password)
    updated = UserService.set_password(current_user.username, hashed_password)
    return updated

@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = UserService.get_user_active(form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.delete("/users", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_user(username: str, current_user: Optional[dict] = Depends(get_current_username_admin)):
    user = UserService.get_user_active(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    deleted = UserService.delete_user(username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user