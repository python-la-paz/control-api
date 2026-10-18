import logging

import pymongo
from pymongo.errors import OperationFailure

from app.core import configuration

logger = logging.getLogger(__name__)

client = pymongo.MongoClient(configuration.APP_MONGO_URL)
db = client.get_database(configuration.APP_MONGO_DB)


def ensure_indexes() -> None:
    try:
        db.redeem_meals.create_index(
            "participant_control_code",
            unique=True,
            name="unique_meal_per_participant",
            partialFilterExpression={"disabled": False},
        )
        db.redeem_gifts.create_index(
            [("participant_control_code", 1), ("gift", 1)],
            unique=True,
            name="unique_single_gift_per_participant",
            partialFilterExpression={"disabled": False, "multiple": False},
        )
    except OperationFailure:
        # Usually existing duplicated data; the app keeps working with app-level checks
        logger.exception("Failed to create unique indexes")
