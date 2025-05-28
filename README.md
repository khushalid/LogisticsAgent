# Logistics Agent

A system for managing and querying shipment data using Neo4j graph database, with multiple query generation strategies (RAG, No-Context, Few-Shot) and comprehensive evaluation.

## 📌 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Technical Implementation](#-technical-implementation)
- [Installation](#-installation)
- [Usage](#-usage)
- [Evaluation](#-evaluation)
- [Results](#-results)
- [Future Work](#-future-work)

## 🌟 Project Overview
**Objective**: Create an intelligent logistics agent that can:
- Convert natural language queries to Cypher
- Retrieve shipment data from Neo4j knowledge graph
- Evaluate different query generation strategies

**Why?** Demonstrate:
- Graph database capabilities for logistics
- Comparison of RAG vs traditional approaches
- Automated evaluation framework for NL-to-Cypher systems

## 🚀 Key Features
1. **Multi-Strategy Query Generation**
   - **No-Context Bot**: Pure LLM Cypher generation
   - **Few-Shot Bot**: Example-based learning
   - **RAG Bot**: Context-aware retrieval

2. **Evaluation Framework**
   - Cypher syntax accuracy
   - Execution correctness
   - Semantic similarity metrics

3. **Data Pipeline**
   - Automated Neo4j population
   - Train/test dataset splitting
   - Expected output generation

## 🛠 Technical Implementation

### Tech Stack
- **Database**: Neo4j
- **LLM**: OpenAI GPT-4
- **Evaluation**: deepeval
- **Vector Store**: FAISS
- **Language**: Python 3.12

### Directory Structure
├── bots/ # Query generation implementations
├── core/ # Database and evaluation core
├── data/ # Datasets and results
├── scripts/ # Data processing scripts
├── run.sh # Main execution script
└── requirements.txt # Dependencies


## 💻 Installation

1. **Clone Repository**
```python
git clone [your-repo-url]
cd [your-repo-name]
```

2. **Create and activate a virtual environment:**
```python
python -m venv env
source env/bin/activate # On Windows use `env\Scripts\activate`
```

3. **Install dependencies:**
```python
pip install -r requirements.txt
```

3. **Neo4j Setup**
- Option 1: Install via Neo4j Desktop (https://neo4j.com/download/)
  Create database with credentials:
    URI: `bolt://localhost:7687`
    User: `neo4j`
    Password: `yourpassword`
- Option 2: Docker
    ```
    docker run \
      --restart always \ 
      --publish=7474:7474 --publish=7687:7687 \
      -e NEO4J_AUTH=neo4j/yourpassword \
      neo4j:2025.04.0
    ```
  Access Neo4j browser at http://localhost:7474/ (login: neo4j / yourpassword)

4. **Environment Variables**
```
echo "OPENAI_API_KEY=your_openai_key" > .env
```
6. 




