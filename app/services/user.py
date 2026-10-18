from datetime import datetime

from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.user import User, UserInDB


class UserService:
    TABLE = db.users

    @classmethod
    def get_user(cls, username: str) -> UserInDB | None:
        ret = cls.TABLE.find_one({"username": username})
        if ret is not None:
            return UserInDB(**ret)
        else:
            return None

    @classmethod
    def get_user_active(cls, username: str) -> UserInDB | None:
        ret = cls.TABLE.find_one({"username": username, "disabled": False})
        if ret is not None:
            return UserInDB(**ret)
        else:
            return None

    @classmethod
    def create_user(cls, user: UserInDB) -> User:
        user.date_insert = datetime.utcnow()
        user.disabled = False
        user.id = cls.TABLE.insert_one(user.dict()).inserted_id
        inserted = User(**user.dict())
        inserted.id = user.id
        return inserted

    @classmethod
    def set_admin(cls, username: str, admin: bool) -> User | None:
        ret = cls.TABLE.find_one_and_update(
            {"username": username, "disabled": False},
            {"$set": {"admin": admin}},
            return_document=ReturnDocument.AFTER,
        )
        if ret is not None:
            return User(**ret)
        else:
            return None

    @classmethod
    def set_editor(cls, username: str, editor: bool) -> User | None:
        ret = cls.TABLE.find_one_and_update(
            {"username": username, "disabled": False},
            {"$set": {"editor": editor}},
            return_document=ReturnDocument.AFTER,
        )
        if ret is not None:
            return User(**ret)
        else:
            return None

    @classmethod
    def set_password(cls, username: str, hashed_password: str) -> User | None:
        ret = cls.TABLE.find_one_and_update(
            {"username": username, "disabled": False},
            {"$set": {"hashed_password": hashed_password}},
            return_document=ReturnDocument.AFTER,
        )
        if ret is not None:
            return User(**ret)
        else:
            return None

    @classmethod
    def delete_user(cls, username: str) -> User | None:
        ret = cls.TABLE.find_one_and_update(
            {"username": username, "disabled": False},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if ret is not None:
            return User(**ret)
        else:
            return None
