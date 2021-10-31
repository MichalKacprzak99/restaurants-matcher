from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.db.driver import Driver
from app.models import Friendship
from app.routes.person import _find_and_return_person

router = APIRouter(prefix='/friendship',
                   tags=["friendship"],
                   )


@router.get(
    "/check-friendship",
    status_code=HTTP_200_OK
)
async def check_friendships(person_name: str, friend_name: str):
    with Driver.session() as session:
        result: bool = session.read_transaction(_check_friendships, person_name, friend_name)
    return JSONResponse(status_code=200, content={"is_friend": result})


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
)
async def create_friendship(friendship: Friendship):
    with Driver.session() as session:
        if not all(list(map(lambda person: session.read_transaction(_find_and_return_person, person.name),
                            friendship.members))):
            raise HTTPException(status_code=404, detail="Cannot create friendship - wrong person names")

        session.write_transaction(_create_friendship, friendship)


@router.delete(
    "/",
    status_code=HTTP_200_OK,
)
async def delete_friendship(person_name: str, friend_name: str):
    with Driver.session() as session:
        session.write_transaction(_delete_friendship, person_name, friend_name)


def _create_friendship(tx, friendship: Friendship):
    query = (
        "MATCH (p1:Person {name: $person_name}) "
        "MATCH (p2: Person {name: $friend_name}) "
        "CREATE (p1)-[rel: IS_FRIENDS_WITH]->(p2)"
    )
    tx.run(query, person_name=friendship.members[0].name, friend_name=friendship.members[1].name)


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
