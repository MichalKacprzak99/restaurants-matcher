from typing import List

from fastapi_utils.api_model import APIModel

from .cuisine import Cuisine
from .person import Person


class Restaurant(APIModel):
    name: str
    owner: Person
    cuisine: Cuisine
    ratings: List[int] = []
