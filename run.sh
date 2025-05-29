#!/bin/bash

# Step 1: Clear and populate Neo4j
echo "🚀 Populating Neo4j database..."
python3 scripts/populate_neo4j.py \
    --password "yourpassword" \
    --clear \
    --input data/shipments.json \
    --verify

# Step 2: Generate expected output
echo "📊 Generating expected outputs..."
python3 scripts/generate_expected_output.py \
    --neo4j-password "yourpassword" \
    --input data/cypher_eval.csv \
    --output data/cypher_eval_with_results.csv

# Step 3: Train test split
echo "📊 Generating test dataset..."
python3 -m scripts.generate_dataset --test-size 0.2

# Step 4: Evaluate No Context Bot
echo "🤖 Evaluating No Context Bot..."
python3 bots/no_context_bot.py

# Step 5: Evaluate Few Shot Bot
echo "🤖 Evaluating Few Shot Bot..."
python3 bots/few_shot_bot.py

# Step 6: Evaluate RAG Bot
echo "🧠 Evaluating RAG Bot..."
python3 bots/rag_bot.py

echo "✅ All tasks completed!"
