from neo4j import GraphDatabase
from .base import AbstractRelationsHandler
from extractor.relations.base import Relation

class Neo4jHandler(AbstractRelationsHandler):
    """Saves relations to Neo4j."""
    def __init__(self, uri, user, password, clear=False):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.clear = clear

    def close(self):
        self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close()
        if (type is not None):
            print(value)
            return False
    
    @staticmethod
    def _clear_database(tx):
        tx.run("MATCH (n) DETACH DELETE n");
        return None

    @staticmethod
    def _create_relation(tx, relation: Relation):
        result = tx.run("MERGE (source:Node {name: $source}) " +
                        "MERGE (target:Node {name: $target})" +
                        "MERGE (source)-[relation:" + relation.rel + "]->(target)",
                        source=relation.source, target=relation.target)
        return None

    def handle(self, relations):
        with self.driver.session() as session:
            if(self.clear):
                session.write_transaction(self._clear_database)
            for relation in relations:
                session.write_transaction(self._create_relation, relation)

