from typing import List

from fastapi_utils.api_model import APIModel


class Friendship(APIModel):
    members: List[str]
