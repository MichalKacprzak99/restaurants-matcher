from typing import List

from fastapi import APIRouter, HTTPException
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable
from fastapi.responses import JSONResponse

from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.models.person import Person
from app.db.driver import Driver
from app.routes.person import _find_and_return_person

router = APIRouter()


@router.get(
    "/friendship",
    status_code=HTTP_200_OK,
    tags=["friendship"],
)
async def get_person_friends(person_name: str) -> List[Person]:
    with Driver.session() as session:
        result: List[Person] = session.read_transaction(_get_user_friends, person_name)
    return result


@router.get(
    "/friendship/check-friendship",
    status_code=HTTP_200_OK,
    tags=["friendship"],
)
async def check_friendships(person_name: str, friend_name: str):
    with Driver.session() as session:
        result: bool = session.read_transaction(_check_friendships, person_name, friend_name)
    return JSONResponse(status_code=200, content={"is_friend": result})


@router.post(
    "/friendship",
    status_code=HTTP_201_CREATED,
    tags=["friendship"],
)
async def create_friendship(person_name: str, friend_name: str):
    with Driver.session() as session:
        validate_person_names = [
            session.read_transaction(_find_and_return_person, person_name),
            session.read_transaction(_find_and_return_person, friend_name)
        ]

        if not all(validate_person_names):
            raise HTTPException(status_code=404, detail="Cannot create friendship - wrong person names")

        session.write_transaction(_create_friendship, person_name, friend_name)


@router.delete(
    "/friendship",
    status_code=HTTP_200_OK,
    tags=["friendship"],
)
async def delete_friendship(person_name: str, friend_name: str):
    with Driver.session() as session:
        session.write_transaction(_delete_friendship, person_name, friend_name)


def _create_friendship(tx, person_name: str, friend_name: str):
    query = (
        "MATCH (p1:Person {name: $person_name}) "
        "MATCH (p2: Person {name: $friend_name}) "
        "CREATE (p1)-[rel: IS_FRIENDS_WITH]->(p2)"
    )
    tx.run(query, person_name=person_name, friend_name=friend_name)


def _get_user_friends(tx, person_name: str) -> List[Person]:
    query = (
        "MATCH (:Person {name: 'string'})--(p:Person) "
        "RETURN p"
    )
    result: Result = tx.run(query, person_name=person_name)
    try:
        return [Person(**person.data()['p']) for person in result]
    except ServiceUnavailable as exception:
        raise exception


def _check_friendships(tx, person_name: str, friend_name: str) -> bool:
    query = (
        "MATCH (p1:Person {name: $person_name})-[rel:IS_FRIENDS_WITH]-(p2:Person {name: $friend_name})"
        "RETURN CASE rel WHEN NULL THEN false ELSE true END as are_friends"
    )

    result: Result = tx.run(query, person_name=person_name, friend_name=friend_name)
    try:
        return result.data()[0].get('are_friends')
    except ServiceUnavailable as exception:
        raise exception


def _delete_friendship(tx, person_name: str, friend_name: str):
    query = (
        "MATCH (p1:Person {name: $person_name})-[rel:IS_FRIENDS_WITH]-(p2:Person {name: $friend_name})"
        "DELETE rel"
    )
    tx.run(query, person_name=person_name, friend_name=friend_name)
