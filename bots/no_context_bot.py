import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_bot import BaseBot
from core.evaluator import CypherEvaluator
from scripts.generate_dataset import DatasetManager
import pandas as pd
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class NoContextBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.evaluator = None
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
    def generate_cypher(self, natural_query: str) -> str:
        """Generate Cypher without RAG context"""
        prompt = f"""
        You are a Neo4j Cypher expert. Generate a query for:
        {natural_query}
        
        Return ONLY the Cypher query in this format:
        Cypher Query: <cypher>
        """
        response = self.llm.invoke(prompt)
        return response.content.split("Cypher Query: ")[-1].strip()

    def evaluate(self):
        """Evaluate on test dataset"""
        # Load data
        dm = DatasetManager()
        _, test_df = dm.get_dataset()
        
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
        eval_df.to_csv("data/no_context_results.csv", index=False)
        
        # Generate report
        report = self.evaluator.generate_report(eval_df)
        print("\n📊 No Context Bot Evaluation Summary:")
        self.write_evaluation_summary(report, "No Context Bot")

if __name__ == "__main__":
    bot = NoContextBot()
    bot.evaluate()
