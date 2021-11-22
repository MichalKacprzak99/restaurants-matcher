from neo4j import GraphDatabase

from app.core.config import get_configuration

configuration = get_configuration()
Driver = GraphDatabase.driver(configuration.URI, auth=(configuration.DB_USER, configuration.DB_PASSWORD))
