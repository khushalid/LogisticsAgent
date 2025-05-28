import os
from neo4j import GraphDatabase
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Neo4j Connection
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "yourpassword"))

# LLM (OpenAI Example)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, api_key=os.getenv("OPENAI_API_KEY"))

# Get Schema
def get_schema():
    with driver.session() as session:
        result = session.run("CALL db.schema.visualization()")
        data = result.single()
        return data["nodes"], data["relationships"]

nodes, relationships = get_schema()

# Convert Schema to Text
schema_text = f"""
Graph Schema:

Nodes:
{nodes}

Relationships:
{relationships}
"""

sample_cypher_query = """
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
"""
# Generate Cypher Query
def generate_cypher(user_question):
    system_prompt = f"""
                    "You are an expert in Neo4j Cypher queries. 
                    Given a user question and the schema, generate the correct Cypher query.
                    \n\nSchema:\n{schema_text}. 
                    Here is a sample cypher query you can refer to {sample_cypher_query}. 
                    Make sure the tracking_number is a string
    """
    system = SystemMessage(content=system_prompt)
    human = HumanMessage(content=f"User Question: {user_question}\nCypher Query:")
    response = llm([system, human])
    response = response.content.strip()
    print(response)
    cleaned = response.replace("```", "").strip()
    print(cleaned)
    return cleaned

# Execute Cypher
def execute_cypher(cypher_query):
    with driver.session() as session:
        result = session.run(cypher_query)
        return [record.data() for record in result]

# Generate Natural Response
def generate_natural_response(user_question, cypher_query, db_result):
    system_prompt = f"""
        You are a helpful assistant. 
        Given the user question, the Cypher query, and the database result, write a natural-sounding answer.
        If the user asks a questions about the business’s working hours, reply: We are open from 7 am to 6 pm, Monday to Friday."
    """
    system = SystemMessage(content=system_prompt)
    human = HumanMessage(content=f"User Question: {user_question}\nCypher Query: {cypher_query}\nDatabase Result: {db_result}\nAnswer:")
    response = llm([system, human])
    return response.content.strip()

# Main Chat Loop
def chat():
    print("🚀 Logistics Agent (type 'exit' to quit)")
    while True:
        user_question = input("\nYou: ")
        if user_question.lower() == "exit":
            break
        try:
            cypher_query = generate_cypher(user_question)
            print(f"🛠️ Generated Cypher:\n{cypher_query}")
            db_result = execute_cypher(cypher_query)
            response = generate_natural_response(user_question, cypher_query, db_result)
            print(f"🤖 Bot: {response}")
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    chat()
