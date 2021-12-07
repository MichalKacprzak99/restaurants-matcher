from typing import List

from geopy import Nominatim
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable

from app.db.driver import Driver
from app.schemas import Person


def get_all_persons() -> List[Person]:
    with Driver.session() as session:
        result: List[Person] = session.read_transaction(_return_all_persons)
    return result


def create_person(person: Person) -> Person:
    with Driver.session() as session:
        result: Person = session.write_transaction(_create_and_return_person, person)
    return result


def delete_person(person_name: str):
    with Driver.session() as session:
        session.write_transaction(_delete_person, person_name)


def get_person_friends(person_name: str) -> List[Person]:
    with Driver.session() as session:
        result: List[Person] = session.read_transaction(_get_user_friends, person_name)
    return result


def _delete_person(tx, person_name: str):
    query = (
        '''
        MATCH (p:Person {name: $person_name})
        DETACH
        DELETE p
        '''
    )
    tx.run(query, person_name=person_name)


def _find_and_return_person(tx, person_name: str) -> Person:
    query = (
        '''
        MATCH (p:Person)
        WHERE p.name = $person_name
        RETURN p
        '''
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
        '''
        MATCH (p:Person)
        RETURN p
        '''
    )
    result: Result = tx.run(query)
    try:
        return [Person(**person.data()['p']) for person in result]
    except ServiceUnavailable as exception:
        raise exception


def _create_and_return_person(tx, person: Person) -> Person:
    geolocator = Nominatim(user_agent="Restaurant Matcher")
    location = geolocator.geocode(f'{person.city}, {person.country}')
    query = (
        '''
        CREATE (p:Person {name:$name, city:$city, country:$country, phone:$phone, 
        latitude:$latitude, longitude: $longitude})
        '''
    )
    tx.run(query,
           **person.dict(),
           latitude=location.latitude,
           longitude=location.longitude,
           )
    try:
        return person
    except ServiceUnavailable as exception:
        raise exception


def _get_user_friends(tx, person_name: str) -> List[Person]:
    query = (
        '''
        MATCH (:Person {name: $person_name})--(friend:Person)
        RETURN friend
        '''
    )
    result: Result = tx.run(query, person_name=person_name)
    try:
        return [Person(**person.data()['friend']) for person in result]
    except ServiceUnavailable as exception:
        raise exception
