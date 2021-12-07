from fastapi_utils.api_model import APIModel


class Person(APIModel):
    name: str
    phone: str
    city: str
    country: str
