import statistics
from typing import List, Optional

from geopy.geocoders import Nominatim
from neo4j import Result
from neo4j.exceptions import ServiceUnavailable

from app.db.driver import Driver
from app.schemas import Restaurant
from . import friendship as friendship_controller
from . import person as person_controller


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


def match_restaurant(first_person_name: str, second_person_name: str) -> Optional[Restaurant]:
    are_friends = friendship_controller.check_friendship(first_person_name, second_person_name)
    distance_weight: float = (2 - int(are_friends)) / 2
    first_person_friends = person_controller.get_person_friends(first_person_name)
    second_person_friends = person_controller.get_person_friends(second_person_name)
    common_friends = list(set(first_person_friends) & set(second_person_friends))

    try:
        friends_weight = 1 + 2 * len(common_friends) / (len(first_person_friends) + len(second_person_friends))
    except ZeroDivisionError:
        friends_weight = 1

    with Driver.session() as session:
        restaurant_average_travel_distances = session.read_transaction(
            _calculate_average_travel_distance_to_restaurants,
            first_person_name, second_person_name
        )
    if not restaurant_average_travel_distances:
        return None

    maximum_average_distance = max([d.get('average_travel_distance') for d in restaurant_average_travel_distances])

    def sort_by(d):
        return distance_weight * (d['average_travel_distance'] / maximum_average_distance) * \
               friends_weight * (statistics.mean(d['restaurant'].ratings) if d['restaurant'].ratings else 0)

    sorted_restaurants = sorted(restaurant_average_travel_distances, key=lambda d: sort_by(d), reverse=True)
    return sorted_restaurants[0]


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
            restaurants.append(Restaurant(**restaurant_data.pop('restaurant'), **restaurant_data))

        return restaurants
    except ServiceUnavailable as exception:
        raise exception


def _create_and_return_restaurant(tx, restaurant: Restaurant) -> Restaurant:
    geolocator = Nominatim(user_agent="Restaurant Matcher")
    location = geolocator.geocode(f'{restaurant.city}, {restaurant.country}')
    query = (
        '''
        MATCH (p:Person {name: $owner_name})
        MATCH (c:Cuisine {name: $cuisine_name})
        CREATE (r:Restaurant {name:$name, city:$city, country:$country, ratings: $ratings, 
        latitude:$latitude, longitude: $longitude})
        CREATE (p)-[rel1: OWNER_OF]->(r)
        CREATE (r)-[rel2: SERVE_CUISINE]->(c)
        '''
    )
    restaurant_data = restaurant.dict()
    tx.run(query,
           owner_name=restaurant_data.pop('owner').get('name'),
           cuisine_name=restaurant_data.pop('cuisine').get('name'),
           **restaurant_data,
           latitude=location.latitude,
           longitude=location.longitude,
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


def _calculate_average_travel_distance_to_restaurants(tx, first_person_name: str,
                                                      second_person_name: str) -> List[dict]:
    # TODO move point creating to node creating
    query = (
        '''
        MATCH (p1:Person {name: $first_person_name})
        MATCH (p2:Person {name: $second_person_name})
        MATCH (owner:Person)-[:OWNER_OF]->(restaurant:Restaurant)-[:SERVE_CUISINE]->(cuisine:Cuisine)
        WITH restaurant, owner, cuisine,
        point({longitude: p1.longitude, latitude: p1.latitude}) AS firstPersonPoint,
        point({longitude: p2.longitude, latitude: p2.latitude}) AS secondPersonPoint,
        point({longitude: restaurant.longitude, latitude: restaurant.latitude}) AS restaurantPoint
        WITH restaurant, owner, cuisine, 
        round(point.distance(firstPersonPoint,restaurantPoint)) AS firstPersonTravelDistance, 
        round(point.distance(secondPersonPoint,restaurantPoint)) AS secondPersonTravelDistance
        RETURN restaurant, owner, cuisine, 
        apoc.coll.avg([firstPersonTravelDistance, secondPersonTravelDistance]) as averageTravelDistance
        '''
    )
    result: Result = tx.run(query, first_person_name=first_person_name, second_person_name=second_person_name)
    try:
        average_travel_distances: List = []
        for row in result:
            row_data: dict = row.data()
            average_travel_distance = row_data.pop('averageTravelDistance')
            restaurant = Restaurant(**row_data.pop('restaurant'), **row_data)
            average_travel_distances.append({
                'average_travel_distance': average_travel_distance,
                'restaurant': restaurant
            })
        return average_travel_distances
    except ServiceUnavailable as exception:
        raise exception
