from pprint import pprint
from typing import List

from fastapi import APIRouter, Body, HTTPException, Query
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.models.person import Person
from app.db.driver import Driver

router = APIRouter()


@router.post(
    "/person",
    status_code=HTTP_201_CREATED,
    tags=["person"],
    response_model=Person
)
async def create(person: Person = Body(..., embed=True)):
    with Driver.session() as session:
        if session.read_transaction(_find_and_return_person, person.name):
            raise HTTPException(status_code=404, detail="Person exist")
        result: Person = session.write_transaction(_create_and_return_person, person)
    return result


@router.get(
    "/person/{person_name}",
    status_code=HTTP_200_OK,
    tags=["person"],
    response_model=Person
)
async def get_person(person_name: str = Query(...)):
    with Driver.session() as session:
        result: Person = session.read_transaction(_find_and_return_person, person_name)

    return result


@router.get(
    "/person",
    status_code=HTTP_200_OK,
    tags=["person"],
    response_model=List[Person]
)
async def get_all_person():
    with Driver.session() as session:
        result: List[Person] = session.read_transaction(_return_all_person)
    return result


@router.delete(
    "/person/{person_name}",
    status_code=HTTP_200_OK,
    tags=["person"],
)
async def delete_person(person_name: str = Query(...)):
    with Driver.session() as session:
        session.read_transaction(_delete_and_return_person, person_name)


def _delete_and_return_person(tx, person_name: str):
    query = (
        "MATCH (p:Person {name: $person_name}) DELETE p"
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
        return Person(**result.single()['p'])
    except ServiceUnavailable as exception:
        raise exception


def _return_all_person(tx) -> List[Person]:
    query = (
        "MATCH (p:Person) RETURN p"
    )
    result: Result = tx.run(query)
    try:
        return [Person(**person.data()['p']) for person in result]
    except ServiceUnavailable as exception:
        raise exception


def _create_and_return_person(tx, person: Person) -> Person:
    query = (
        "CREATE (p:Person {name:$name , city:$city, phone:$phone}) RETURN p"
    )
    result: Result = tx.run(query, **person.dict())
    try:
        return Person(**result.single()['p'])
    except ServiceUnavailable as exception:
        raise exception
