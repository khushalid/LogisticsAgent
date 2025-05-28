from abc import ABC, abstractmethod
from core.database import Neo4jConnector
from neo4j import GraphDatabase

class BaseBot(ABC):
    def __init__(self):
        self.db = Neo4jConnector("bolt://localhost:7687", "neo4j", "yourpassword")
    
    @abstractmethod
    def generate_cypher(self, natural_query: str) -> str:
        pass
    
    def execute_cypher(self, cypher_query):
       return self.db.execute_query(query=cypher_query)
    
    def get_schema(self):
        return self.db.get_schema()
    
    def write_evaluation_summary(self, report, bot_name, summary_file="data/evaluation_summary.txt"):
        with open(summary_file, "a") as f:
            f.write(f"\n📊 {bot_name} Evaluation Summary:\n")
            for metric, score in report.items():
                f.write(f"{metric.replace('_', ' ').title()}: {score:.2%}\n")
                print(f"{metric.replace('_', ' ').title()}: {score:.2%}")
            f.write("\n" + "="*40 + "\n")
