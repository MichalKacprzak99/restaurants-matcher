from neo4j import GraphDatabase

from app.core.config import get_settings

settings = get_settings()
Driver = GraphDatabase.driver(settings.URI, auth=(settings.DB_USER, settings.DB_PASSWORD))
