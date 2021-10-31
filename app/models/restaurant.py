from fastapi_utils.api_model import APIModel

from app.models.cuisine import Cuisine
from app.models.person import Person


class Restaurant(APIModel):
    cuisine: Cuisine
    name: str
    owner: Person
