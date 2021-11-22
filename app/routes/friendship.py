from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

import app.controllers.friendship as controller
from app.schemas import Friendship


router = APIRouter(prefix='/friendship',
                   tags=["friendship"],
                   )


@router.get(
    "/check-friendship",
    status_code=HTTP_200_OK
)
async def check_friendships(person_name: str, friend_name: str):
    is_friend = controller.check_friendships(person_name=person_name, friend_name=friend_name)
    return JSONResponse(status_code=200, content={"is_friend": is_friend})


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
