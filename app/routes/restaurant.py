from typing import Dict, List, Optional

from fastapi import APIRouter, Body
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

import app.controllers.restaurant as controller
from app.schemas import Person, Restaurant

router = APIRouter(prefix='/restaurant',
                   tags=['restaurant'],
                   )


@router.get(
    "/",
    status_code=HTTP_200_OK,
)
async def get_all_restaurants() -> List[Restaurant]:
    return controller.get_all_restaurants()


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
)
async def create_restaurant(restaurant: Restaurant) -> Restaurant:
    return controller.create_restaurant(restaurant=restaurant)


@router.delete(
    "/",
    status_code=HTTP_204_NO_CONTENT,
)
async def delete_restaurant(restaurant_name: str):
    controller.delete_restaurant(restaurant_name=restaurant_name)


@router.post(
    "/rate",
)
async def rate_restaurant(restaurant_name: str, rating: int = Body(..., embed=True)):
    controller.rate_restaurant(restaurant_name=restaurant_name, rating=rating)


@router.get(
    "/match",
)
async def match_restaurant(first_person_name: str,
                           second_person_name: str) -> Optional[Restaurant]:
    return controller.match_restaurant(first_person_name=first_person_name,
                                       second_person_name=second_person_name)
