from typing import List

from fastapi import APIRouter
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable
from starlette.status import HTTP_200_OK

from app.models.cuisine import Cuisine
from app.db.driver import Driver

router = APIRouter(prefix='/cuisine',
                   tags=['cuisine'],
                   )


@router.get(
    "/",
    status_code=HTTP_200_OK,
)
async def get_all_cuisines() -> List[Cuisine]:
    with Driver.session() as session:
        result: List[Cuisine] = session.read_transaction(_return_all_cuisines)
    return result


@router.post(
    "/",
    status_code=HTTP_200_OK,
)
async def create_cuisine(cuisine: Cuisine) -> Cuisine:
    with Driver.session() as session:
        result: Cuisine = session.write_transaction(_create_and_return_cuisine, cuisine)
    return result


@router.delete(
    "/",
    status_code=HTTP_200_OK,
)
async def delete_cuisine(cuisine_name: str) -> Cuisine:
    with Driver.session() as session:
        result: Cuisine = session.write_transaction(_delete_cuisine, cuisine_name)
    return result


def _create_and_return_cuisine(tx, cuisine: Cuisine) -> Cuisine:
    query = (
        "CREATE (c:Cuisine {name:$name) ",
        "RETURN c"
    )
    result: Result = tx.run(query, **cuisine.dict())
    try:
        return Cuisine(**result.single()['p'])
    except ServiceUnavailable as exception:
        raise exception


def _return_all_cuisines(tx) -> List[Cuisine]:
    query = (
        "MATCH (c:Cuisine) "
        "RETURN c"
    )
    result: Result = tx.run(query)
    try:
        return [Cuisine(**cuisine.data()['c']) for cuisine in result]
    except ServiceUnavailable as exception:
        raise exception


def _delete_cuisine(tx, cuisine_name: str):
    query = (
        "MATCH (c:Cuisine {name: $cuisine_name}) "
        "DELETE c"
    )
    tx.run(query, cuisine_name=cuisine_name)