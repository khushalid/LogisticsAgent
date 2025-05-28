from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import DataFrameLoader
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from dotenv import load_dotenv
from rag_bot_eval import evaluate_row
import pandas as pd

load_dotenv()


# 1. Load and Split Data
import pandas as pd
df = pd.read_csv("cypher_eval_with_results.csv")
train_df = df.sample(frac=0.8)
test_df = df.drop(train_df.index)

# 2. Prepare Vector Store
train_docs = [
    Document(
        page_content=f"Q: {row['question']}\nCypher: {row['cypher']}\nAnswer: {row['expected_output']}",
    )
    for i, row in train_df.iterrows()
]
vector_store = FAISS.from_documents(train_docs, OpenAIEmbeddings())

# 3. Query RAG
def generate_with_rag(user_query):
    # Retrieve similar examples
    retriever = vector_store.as_retriever(search_type="similarity", k=3)
    retrieved = retriever.get_relevant_documents(user_query)
    context = "\n\n".join([doc.page_content for doc in retrieved])
    
    # Prompt LLM
    prompt = f"""
    You are an expert Cypher query assistant. Given the following user query and context, generate a Cypher query and a natural language answer.
    
    Context:\n{context}
    
    User Query: {user_query}
    
    Return format:
    Cypher Query: <cypher>
    """
    llm = ChatOpenAI(model="gpt-4")
    response = llm.invoke(prompt)
    return response

# 4. Evaluate on Test Set
results = []
for index, row in test_df.iterrows():
    llm_response = generate_with_rag(row['question'])
    print(row['question'])
    llm_cypher_query = llm_response.content.split("Cypher Query: ")[1]
    print(llm_cypher_query)
    results.append(evaluate_row(row, llm_cypher_query))
eval_df = pd.DataFrame(results)
eval_df.to_csv("rag_evaluation_results.csv", index=False)
summary = {
    'avg_cypher_relevancy_score': eval_df['cypher_relevancy_score'].mean(),
    'avg_cypher_correctness_score': eval_df['cypher_correctness_score'].mean(),
    'avg_answer_relevancy_score': eval_df['answer_relevancy_score'].mean(),
    'avg_answer_correctness_score': eval_df['answer_correctness_score'].mean(),
}
    
print("\n📊 Evaluation Summary:")
for k, v in summary.items():
    print(f"{k.replace('_', ' ').title()}: {v:.2%}")
    
"""
📊 Evaluation Summary:
Avg Cypher Relevancy Score: 92.26%
Avg Cypher Correctness Score: 78.49%
Avg Answer Relevancy Score: 93.75%
Avg Answer Correctness Score: 75.18%
"""
