from datetime import datetime
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.user import User, UserInDB


class UserService:
    @staticmethod
    def get_user(username: str) -> UserInDB | None:
        ret = db.users.find_one({"username": username})
        if ret is not None:
            return UserInDB(**ret)
        else:
            return None
    @staticmethod
    def get_user_active(username: str) -> UserInDB | None:
        ret = db.users.find_one({"username": username, "disabled": False})
        if ret is not None:
            return UserInDB(**ret)
        else:
            return None
    
    @staticmethod
    def create_user(user: UserInDB) -> User:
        user.date_insert = datetime.utcnow()
        user.disabled = False
        user.id = db.users.insert_one(user.dict()).inserted_id
        inserted = User(**user.dict())
        inserted.id = user.id
        return inserted