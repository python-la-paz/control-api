import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, status
from fastapi.responses import HTMLResponse

from app.models.control import ControlInDB
from app.models.gift import SelfServiceGift
from app.models.participant import (
    ParticipantInDB,
    SelfServiceCheckRequest,
    SelfServiceParticipant,
    SelfServiceRedeem,
    SelfServiceRedeemRequest,
    SelfServiceRegisterRequest,
    SelfServiceResult,
)
from app.models.point import PointInDB
from app.services.control import ControlService
from app.services.gift import GiftService
from app.services.location import LocationService
from app.services.participant import ParticipantService
from app.services.point import PointService
from app.services.presentation import PresentationService
from app.services.presentation_checkpoint_link import PresentationCheckpointLinkService
from app.services.redemption import (
    RedemptionError,
    redeem_gift,
    redeem_virtual_meal,
    send_redeem_email,
)
from app.utils.control_code_generator import generate_name
from app.utils.qr_generator import qr_to_base64

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/registration", response_model=SelfServiceParticipant)
async def self_service_registration(register: SelfServiceRegisterRequest):
    ci = register.ci
    birthday = register.birthday
    birthday_datetime = datetime(birthday.year, birthday.month, birthday.day)
    find = ParticipantService.get_by_ci_and_birthday(ci=ci, birthday=birthday_datetime)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    if find.control_code or find.registration:
        control_code = find.control_code
    else:
        exist = False
        control_code = ""
        while not exist:
            control_code = generate_name()
            exist = not ParticipantService.exist_control_code(control_code)
        finish = ParticipantService.finish_registration(find.id, control_code)
        if not finish:
            return HTMLResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content="Failed to finish registration",
            )
    qr_image = qr_to_base64(control_code)
    participant = SelfServiceParticipant(
        control_code=control_code,
        qr_code=qr_image,
    )
    return participant


@router.get("/check/{code}", response_model=SelfServiceResult)
async def self_service_participation(code: str):

    find = PresentationCheckpointLinkService.get_by_code(code)
    if find is None:
        return HTMLResponse(
            "Presentation not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not find.active:
        return HTMLResponse(
            "Presentation not active",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    now = datetime.utcnow()
    if not find.start_duration or not find.end_duration:
        return HTMLResponse(
            "Presentation duration undefined",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if not (find.start_duration <= now <= find.end_duration):
        return HTMLResponse(
            "Presentation not within active duration",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return SelfServiceResult(
        control_code="",
        message="Presentation active",
    )


@router.post("/check/{code}", response_model=SelfServiceResult)
async def self_service_participation_register(
    code: str,
    checks: SelfServiceCheckRequest,
):
    control_code = checks.control_code
    find = PresentationCheckpointLinkService.get_by_code(code)
    if find is None:
        return HTMLResponse(
            "Presentation not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not find.active:
        return HTMLResponse(
            "Presentation not active",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    now = datetime.utcnow()
    if not find.start_duration or not find.end_duration:
        return HTMLResponse(
            "Presentation duration undefined",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if not (find.start_duration <= now <= find.end_duration):
        return HTMLResponse(
            "Presentation not within active duration",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    participant = ParticipantService.get_by_control_code(control_code)
    if participant is None:
        return HTMLResponse(
            "Participant not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not participant:
        return HTMLResponse(
            "Participants with same control code found",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    presentation = PresentationService.get(find.presentation)
    if presentation is None:
        return HTMLResponse(
            "Presentation not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    location = LocationService.get(presentation.location)
    if location is None:
        return HTMLResponse(
            "Location not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if PointService.exist_by_participant_and_checkpoint(control_code, find.id):
        return HTMLResponse(
            "Checkpoint already registered",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user_control = "self_service"
    in_and_outs = ControlService.count_in_and_outs(control_code, presentation.location)
    if in_and_outs <= 0:
        # Virtual attendance: auto check-in, unless checked in elsewhere
        if ControlService.count_in_and_outs_global(control_code) > 0:
            return SelfServiceResult(
                control_code=control_code,
                message="Current check in a location",
            )
        check_in = ControlInDB(
            participant_control_code=control_code,
            location=presentation.location,
            location_name=location.name,
            control="in",
            date=datetime.now(),
            user_control=user_control,
        )
        check_in.username_insert = user_control
        ControlService.insert(check_in)

    ParticipantService.add_points(participant.id, find.points)
    point = PointInDB(
        participant_control_code=control_code,
        presentation=presentation.id,
        points=find.points,
        date=datetime.now(),
        user_control=user_control,
        checkpoint_link=find.id,
    )
    point.username_insert = user_control
    PointService.insert(point)

    if find.checkpoint >= presentation.attendance_checkpoints:
        check_out = ControlInDB(
            participant_control_code=control_code,
            location=presentation.location,
            location_name=location.name,
            control="out",
            date=datetime.now(),
            user_control=user_control,
        )
        check_out.username_insert = user_control
        ControlService.insert(check_out)

    return SelfServiceResult(
        control_code=control_code,
        message="Checkpoint registered",
        points=find.points,
    )


def _get_self_service_participant(
    control_code: str,
    ci: str,
) -> ParticipantInDB | HTMLResponse:
    participant = ParticipantService.get_by_control_code(control_code)
    # Same message for unknown code and CI mismatch to avoid leaking valid codes
    if not isinstance(participant, ParticipantInDB) or participant.ci != ci:
        return HTMLResponse(
            content="Participant not found",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return participant


@router.get("/gifts", response_model=list[SelfServiceGift])
async def self_service_gifts():
    return GiftService.get_all_virtual()


@router.post("/redeem/gift", response_model=SelfServiceRedeem)
async def self_service_redeem_gift(
    redeem_request: SelfServiceRedeemRequest,
    background_tasks: BackgroundTasks,
):
    control_code = redeem_request.control_code
    ci = redeem_request.ci
    gift_id = redeem_request.gift
    participant = _get_self_service_participant(control_code, ci)
    if isinstance(participant, HTMLResponse):
        return participant
    try:
        redeem, product = redeem_gift(
            participant,
            gift_id,
            "self_service",
            virtual=True,
        )
    except RedemptionError as error:
        return HTMLResponse(
            content=error.message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    background_tasks.add_task(
        send_redeem_email,
        participant,
        product,
        redeem.discount_code,
        redeem.download_url,
    )
    return SelfServiceRedeem(
        control_code=control_code,
        message="Gift redeemed",
        product_name=product.name,
        discount_code=redeem.discount_code,
        download_url=redeem.download_url,
    )


@router.post("/redeem/meal", response_model=SelfServiceRedeem)
async def self_service_redeem_meal(
    redeem_request: SelfServiceRedeemRequest,
    background_tasks: BackgroundTasks,
):
    control_code = redeem_request.control_code
    ci = redeem_request.ci
    participant = _get_self_service_participant(control_code, ci)
    if isinstance(participant, HTMLResponse):
        return participant
    try:
        redeem, product = redeem_virtual_meal(participant, "self_service")
    except RedemptionError as error:
        return HTMLResponse(
            content=error.message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    background_tasks.add_task(
        send_redeem_email,
        participant,
        product,
        redeem.discount_code,
        redeem.download_url,
    )
    return SelfServiceRedeem(
        control_code=control_code,
        message="Meal redeemed",
        product_name=product.name,
        discount_code=redeem.discount_code,
        download_url=redeem.download_url,
    )
