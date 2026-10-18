from datetime import datetime

from app.core.database import db
from app.models.control import ControlInDB
from app.utils.mongo_validator import PyObjectId


class ControlService:
    TABLE = db.control

    @classmethod
    def insert(cls, item: ControlInDB) -> ControlInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def get_all(cls) -> list[ControlInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [ControlInDB(**item) for item in items]

    @classmethod
    def get_all_by_participant(cls, participant_control_code: str) -> list[ControlInDB]:
        items = cls.TABLE.find(
            {"participant_control_code": participant_control_code, "disabled": False},
        )
        return [ControlInDB(**item) for item in items]

    @classmethod
    def get_latest_check_in(
        cls,
        participant_control_code: str,
        location: PyObjectId,
    ) -> ControlInDB | None:
        item = cls.TABLE.find_one(
            {
                "participant_control_code": participant_control_code,
                "location": location,
                "control": "in",
                "disabled": False,
            },
            sort=[("date_insert", -1), ("_id", -1)],
        )
        if item is not None:
            return ControlInDB(**item)
        return None

    @classmethod
    def count_checks(
        cls,
        participant_control_code: str,
        location: PyObjectId,
        control: str,
    ) -> int:
        return cls.TABLE.count_documents(
            {
                "participant_control_code": participant_control_code,
                "location": location,
                "control": control,
                "disabled": False,
            },
        )

    @classmethod
    def count_in_and_outs_global(cls, participant_control_code: str) -> int:
        # 1: current in
        # 0: empty
        # -1: current out
        query = [
            {
                "$match": {
                    "disabled": False,
                    "participant_control_code": participant_control_code,
                },
            },
            {
                "$group": {
                    "_id": None,
                    "count_in_outs": {
                        "$sum": {"$cond": [{"$eq": ["$control", "in"]}, 1, -1]},
                    },
                },
            },
        ]
        items = cls.TABLE.aggregate(query)
        result = [dict(**item) for item in items]
        if result != []:
            return result[0]["count_in_outs"]
        else:
            return 0

    @classmethod
    def count_in_and_outs(
        cls,
        participant_control_code: str,
        location: PyObjectId,
    ) -> int:
        # 1: current in
        # 0: empty
        # -1: current out
        query = [
            {
                "$match": {
                    "disabled": False,
                    "participant_control_code": participant_control_code,
                    "location": location,
                },
            },
            {
                "$group": {
                    "_id": None,
                    "count_in_outs": {
                        "$sum": {"$cond": [{"$eq": ["$control", "in"]}, 1, -1]},
                    },
                },
            },
        ]
        items = cls.TABLE.aggregate(query)
        result = [dict(**item) for item in items]
        if result != []:
            return result[0]["count_in_outs"]
        else:
            return 0

    @classmethod
    def exist_participant_control_code(cls, participant_control_code: str) -> bool:
        items = cls.TABLE.count_documents(
            {"participant_control_code": participant_control_code, "disabled": False},
        )
        return items > 0
