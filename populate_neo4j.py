from neo4j import GraphDatabase
import json

# Neo4j connection
uri = "bolt://localhost:7687"
username = "neo4j"
password = "yourpassword"  # replace with your password

driver = GraphDatabase.driver(uri, auth=(username, password))

# Load JSON data
with open("shipments.json", "r") as f:
    shipments = json.load(f)

def create_graph(tx, shipment):
    tx.run("""
        MERGE (s:Shipment {tracking_number: $tracking_number})
        SET s.status = $status, s.dispatch_date = $dispatch_date, s.expected_delivery_date = $expected_delivery_date
        FOREACH (_ IN CASE WHEN $status = "Delivered" THEN [1] ELSE [] END | 
            SET s.delivery_date = $delivery_date
        )

        MERGE (d_loc:Location {name: $dispatch_location})
        MERGE (del_loc:Location {name: $delivery_location})
        MERGE (cust:Customer {name: $customer})
        MERGE (courier:Courier {name: $courier})

        MERGE (s)-[:DISPATCHED_FROM]->(d_loc)
        MERGE (s)-[:DELIVERED_TO]->(del_loc)
        MERGE (s)-[:ASSIGNED_TO]->(courier)
        MERGE (s)-[:BELONGS_TO]->(cust)
    """, **shipment)

def get_shipment_details(tracking_number):
    with driver.session() as session:
        result = session.run("""
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
        """, tracking_number=tracking_number)
        
        shipment = result.single()
        if shipment:
            print(f"\n📦 Shipment {shipment['tracking_number']} Details:")
            print(f"  Status: {shipment['status']}")
            print(f"  Dispatch Date: {shipment['dispatch_date']}")
            print(f"  Expected Delivery Date: {shipment['expected_delivery_date']}")
            print(f"  Dispatch Location: {shipment['dispatch_location']}")
            print(f"  Delivery Location: {shipment['delivery_location']}")
            print(f"  Courier: {shipment['courier']}")
            print(f"  Customer: {shipment['customer']}")
        else:
            print(f"\n❌ Shipment {tracking_number} not found!")



# with driver.session() as session:
#     for shipment in shipments:
#         session.execute_write(create_graph, shipment)

# print("✅ Data loaded into Neo4j!")

# get_shipment_details("1234")

def get_schema(query):
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]
print(get_schema("MATCH (s:Shipment)-[r:DISPATCHED_FROM|DELIVERED_TO]->(l:Location) RETURN l.name as route, count(*) as count ORDER BY count DESC LIMIT 1"))


