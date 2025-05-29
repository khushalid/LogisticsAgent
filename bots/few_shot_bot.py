import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_bot import BaseBot
from core.evaluator import CypherEvaluator
from scripts.generate_dataset import DatasetManager
import pandas as pd
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
example_query = """
        MATCH (s:Shipment {tracking_number: $tracking_number})
            OPTIONAL MATCH (s)-[:DISPATCHED_FROM]->(d_loc:Location)
            OPTIONAL MATCH (s)-[:DELIVERED_TO]->(del_loc:Location)
            OPTIONAL MATCH (s)-[:ASSIGNED_TO]->(courier:Courier)
            OPTIONAL MATCH (s)-[:BELONGS_TO]->(cust:Customer)
            RETURN s.tracking_number AS tracking_number, 
                   s.status AS status, 
                   s.dispatch_date AS dispatch_date, 
                   s.expected_delivery_date AS expected_delivery_date,
                   d_loc.name AS dispatch_location,
                   del_loc.name AS delivery_location,
                   courier.name AS courier,
                   cust.name AS customer
        -------------------------------------------------
        You: What is the status of shipment 1234?
        🛠️ Generated Cypher:
        MATCH (s:Shipment {tracking_number: "1234"}) RETURN s.status
        🤖 Bot: The status of shipment 1234 is "In Transit".
        -------------------------------------------------
        You: Where was shipment 5678 dispatched from?
        🛠️ Generated Cypher:
        MATCH (s:Shipment {tracking_number: "5678"})-[:DISPATCHED_FROM]->(l:Location) RETURN l.name
        🤖 Bot: Shipment 5678 was dispatched from New York.
        -------------------------------------------------
        You: what was the courier assiged to shipment 3141 
        MATCH (s:Shipment {tracking_number: '3141'})
            OPTIONAL MATCH (s)-[:ASSIGNED_TO]->(courier:Courier)
            RETURN courier.name AS courier_assigned
        🤖 Bot: The courier assigned to shipment 3141 was SwiftExpress.
        -------------------------------------------------
        You: List shipments expected to arrive after June 1, 2024
        MATCH (s:Shipment) WHERE s.expected_delivery_date > '2024-06-01' RETURN s.tracking_number
        RESULT: s.tracking_number:2595 | s.tracking_number:1072 | s.tracking_number:7731 | s.tracking_number:9897 | s.tracking_number:4000 | s.tracking_number:4003 | s.tracking_number:4006 | s.tracking_number:4007 | s.tracking_number:4009 | s.tracking_number:4019
        -------------------------------------------------
    """

class FewShotBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.evaluator = None
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.example_query = example_query

    def knowledge_graph_schema(self):
        nodes, relationships = self.get_schema()
        # Convert Schema to Text
        schema_text = f"""
        Graph Schema:

        Nodes:
        {nodes}

        Relationships:
        {relationships}
        """
        return schema_text
        
    def generate_cypher(self, natural_query: str) -> str:
        """Generate Cypher without RAG context"""
        system_prompt = f"""
                    "You are an expert in Neo4j Cypher queries. 
                    Given a user question and the schema, generate the correct Cypher query.
                    \n\nSchema:\n{self.knowledge_graph_schema()}. 
                    Here are few examples of cypher query you can refer to {self.example_query}. 
                    Make sure the tracking_number is a string and if not specifically asked about what details the user want just return the tracking number.
            """
        human_prompt = f"""
                    You are a Neo4j Cypher expert. Generate a query for:
                    {natural_query}
                    
                    Return ONLY the Cypher query in this format:
                    Cypher Query: <cypher>
            """
        messages = [
            ("system", system_prompt),
            ("human", human_prompt),
        ]
        
        response = self.llm.invoke(messages)
        return response.content.split("Cypher Query: ")[-1].strip()

    def evaluate(self):
        """Evaluate on test dataset"""
        # Load data
        dm = DatasetManager()
        _, test_df = dm.get_dataset()
        
        # Generate results
        bot_results = []
        for _, row in test_df.iterrows():
            try:
                cypher = self.generate_cypher(row['question'])
                result = self.execute_cypher(cypher)
                bot_results.append({
                    'question': row['question'],
                    'generated_cypher': cypher,
                    'generated_answer': result
                })
            except Exception as e:
                print(f"Error processing {row['question']}: {str(e)}")
        
        # Evaluate
        self.evaluator = CypherEvaluator(test_df)
        eval_df = self.evaluator.evaluate(bot_results)
        eval_df.to_csv("data/few_shot_results.csv", index=False)
        
        # Generate report
        report = self.evaluator.generate_report(eval_df)
        print("\n📊 Few Shot Bot Evaluation Summary:")
        self.write_evaluation_summary(report, "Few Shot Bot")
        

if __name__ == "__main__":
    bot = FewShotBot()
    bot.evaluate()