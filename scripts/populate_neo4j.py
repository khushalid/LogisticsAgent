
# scripts/populate_neo4j.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import argparse
from core.database import Neo4jConnector

class Neo4jPopulator:
    def __init__(self, uri, user, password):
        self.connector = Neo4jConnector(uri, user, password)
    
    def create_graph(self, tx, shipment):
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
    
    def get_shipment_details(self, tracking_number):
        with self.connector.driver.session() as session:
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
            return result.single()

def main(args):
    populator = Neo4jPopulator("bolt://localhost:7687", "neo4j", args.password)
    
    if args.clear:
        print("🚀 Clearing existing data...")
        populator.connector.clear_database()
    
    print("📦 Loading shipment data...")
    with open(args.input, "r") as f:
        shipments = json.load(f)
    
    with populator.connector.driver.session() as session:
        for shipment in shipments:
            session.execute_write(populator.create_graph, shipment)
    
    print("✅ Data loaded into Neo4j!")
    
    # Example verification
    if args.verify:
        sample = shipments[0]['tracking_number']
        result = populator.get_shipment_details(sample)
        print(f"\n🔍 Sample verification for {sample}:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Populate Neo4j with shipment data')
    parser.add_argument('--input', default='data/shipments.json', help='Input JSON file')
    parser.add_argument('--password', required=True, help='Neo4j password')
    parser.add_argument('--clear', action='store_true', help='Clear existing data')
    parser.add_argument('--verify', action='store_true', help='Verify sample data')
    args = parser.parse_args()
    
    main(args)
