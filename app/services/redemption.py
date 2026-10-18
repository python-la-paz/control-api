from datetime import datetime

from fastapi import status
from pymongo.errors import DuplicateKeyError

from app.models.gift import RedeemGiftInDB
from app.models.meal import RedeemMealInDB
from app.models.participant import ParticipantInDB
from app.models.product import ProductInDB
from app.services.gift import GiftService, RedeemGiftService
from app.services.meal import RedeemMealService
from app.services.participant import ParticipantService
from app.services.product import ProductService
from app.utils.mailer import send_email
from app.utils.mongo_validator import PyObjectId


class RedemptionError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _deliver(product: ProductInDB, control_code: str) -> str | None:
    """Reserve one unit of stock; returns the assigned discount code, if any."""
    if product.kind == "discount_code":
        code = ProductService.assign_code(product.id, control_code)
        if code is None:
            raise RedemptionError("Out of stock")
        return code
    if not ProductService.reserve_stock(product.id):
        raise RedemptionError("Out of stock")
    return None


def _download_url(product: ProductInDB) -> str | None:
    if product.kind == "digital_file" and product.file_url:
        return product.file_url
    return None


def _release(product: ProductInDB, discount_code: str | None) -> None:
    if discount_code:
        ProductService.release_code(product.id, discount_code)
    else:
        ProductService.release_stock(product.id)


def redeem_reward(
    participant: ParticipantInDB,
    gift_id: PyObjectId,
    user_control: str,
    virtual: bool = False,
) -> tuple[RedeemGiftInDB, ProductInDB]:
    gift = GiftService.get(gift_id)
    if gift is None:
        raise RedemptionError("Reward not found", status.HTTP_404_NOT_FOUND)
    if not gift.multiple and RedeemGiftService.get_redeem_gift_by_participant(
        participant.control_code,
        gift_id,
    ):
        raise RedemptionError("Reward already redeemed")
    if participant.points < gift.points:
        raise RedemptionError(
            f"Not enough points, participant has {participant.points} points",
        )
    product = ProductService.get(gift.product)
    if product is None:
        raise RedemptionError("Product not found", status.HTTP_404_NOT_FOUND)
    if virtual and product.kind == "physical":
        raise RedemptionError("Reward not available for virtual redemption")

    discount_code = _deliver(product, participant.control_code)
    redeem = RedeemGiftInDB(
        participant_control_code=participant.control_code,
        gift=gift_id,
        date=datetime.now(),
        user_control=user_control,
        username_insert=user_control,
        product=product.id,
        discount_code=discount_code,
        download_url=_download_url(product),
        multiple=gift.multiple,
    )
    try:
        inserted = RedeemGiftService.insert(redeem)
    except DuplicateKeyError:
        _release(product, discount_code)
        raise RedemptionError("Reward already redeemed")
    ParticipantService.subtract_points(participant.id, gift.points)
    return inserted, product


def redeem_virtual_gift(
    participant: ParticipantInDB,
    user_control: str,
) -> tuple[RedeemMealInDB, ProductInDB]:
    if RedeemMealService.get_by_participant(participant.control_code):
        raise RedemptionError("Participant already redeemed gift")
    product = ProductService.get_virtual_meal()
    if product is None:
        raise RedemptionError("Virtual meal not available", status.HTTP_404_NOT_FOUND)

    discount_code = _deliver(product, participant.control_code)
    redeem = RedeemMealInDB(
        participant_control_code=participant.control_code,
        date=datetime.now(),
        user_control=user_control,
        username_insert=user_control,
        product=product.id,
        discount_code=discount_code,
        download_url=_download_url(product),
    )
    try:
        return RedeemMealService.insert(redeem), product
    except DuplicateKeyError:
        _release(product, discount_code)
        raise RedemptionError("Participant already redeemed gift")


def send_redeem_email(
    participant: ParticipantInDB,
    product: ProductInDB,
    discount_code: str | None,
    download_url: str | None,
) -> None:
    if not discount_code and not download_url:
        return
    lines = [f"Hola {participant.name},", "", f"Canjeaste: {product.name}"]
    if product.description:
        lines.append(product.description)
    if discount_code:
        lines.append(f"Tu código: {discount_code}")
    if download_url:
        lines.append(f"Descarga tu archivo aquí: {download_url}")
    send_email(participant.mail, f"Tu canje: {product.name}", "\n".join(lines))
