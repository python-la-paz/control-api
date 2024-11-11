import csv
from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import HTMLResponse
from app.auth.auth import get_current_active_user
from app.models.participant import Participant, ParticipantInDB

from app.models.user import UserInDB
from app.services.participant import ParticipantService
from app.utils.mongo_validator import PyObjectId


router = APIRouter()


# insert, delete, get, get_all
@router.post("", response_model=Participant)
async def insert_participant(
    participant: Participant,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    participantDB = ParticipantInDB(**participant.dict())
    participantDB.username_insert = current_user.username
    inserted = ParticipantService.insert(participantDB)
    return inserted


@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_participant(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ParticipantService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    ParticipantService.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=Participant)
async def get_participant(
    id: PyObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ParticipantService.get(id)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    return find


@router.get("", response_model=List[Participant])
async def get_all_participant(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    finds = ParticipantService.get_all()
    return finds


@router.post("/registration", response_model=Participant)
async def register_participant(
    ci: str,
    control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = ParticipantService.get_by_ci(ci)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
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


@router.get("/user/code", response_model=Participant)
async def get_participant_control_code(
    participant_control_code: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    find = ParticipantService.get_by_control_code_full(participant_control_code)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    if find is False:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Multiple participant with same control code found",
        )
    return find


@router.get("/user/ci", response_model=Participant)
async def get_participant_ci(
    ci: str, current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    find = ParticipantService.get_by_control_ci(ci)
    if find is None:
        return HTMLResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Participant not found"
        )
    if find is False:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Multiple Participants with same ci found",
        )
    return find

#import file csv with participants
@router.post("/import")
async def upload_file(file: UploadFile):
    # Check if the uploaded file is a CSV
    if file.filename.endswith('.csv'):
        # Read the CSV file and print the content of the cells
        csv_data = file.file.read().decode("utf-8")
        reader = csv.reader(csv_data.splitlines())
        list_participants = []
        for row in reader:
            #split row 12 using ;
            row_12  = row[12].split(";")
            row_13  = row[13].split(";")
            # print (row_12,row_13)
            location_id = []
            for i in range(len(row_12)):
                if row_12[i] != "":
                    id = PyObjectId(row_12[i])
                    location_id.append(id)
            # print(location_id)
            combos_id = []
            for i in range(len(row_13)):
                if row_13[i] != "":
                    id = PyObjectId(row_13[i])
                    combos_id.append(id)
            # print(combos_id)
            list_participants.append(ParticipantInDB(
                mail=row[0],
                name=row[1],
                birthday=datetime.strptime(row[2], "%d/%m/%Y" ),
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
            ))
        ids = ParticipantService.insert_many(list_participants)
        print(ids)

        return {"message": "File uploaded and data printed successfully."}
    
    else:
        return {"error": "Only CSV files are supported."} 