from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from app.schemas.cuisine import Cuisine
import app.controllers.cuisine as controller

router = APIRouter(prefix='/cuisine',
                   tags=['cuisine'],
                   )


@router.get(
    "/cuisine_name={cuisine_name}",
    status_code=HTTP_200_OK,
)
async def get_cuisine(person_name: str) -> Cuisine:
    return controller.get_cuisine(person_name=person_name)


@router.get(
    "/",
    status_code=HTTP_200_OK,
)
async def get_all_cuisines() -> List[Cuisine]:
    return controller.get_all_cuisines()


@router.post(
    "/",
    status_code=HTTP_200_OK,
)
async def create_cuisine(cuisine: Cuisine) -> Cuisine:
    return controller.create_cuisine(cuisine=cuisine)


@router.delete(
    "/",
    status_code=HTTP_200_OK,
)
async def delete_cuisine(cuisine_name: str):
    controller.delete_cuisine(cuisine_name=cuisine_name)
