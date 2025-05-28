import csv
from neo4j import GraphDatabase

# 1. Neo4j Connection Setup
uri = "bolt://localhost:7687"
username = "neo4j"
password = "yourpassword"
driver = GraphDatabase.driver(uri, auth=(username, password))

# 2. Process CSV
input_file = "cypher_eval.csv"
output_file = "cypher_eval_with_results.csv"

def run_cypher(tx, query):
    result = tx.run(query)
    return [dict(record) for record in result]

with driver.session() as session:
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        
        # Create new fieldnames with expected_output
        fieldnames = reader.fieldnames + ['expected_output']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                # Initialize expected_output in row
                row['expected_output'] = ''
                
                # Execute Cypher query
                result = session.execute_read(
                    run_cypher,
                    row['cypher']
                )
                
                # Format results
                formatted_results = []
                for record in result:
                    formatted_results.append("; ".join(f"{k}:{v}" for k,v in record.items()))
                
                # Update expected_output
                row['expected_output'] = result
                
            except Exception as e:
                row['expected_output'] = f"Error: {str(e)}"
            
            writer.writerow(row)

driver.close()
print(f"Results written to {output_file}")
