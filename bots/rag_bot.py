# bots/rag_bot.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from dotenv import load_dotenv
import pandas as pd
from base_bot import BaseBot
from scripts.generate_dataset import DatasetManager
from core.evaluator import CypherEvaluator
from langchain.chat_models import ChatOpenAI

load_dotenv()

class RagBot(BaseBot):
    def __init__(self):
        super().__init__()  # Initialize Neo4j connection from BaseBot
        self.vector_store = None
        self.evaluator = None
        self.llm = ChatOpenAI(model="gpt-4")

    def _prepare_vector_store(self, train_df: pd.DataFrame):
        """Create FAISS vector store from training data"""
        train_docs = [
            Document(
                page_content=f"Q: {row['question']}\nCypher: {row['cypher']}\nAnswer: {row['expected_output']}",
            )
            for _, row in train_df.iterrows()
        ]
        self.vector_store = FAISS.from_documents(train_docs, OpenAIEmbeddings())

    def generate_cypher(self, user_query: str) -> str:
        """Generate Cypher using RAG approach"""
        retriever = self.vector_store.as_retriever(search_type="similarity", k=3)
        context = "\n\n".join([doc.page_content for doc in retriever.get_relevant_documents(user_query)])
        
        prompt = f"""
        You are an expert Cypher query assistant. Given the following context:
        {context}
        
        User Query: {user_query}
        
        Return ONLY the Cypher query in this format:
        Cypher Query: <cypher>
        """
        response = self.llm.invoke(prompt)
        return response.content.split("Cypher Query: ")[-1].strip()
    
    def evaluate(self):
        """Evaluate on test dataset"""
        # 1. Load data
        dm = DatasetManager()
        train_df, test_df = dm.get_dataset()

        # 2. Prepare RAG components
        self._prepare_vector_store(train_df)
        
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
        eval_df.to_csv("data/rag_evaluation_results.csv", index=False)
        
        # Generate report
        report = self.evaluator.generate_report(eval_df)
        print("\n📊 RAG Bot Evaluation Summary:")
        self.write_evaluation_summary(report, "RAG Bot")

if __name__ == "__main__":
    bot = RagBot()
    bot.evaluate()
















# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.schema import Document
# from dotenv import load_dotenv
# import pandas as pd
# from scripts.generate_dataset import DatasetManager
# from core.evaluator import CypherEvaluator
# from langchain.chat_models import ChatOpenAI
# from chatbot import execute_cypher  # Assuming execute_cypher is defined here

# load_dotenv()

# # 1. Load data using generate_dataset
# dm = DatasetManager()
# train_df, test_df = dm.get_dataset()

# # 2. Prepare Vector Store
# train_docs = [
#     Document(
#         page_content=f"Q: {row['question']}\nCypher: {row['cypher']}\nAnswer: {row['expected_output']}",
#     )
#     for _, row in train_df.iterrows()
# ]
# vector_store = FAISS.from_documents(train_docs, OpenAIEmbeddings())

# # 3. Initialize Evaluator with test data
# evaluator = CypherEvaluator(test_df)

# # 4. Query RAG and Evaluate
# def generate_with_rag(user_query):
#     retriever = vector_store.as_retriever(search_type="similarity", k=3)
#     retrieved = retriever.get_relevant_documents(user_query)
#     context = "\n\n".join([doc.page_content for doc in retrieved])
    
#     prompt = f"""
#     You are an expert Cypher query assistant. Given the following context:
#     {context}
    
#     User Query: {user_query}
    
#     Return ONLY the Cypher query in this format:
#     Cypher Query: <cypher>
#     """
#     llm = ChatOpenAI(model="gpt-4")
#     response = llm.invoke(prompt)
#     return response.content.split("Cypher Query: ")[-1].strip()

# bot_results = []
# for _, row in test_df.iterrows():
#     try:
#         # Generate Cypher
#         llm_cypher = generate_with_rag(row['question'])
        
#         # Execute query
#         llm_answer = execute_cypher(llm_cypher)
        
#         # Collect results
#         bot_results.append({
#             'question': row['question'],
#             'generated_cypher': llm_cypher,
#             'generated_answer': llm_answer
#         })
#     except Exception as e:
#         print(f"Error processing {row['question']}: {str(e)}")

# # 5. Perform Evaluation
# eval_df = evaluator.evaluate(bot_results)
# eval_df.to_csv("data/rag_evaluation_results.csv", index=False)

# # 6. Generate and print report
# report = evaluator.generate_report(eval_df)
# print("\n📊 RAG Bot Evaluation Summary:")
# for metric, score in report.items():
#     print(f"{metric.replace('_', ' ').title()}: {score:.2%}")