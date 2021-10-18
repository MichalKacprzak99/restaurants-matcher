from pydantic import BaseModel


class Person(BaseModel):
    name: str
    phone: str
    city: str
