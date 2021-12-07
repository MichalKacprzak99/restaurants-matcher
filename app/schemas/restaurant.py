from typing import List, Optional

from fastapi_utils.api_model import APIModel

from .cuisine import Cuisine
from .person import Person


class Restaurant(APIModel):
    name: str
    owner: Person
    cuisine: Cuisine
    city: str
    country: str
    ratings: List[int] = []
