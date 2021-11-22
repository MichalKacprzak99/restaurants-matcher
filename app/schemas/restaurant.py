from typing import Optional

from fastapi_utils.api_model import APIModel

from app.schemas.cuisine import Cuisine
from app.schemas.person import Person


# TODO temporary optional
class Restaurant(APIModel):
    name: str
    owner: Optional[Person]
    cuisine: Optional[Cuisine]
