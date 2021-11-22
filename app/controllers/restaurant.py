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
        "DETACH "
        "DELETE r"
    )
    tx.run(query, restaurant_name=restaurant_name)


def _find_and_return_restaurant(tx, restaurant_name: str) -> Restaurant:
    query = (
        "MATCH"
        "(restaurant)-[:CUISINE]->(cuisine),"
        "(owner:Person)-[:OWNER]->(restaurant) "
        "WHERE restaurant.name = $restaurant_name "
        "RETURN restaurant, owner, cuisine"
    )
    result: Result = tx.run(query, restaurant_name=restaurant_name)
    try:
        restaurant = result.single()
        if restaurant:
            restaurant_data: dict = restaurant.data()
            name = restaurant_data.pop('restaurant').get('name')
            return Restaurant(name=name, **restaurant_data)
    except ServiceUnavailable as exception:
        raise exception


def _return_all_restaurants(tx) -> List[Restaurant]:
    query = (
        'MATCH'
        '(restaurant)-[:CUISINE]->(cuisine),'
        '(owner:Person)-[:OWNER]->(restaurant)'

        'RETURN restaurant, owner, cuisine'
    )
    result: Result = tx.run(query)
    try:
        restaurants: List[Restaurant] = []
        for restaurant in result:
            restaurant_data: dict = restaurant.data()
            name = restaurant_data.pop('restaurant').get('name')
            restaurants.append(Restaurant(name=name, **restaurant_data))

        return restaurants
    except ServiceUnavailable as exception:
        raise exception


def _create_and_return_restaurant(tx, restaurant: Restaurant) -> Restaurant:
    query = (
        "MATCH (p:Person {name: $owner_name}) "
        "MATCH (c:Cuisine {name: $cuisine_name}) "
        "CREATE (r:Restaurant {name:$restaurant_name}) "
        "CREATE (p)-[rel1: OWNER_OF]->(r)"
        "CREATE (r)-[rel2: SERVE_CUISINE]->(c)"
    )
    tx.run(query, restaurant_name=restaurant.name,
           owner_name=restaurant.owner.name,
           cuisine_name=restaurant.cuisine.name)
    try:
        return restaurant
    except ServiceUnavailable as exception:
        raise exception
