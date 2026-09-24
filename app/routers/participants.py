import csv
import json
import logging
from datetime import datetime
from typing import Annotated, List, Optional

import requests
from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import HTMLResponse

from app.auth.auth import get_current_active_user, get_current_username_admin
from app.core.configuration import APP_USERS_API_TOKEN, APP_USERS_API_URL
from app.core.roles import Roles
from app.models.participant import Participant, ParticipantInDB
from app.models.user import UserInDB
from app.services.buy import BuyService
from app.services.combo import RedeemComboService
from app.services.control import ControlService
from app.services.gift import RedeemGiftService
from app.services.meal import RedeemMealService
from app.services.participant import ParticipantService
from app.services.point import PointService
from app.services.special_point import SpecialPointService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()
logger = logging.getLogger(__name__)


# insert, delete, get, get_all
@router.post("", response_model=Participant)
async def insert_participant(
    participant: Participant,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participantDB = ParticipantInDB(**participant.dict())
    participantDB.username_insert = current_user.username
    participantDB.birthday = participantDB.birthday.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    )
    inserted = ParticipantService.insert(participantDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_participant(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = ParticipantService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    ParticipantService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=Participant)
async def get_participant(
    id: PyObjectId,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = ParticipantService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    return find


@router.get("", response_model=List[Participant])
async def get_all_participant(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    finds = ParticipantService.get_all()
    return finds


@router.put("/{id}", response_model=Participant)
async def update_participant(
    id: PyObjectId,
    participant: Participant,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = ParticipantService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    participantDB = ParticipantInDB(**participant.dict())
    participantDB.username_update = current_user.username
    participantDB.birthday = participantDB.birthday.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    )
    updated = ParticipantService.update(id, participantDB)
    return updated


@router.post("/registration", response_model=Participant)
async def register_participant(
    ci: str,
    control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    if Roles.ACCREDITATION not in current_user.roles:
        return HTMLResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="User not authorized",
        )
    find = ParticipantService.get_by_ci(ci)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    if find.registration:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant already registered",
        )
    # search other use with the same control code
    exist = ParticipantService.exist_control_code(control_code)

    if exist:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Control code already exist in other user",
        )

    finish = ParticipantService.finish_registration(find.id, control_code)
    return finish


@router.post("/unregistration", response_model=Participant)
async def unregister_participant(
    control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    if Roles.REVOCATION not in current_user.roles:
        return HTMLResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="User not authorized",
        )
    find = ParticipantService.get_by_control_code(control_code)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    # search activity check in and checkouts
    points = PointService.exist_participant_control_code(control_code)
    if points:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant has points",
        )
    buys = BuyService.exist_participant_control_code(control_code)
    if buys:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant has buys",
        )
    combos = RedeemComboService.exist_participant_control_code(control_code)
    if combos:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant has combos",
        )
    control = ControlService.exist_participant_control_code(control_code)
    if control:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant has controls",
        )
    gifts = RedeemGiftService.exist_participant_control_code(control_code)
    if gifts:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant has redeemed gifts",
        )
    meals = RedeemMealService.exist_participant_control_code(control_code)
    if meals:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant has redeemed meals",
        )
    special = SpecialPointService.exist_participant_control_code(control_code)
    if special:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant has special points",
        )

    finish = ParticipantService.finish_unregistration(find.id, current_user.username)
    if finish is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    save_revoke = ParticipantService.save_revoke(
        finish.id,
        control_code,
        find.ci,
        current_user.username,
    )
    logger.info("Participant unregistration finished: %s", save_revoke)
    return finish


@router.get("/user/code", response_model=Participant)
async def get_participant_control_code(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    if Roles.INFORMATION not in current_user.roles:
        return HTMLResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="User not authorized",
        )
    find = ParticipantService.get_by_control_code_full(participant_control_code)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    if find is False:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Multiple participant with same control code found",
        )
    return find


@router.get("/user/code/ci", response_model=Participant)
async def get_participant_control_code_ci(
    ci: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    if Roles.INFORMATION not in current_user.roles:
        return HTMLResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="User not authorized",
        )
    find = ParticipantService.get_by_control_ci(ci)
    if not find:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    if not find.control_code:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Participant not registered",
        )
    find = ParticipantService.get_by_control_code_full(find.control_code)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Participant not found",
        )
    if find is False:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Multiple participant with same control code found",
        )
    return find


@router.get("/user/ci", response_model=Participant)
async def get_participant_ci(
    ci: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = ParticipantService.get_by_control_ci(ci)
    if find is None:
        headers = {
            "Authorization": APP_USERS_API_TOKEN,
            "Content-Type": "application/json",
        }
        response = requests.post(APP_USERS_API_URL + f"/{ci}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            parti = ParticipantInDB(
                mail=data["email"],
                name=data["given_name"] + " " + data["family_name"],
                #'birthday': '2003-06-17T04:00:00'
                birthday=datetime.strptime(data["birthday"].split("T")[0], "%Y-%m-%d"),
                gender=data["gender"],
                ci=data["dni"],
                profession=data["profession"],
                work_place=data["place_profession"],
                residence_place=data["residence"],
                photo=data["picture"],
                phone=data["phone"],
                t_shirt_size="",
                food_restrictions="",
            )
            parti.id = PyObjectId(data["_id"])
            ids = ParticipantService.insert_many([parti], delete_id=False)
            logger.info("Participant imported with ID: %s", ids)
            find = ParticipantService.get_by_control_ci(ci)
        else:
            return HTMLResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="Participant not found",
            )
    if find is False:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Multiple Participants with same ci found",
        )
    return find


# import file csv with participants
@router.post("/import")
async def upload_file(
    file: UploadFile,
    current_user: Optional[dict] = Depends(get_current_username_admin),
):
    # Check if the uploaded file is a CSV
    if file.filename.endswith(".csv"):
        # Read the CSV file and print the content of the cells
        csv_data = file.file.read().decode("utf-8")
        reader = csv.reader(csv_data.splitlines())
        list_participants = []
        for row in reader:
            # split row 12 using ;
            row_12 = row[12].split(";")
            row_13 = row[13].split(";")
            location_id = []
            for i in range(len(row_12)):
                if row_12[i] != "":
                    id = PyObjectId(row_12[i])
                    location_id.append(id)
            combos_id = []
            for i in range(len(row_13)):
                if row_13[i] != "":
                    id = PyObjectId(row_13[i])
                    combos_id.append(id)
            list_participants.append(
                ParticipantInDB(
                    mail=row[0],
                    name=row[1],
                    birthday=datetime.strptime(row[2], "%d/%m/%Y"),
                    gender=row[3],
                    ci=row[4],
                    profession=row[5],
                    work_place=row[6],
                    residence_place=row[7],
                    photo=row[8],
                    phone=row[9],
                    t_shirt_size=row[10],
                    food_restrictions=row[11],
                    locations=location_id,
                    combos=combos_id,
                ),
            )
        ids = ParticipantService.insert_many(list_participants)
        logger.info("Participants imported with IDs: %s", ids)

        return {"message": "File uploaded and data printed successfully."}

    else:
        return {"error": "Only CSV files are supported."}


@router.post("/migration")
async def migrate(current_user: Optional[dict] = Depends(get_current_username_admin)):
    # Consume API
    headers = {"Authorization": APP_USERS_API_TOKEN, "Content-Type": "application/json"}
    actual_ids = ParticipantService.get_all_ids()
    payload = json.dumps(actual_ids)
    response = requests.post(APP_USERS_API_URL, headers=headers, data=payload)
    data = response.json()
    participants = data["participants"]
    list_participants = []
    for participant in participants:
        parti = ParticipantInDB(
            id=PyObjectId(participant["_id"]),
            mail=participant["email"],
            name=participant["given_name"] + " " + participant["family_name"],
            #'birthday': '2003-06-17T04:00:00'
            birthday=datetime.strptime(
                participant["birthday"].split("T")[0],
                "%Y-%m-%d",
            ),
            gender=participant["gender"],
            ci=participant["dni"],
            profession=participant["profession"],
            work_place=participant["place_profession"],
            residence_place=participant["residence"],
            photo=participant["picture"],
            phone=participant["phone"],
            t_shirt_size="",
            food_restrictions="",
        )
        parti.id = PyObjectId(participant["_id"])
        list_participants.append(parti)
    if list_participants:
        ids = ParticipantService.insert_many(list_participants, delete_id=False)
        logger.info("Participants migrated with IDs: %s", ids)
        return True
    else:
        return False
