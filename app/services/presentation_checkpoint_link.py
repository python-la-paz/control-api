from datetime import datetime, timedelta

from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.presentation import PresentationInDB
from app.models.presentation_checkpoint_link import PresentationCheckpointLinkInDB
from app.utils.link_code_generator import generate_unique_codes
from app.utils.mongo_validator import PyObjectId


class PresentationCheckpointLinkService:
    TABLE = db.presentation_checkpoint_links

    @classmethod
    def insert(
        cls,
        item: PresentationCheckpointLinkInDB,
    ) -> PresentationCheckpointLinkInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> PresentationCheckpointLinkInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return PresentationCheckpointLinkInDB(**deleted)
        else:
            return None

    @classmethod
    def update(
        cls,
        id: PyObjectId,
        item: PresentationCheckpointLinkInDB,
    ) -> PresentationCheckpointLinkInDB | None:
        item.date_update = datetime.utcnow()
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "date_insert"):
            delattr(item, "date_insert")
        if hasattr(item, "username_insert"):
            delattr(item, "username_insert")
        if hasattr(item, "disabled"):
            delattr(item, "disabled")
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": item.dict(by_alias=True)},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return PresentationCheckpointLinkInDB(**updated)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> PresentationCheckpointLinkInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return PresentationCheckpointLinkInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> list[PresentationCheckpointLinkInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [PresentationCheckpointLinkInDB(**item) for item in items]

    @classmethod
    def get_by_code(cls, code: str) -> PresentationCheckpointLinkInDB | None:
        item = cls.TABLE.find_one({"code": code, "disabled": False})
        if item is not None:
            return PresentationCheckpointLinkInDB(**item)
        return None

    @classmethod
    def active_link(
        cls,
        id: PyObjectId,
        start: datetime,
    ) -> PresentationCheckpointLinkInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is None:
            return None

        minutes = item.get("min_duration", 0)
        end = start + timedelta(minutes=minutes)
        update_data = {
            "active": True,
            "start_duration": start,
            "end_duration": end,
            "date_update": datetime.utcnow(),
        }

        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return PresentationCheckpointLinkInDB(**updated)
        return None

    @classmethod
    def deactivate_link(cls, id: PyObjectId) -> PresentationCheckpointLinkInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is None:
            return None

        if item.get("active", True) is False:
            return None

        update_data = {
            "active": False,
            "end_duration": datetime.utcnow(),
            "date_update": datetime.utcnow(),
        }

        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return PresentationCheckpointLinkInDB(**updated)
        return None

    @classmethod
    def update_code(
        cls,
        id: PyObjectId,
        code: str,
    ) -> PresentationCheckpointLinkInDB | None:
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"code": code, "date_update": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return PresentationCheckpointLinkInDB(**updated)
        return None

    @classmethod
    async def generate_links(
        cls,
        presentation: PresentationInDB,
    ) -> list[PresentationCheckpointLinkInDB]:
        cls.TABLE.update_many(
            {"presentation": presentation.id, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.utcnow()}},
        )
        codes = generate_unique_codes(
            cls.TABLE,
            quantity=presentation.attendance_checkpoints,
            column="code",
            other_conditions={"disabled": False},
        )
        links = []
        for checkpoint, code in enumerate(codes, start=1):
            link = PresentationCheckpointLinkInDB(
                presentation=presentation.id,
                checkpoint=checkpoint,
                code=code,
                active=False,
                disabled=False,
                min_duration=presentation.min_checkpoint_duration,
                points=presentation.checkpoint_point(checkpoint),
                date_insert=datetime.utcnow(),
            )
            if hasattr(link, "id"):
                delattr(link, "id")
            links.append(link)
        ids = cls.TABLE.insert_many([link.dict(by_alias=True) for link in links])
        links = cls.TABLE.find({"_id": {"$in": ids.inserted_ids}})
        return [PresentationCheckpointLinkInDB(**link) for link in links]
