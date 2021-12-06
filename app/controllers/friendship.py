from typing import List

from fastapi import HTTPException
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable

from app.controllers.person import _find_and_return_person
from app.db.driver import Driver
from app.schemas import Friendship


def get_friendships():
    with Driver.session() as session:
        result: List[Friendship] = session.read_transaction(_return_all_friendships)
    return result


def check_friendships(person_name: str, friend_name: str):
    with Driver.session() as session:
        is_friend: bool = session.read_transaction(_check_friendships, person_name, friend_name)
    return is_friend


def create_friendship(friendship: Friendship):
    with Driver.session() as session:
        if not all(list(map(lambda person: session.read_transaction(_find_and_return_person, person),
                            friendship.members))):
            raise HTTPException(status_code=404, detail="Cannot create friendship - wrong person names")

        session.write_transaction(_create_friendship, friendship)


def delete_friendship(person_name: str, friend_name: str):
    with Driver.session() as session:
        session.write_transaction(_delete_friendship, person_name, friend_name)


def _return_all_friendships(tx) -> List[Friendship]:
    query = (
        '''
        MATCH 
        (p1:Person)-[r:FRIEND_WITH]->(p2:Person) 
        RETURN [p1.name, p2.name] as friendship
        '''
    )
    result: Result = tx.run(query)
    try:
        return [Friendship(members=person.data()['friendship']) for person in result]
    except ServiceUnavailable as exception:
        raise exception


def _create_friendship(tx, friendship: Friendship):
    query = (
        '''
        MATCH (p1:Person {name: $person_name})
        MATCH (p2: Person {name: $friend_name})
        CREATE (p1)-[rel: FRIEND_WITH]->(p2)
        '''
    )
    tx.run(query, person_name=friendship.members[0], friend_name=friendship.members[1])


def _check_friendships(tx, person_name: str, friend_name: str) -> bool:
    query = (
        '''
        MATCH (p1:Person {name: $person_name})-[rel:FRIEND_WITH]-(p2:Person {name: $friend_name})
        RETURN CASE rel WHEN NULL THEN false ELSE true END as are_friends
        '''
    )

    result: Result = tx.run(query, person_name=person_name, friend_name=friend_name)
    try:
        return result.data()[0].get('are_friends')
    except ServiceUnavailable as exception:
        raise exception


def _delete_friendship(tx, person_name: str, friend_name: str):
    query = (
        '''
        MATCH (p1:Person {name: $person_name})-[rel:FRIEND_WITH]-(p2:Person {name: $friend_name})
        DETACH
        DELETE rel
        '''
    )
    tx.run(query, person_name=person_name, friend_name=friend_name)
