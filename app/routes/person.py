from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

import app.controllers.person as controller
from app.schemas import Person


router = APIRouter(prefix='/person',
                   tags=["person"],
                   )


@router.get(
    "/person_name={person_name}",
    status_code=HTTP_200_OK,
)
async def get_person(person_name: str) -> Person:
    return controller.get_person(person_name=person_name)


@router.get(
    "/",
    status_code=HTTP_200_OK,
)
async def get_all_persons() -> List[Person]:
    return controller.get_all_persons()


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
)
async def create_person(person: Person) -> Person:
    return controller.create_person(person=person)


@router.delete(
    "/",
    status_code=HTTP_200_OK,
)
async def delete_person(person_name: str):
    controller.delete_person(person_name=person_name)


@router.get(
    "/friends",
    status_code=HTTP_200_OK,
)
async def get_person_friends(person_name: str) -> List[Person]:
    return controller.get_person_friends(person_name=person_name)
