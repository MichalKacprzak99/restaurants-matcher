from typing import List

from fastapi_utils.api_model import APIModel

from app.models import Person


class Friendship(APIModel):
    members: List[Person]
