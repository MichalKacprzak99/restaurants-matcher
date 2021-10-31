from typing import List

from fastapi import APIRouter, HTTPException
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.db.driver import Driver
from app.models import Person

router = APIRouter(prefix='/person',
                   tags=["person"],
                   )


@router.get(
    "/person_name={person_name}",
    status_code=HTTP_200_OK,
)
async def get_person(person_name: str) -> Person:
    with Driver.session() as session:
        result: Person = session.read_transaction(_find_and_return_person, person_name)
        if not result:
            raise HTTPException(status_code=404, detail="Not found")

    return result


@router.get(
    "/",
    status_code=HTTP_200_OK,
)
async def get_all_persons() -> List[Person]:
    with Driver.session() as session:
        result: List[Person] = session.read_transaction(_return_all_persons)
    return result


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
)
async def create_person(person: Person) -> Person:
    with Driver.session() as session:
        result: Person = session.write_transaction(_create_and_return_person, person)
    return result


@router.delete(
    "/",
    status_code=HTTP_200_OK,
)
async def delete_person(person_name: str):
    with Driver.session() as session:
        session.write_transaction(_delete_person, person_name)


@router.get(
    "/friends",
    status_code=HTTP_200_OK,
)
async def get_person_friends(person_name: str) -> List[Person]:
    with Driver.session() as session:
        result: List[Person] = session.read_transaction(_get_user_friends, person_name)
    return result


def _delete_person(tx, person_name: str):
    query = (
        "MATCH (p:Person {name: $person_name}) "
        "DELETE p"
    )
    tx.run(query, person_name=person_name)


def _find_and_return_person(tx, person_name: str) -> Person:
    query = (
        "MATCH (p:Person) "
        "WHERE p.name = $person_name "
        "RETURN p"
    )
    result: Result = tx.run(query, person_name=person_name)
    try:
        person_data = result.single()
        if person_data:
            return Person(**person_data['p'])
    except ServiceUnavailable as exception:
        raise exception


def _return_all_persons(tx) -> List[Person]:
    query = (
        "MATCH (p:Person) "
        "RETURN p"
    )
    result: Result = tx.run(query)
    try:
        return [Person(**person.data()['p']) for person in result]
    except ServiceUnavailable as exception:
        raise exception


def _create_and_return_person(tx, person: Person) -> Person:
    query = (
        "CREATE (p:Person {name:$name , city:$city, phone:$phone}) ",
        "RETURN p"
    )
    result: Result = tx.run(query, **person.dict())
    try:
        return Person(**result.single()['p'])
    except ServiceUnavailable as exception:
        raise exception


def _get_user_friends(tx, person_name: str) -> List[Person]:
    query = (
        "MATCH (:Person {name: $person_name})--(p:Person) "
        "RETURN p"
    )
    result: Result = tx.run(query, person_name=person_name)
    try:
        return [Person(**person.data()['p']) for person in result]
    except ServiceUnavailable as exception:
        raise exception
