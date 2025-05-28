from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import DataFrameLoader
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()


# 1. Load and Split Data
import pandas as pd
df = pd.read_csv("cypher_eval_with_results.csv")
train_df = df.sample(frac=0.8, random_state=42)
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
for index, row in test_df.iterrows():
    llm_response = generate_with_rag(row['question'])
    print(f"User Query: {row['question']}")
    print(f"LLM Response: {llm_response}\n")
