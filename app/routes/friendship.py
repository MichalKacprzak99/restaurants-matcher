from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

import app.controllers.friendship as controller
from app.schemas import Friendship


router = APIRouter(prefix='/friendship',
                   tags=["friendship"],
                   )


@router.get(
    "/",
    status_code=HTTP_200_OK,
)
async def get_all_friendships():
    return controller.get_friendships()


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
)
async def create_friendship(friendship: Friendship):
    controller.create_friendship(friendship=friendship)


@router.delete(
    "/",
    status_code=HTTP_204_NO_CONTENT,
)
async def delete_friendship(person_name: str, friend_name: str):
    controller.delete_friendship(person_name=person_name, friend_name=friend_name)
