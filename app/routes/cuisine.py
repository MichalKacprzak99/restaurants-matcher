from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.schemas.cuisine import Cuisine
import app.controllers.cuisine as controller

router = APIRouter(prefix='/cuisine',
                   tags=['cuisine'],
                   )

# TODO DELETE
@router.get(
    "/cuisine_name={cuisine_name}",
    status_code=HTTP_200_OK,
)
async def get_cuisine(cuisine_name: str) -> Cuisine:
    return controller.get_cuisine(cuisine_name=cuisine_name)


@router.get(
    "/",
    status_code=HTTP_200_OK,
)
async def get_all_cuisines() -> List[Cuisine]:
    return controller.get_all_cuisines()


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
)
async def create_cuisine(cuisine: Cuisine) -> Cuisine:
    return controller.create_cuisine(cuisine=cuisine)


@router.delete(
    "/",
    status_code=HTTP_204_NO_CONTENT,
)
async def delete_cuisine(cuisine_name: str):
    controller.delete_cuisine(cuisine_name=cuisine_name)
