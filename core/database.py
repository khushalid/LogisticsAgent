from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def execute_query(self, query, params=None):
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]   
    def get_schema(self):
        with self.driver.session() as session:
            result = session.run("CALL db.schema.visualization()")
            data = result.single()
            return data["nodes"], data["relationships"]   
    
    def clear_database(self):
        self.execute_query("MATCH (n) DETACH DELETE n")
