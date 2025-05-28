# import csv
# from neo4j import GraphDatabase

# # 1. Neo4j Connection Setup
# uri = "bolt://localhost:7687"
# username = "neo4j"
# password = "yourpassword"
# driver = GraphDatabase.driver(uri, auth=(username, password))

# # 2. Process CSV
# input_file = "cypher_eval.csv"
# output_file = "cypher_eval_with_results.csv"



# with driver.session() as session:
#     with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
#         reader = csv.DictReader(infile)
        
#         # Create new fieldnames with expected_output
#         fieldnames = reader.fieldnames + ['expected_output']
#         writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#         writer.writeheader()
        
#         for row in reader:
#             try:
#                 # Initialize expected_output in row
#                 row['expected_output'] = ''
                
#                 # Execute Cypher query
#                 result = session.execute_read(
#                     run_cypher,
#                     row['cypher']
#                 )
                
#                 # Format results
#                 formatted_results = []
#                 for record in result:
#                     formatted_results.append("; ".join(f"{k}:{v}" for k,v in record.items()))
                
#                 # Update expected_output
#                 row['expected_output'] = result
                
#             except Exception as e:
#                 row['expected_output'] = f"Error: {str(e)}"
            
#             writer.writerow(row)

# driver.close()
# print(f"Results written to {output_file}")


# scripts/generate_expected_output.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from core.database import Neo4jConnector

class QueryExecutor:
    def __init__(self, uri, user, password):
        self.connector = Neo4jConnector(uri, user, password)
    
    def run_cypher(self, tx, query):
        result = tx.run(query)
        return [dict(record) for record in result]
    
    def _execute_query(self, cypher_query):
        """Execute a single Cypher query and return formatted results"""
        try:
            with self.connector.driver.session() as session:
                return session.execute_read(
                        self.run_cypher,
                        cypher_query
                    )
        except Exception as e:
            return [f"Error: {str(e)}"]

    def process_csv(self, input_path, output_path):
        """Process CSV file and generate expected outputs"""
        with open(input_path, 'r') as infile, open(output_path, 'w', newline='') as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['expected_output']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                results = self._execute_query(row['cypher'])
                row['expected_output'] = results
                writer.writerow(row)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate expected outputs from Cypher queries')
    parser.add_argument('--input', default='data/cypher_eval.csv', help='Input CSV file')
    parser.add_argument('--output', default='data/cypher_eval_with_results.csv', help='Output CSV file')
    parser.add_argument('--neo4j-uri', default='bolt://localhost:7687', help='Neo4j connection URI')
    parser.add_argument('--neo4j-user', default='neo4j', help='Neo4j username')
    parser.add_argument('--neo4j-password', required=True, help='Neo4j password')
    
    args = parser.parse_args()
    
    executor = QueryExecutor(args.neo4j_uri, args.neo4j_user, args.neo4j_password)
    executor.process_csv(args.input, args.output)
    print(f"✅ Expected outputs generated at {args.output}")

if __name__ == "__main__":
    main()
