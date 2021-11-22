from typing import List

from fastapi import APIRouter, HTTPException
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable


from app.schemas.cuisine import Cuisine
from app.db.driver import Driver

router = APIRouter(prefix='/cuisine',
                   tags=['cuisine'],
                   )


def get_cuisine(cuisine_name: str) -> Cuisine:
    with Driver.session() as session:
        result: Cuisine = session.read_transaction(_find_and_return_cuisine, cuisine_name)
        if not result:
            raise HTTPException(status_code=404, detail="Not found")

    return result


def get_all_cuisines() -> List[Cuisine]:
    with Driver.session() as session:
        result: List[Cuisine] = session.read_transaction(_return_all_cuisines)
    return result


def create_cuisine(cuisine: Cuisine) -> Cuisine:
    with Driver.session() as session:
        result: Cuisine = session.write_transaction(_create_and_return_cuisine, cuisine)
    return result


def delete_cuisine(cuisine_name: str):
    with Driver.session() as session:
        session.write_transaction(_delete_cuisine, cuisine_name)


def _create_and_return_cuisine(tx, cuisine: Cuisine) -> Cuisine:
    query = (
        "CREATE (c:Cuisine {name:$name) ",
        "RETURN c"
    )
    result: Result = tx.run(query, **cuisine.dict())
    try:
        return Cuisine(**result.single()['c'])
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
        "DETACH "
        "DELETE c"
    )
    tx.run(query, cuisine_name=cuisine_name)


def _find_and_return_cuisine(tx, cuisine_name: str) -> Cuisine:
    query = (
        "MATCH (c:Cuisine) "
        "WHERE c.name = $cuisine_name "
        "RETURN c"
    )
    result: Result = tx.run(query, cuisine_name=cuisine_name)
    try:
        cuisine_data = result.single()
        if cuisine_data:
            return Cuisine(**cuisine_data['c'])
    except ServiceUnavailable as exception:
        raise exception
