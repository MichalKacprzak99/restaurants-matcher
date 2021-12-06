from typing import List

from neo4j import Result
from neo4j.exceptions import ServiceUnavailable

from app.db.driver import Driver
from app.schemas import Restaurant


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


def rate_restaurant(restaurant_name: str, rating: int):
    with Driver.session() as session:
        session.write_transaction(_rate_restaurant, restaurant_name, rating)


def _delete_restaurant(tx, restaurant_name: str):
    query = (
        '''
        MATCH (r:Restaurant {name: $restaurant_name})
        DETACH
        DELETE r
        '''
    )
    tx.run(query, restaurant_name=restaurant_name)


def _return_all_restaurants(tx) -> List[Restaurant]:
    query = (
        '''
        MATCH
        (owner:Person)-[:OWNER_OF]->(restaurant:Restaurant)-[:SERVE_CUISINE]->(cuisine:Cuisine)
        RETURN restaurant, owner, cuisine
        '''
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
        '''
        MATCH (p:Person {name: $owner_name})
        MATCH (c:Cuisine {name: $cuisine_name})
        CREATE (r:Restaurant {name:$restaurant_name, ratings: $ratings})
        CREATE (p)-[rel1: OWNER_OF]->(r)
        CREATE (r)-[rel2: SERVE_CUISINE]->(c)
        '''
    )
    tx.run(query,
           restaurant_name=restaurant.name,
           owner_name=restaurant.owner.name,
           cuisine_name=restaurant.cuisine.name,
           ratings=restaurant.ratings
           )
    try:
        return restaurant
    except ServiceUnavailable as exception:
        raise exception


def _rate_restaurant(tx, restaurant_name: str, rating: int):
    query = (
        '''
        MATCH (r:Restaurant {name: $restaurant_name})

        SET r.ratings =r.ratings + $rating
        '''
    )
    tx.run(query, restaurant_name=restaurant_name, rating=rating)
