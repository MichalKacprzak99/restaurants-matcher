from typing import List

from fastapi import HTTPException
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable


from app.db.driver import Driver
from app.schemas import Restaurant


def get_restaurant(restaurant_name: str) -> Restaurant:
    with Driver.session() as session:
        result: Restaurant = session.read_transaction(_find_and_return_restaurant, restaurant_name)
        if not result:
            raise HTTPException(status_code=404, detail="Not found")

    return result


def get_all_restaurants() -> List[Restaurant]:
    with Driver.session() as session:
        result: List[Restaurant] = session.read_transaction(_return_all_restaurants)
    return result


def create_restaurant(restaurant: Restaurant) -> Restaurant:
    with Driver.session() as session:
        result: Restaurant = session.write_transaction(_create_and_return_restaurant, restaurant)
    return result


def delete_restaurant(restaurant_name: str):
    with Driver.session() as session:
        session.write_transaction(_delete_restaurant, restaurant_name)


def _delete_restaurant(tx, restaurant_name: str):
    query = (
        "MATCH (r:Restaurant {name: $restaurant_name}) "
        "DELETE r"
    )
    tx.run(query, restaurant_name=restaurant_name)


def _find_and_return_restaurant(tx, restaurant_name: str) -> Restaurant:
    query = (
        "MATCH (r:Restaurant) "
        "WHERE r.name = $restaurant_name "
        "RETURN r"
    )
    result: Result = tx.run(query, restaurant_name=restaurant_name)
    try:
        restaurant_data = result.single()
        if restaurant_data:
            return Restaurant(**restaurant_data['r'])
    except ServiceUnavailable as exception:
        raise exception


def _return_all_restaurants(tx) -> List[Restaurant]:
    query = (
        "MATCH (r:Restaurant) "
        "RETURN r"
    )
    result: Result = tx.run(query)
    try:
        return [Restaurant(**person.data()['p']) for person in result]
    except ServiceUnavailable as exception:
        raise exception


def _create_and_return_restaurant(tx, restaurant: Restaurant) -> Restaurant:
    query = (
        "MATCH (p:Person {name: $owner_name}) "
        "MATCH (c:Cuisine {name: $cuisine_name}) "
        "CREATE (r:Restaurant {name:$restaurant_name}) "
        "CREATE (p)-[rel1: OWNER_OF]->(r)"
        "CREATE (r)-[rel2: SERVE_CUISINE]->(c)"
        "RETURN r"
    )
    result: Result = tx.run(query, restaurant_name=restaurant.name,
                            owner_name=restaurant.owner.name,
                            cuisine_name=restaurant.cuisine.name)
    try:
        return Restaurant(**result.single()['p'])
    except ServiceUnavailable as exception:
        raise exception



