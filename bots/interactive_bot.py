import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_bot import BaseBot
from few_shot_bot import FewShotBot
from langchain.chat_models import ChatOpenAI

class InteractiveBot(BaseBot):
    def __init__(self):
        super().__init__()  # Initialize Neo4j connection from BaseBot
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.few_shot_bot = FewShotBot()
    def generate_cypher(self, query):
        return self.few_shot_bot.generate_cypher(query)
    def working_hour(self, query):
        prompt = f"""
            You are a helpful business assistant. 
            You can answer questions about the business’s working hours
            (e.g., 'We are open from 7 am to 6 pm, Monday to Friday.') 
            Answer the user query: {query}
        """
        response = self.llm.invoke(prompt)
        return response.content

    
if __name__ == "__main__":
    bot = InteractiveBot()
    while True:
        user_input = input("Ask me anything (exit to quit): ")
        if user_input == "exit":
            break
        if "hours" in user_input or "work" in user_input or "business" in user_input:
            print(f"🤖 Bot: {bot.working_hour(user_input)}")
        else:
            print(f"🤖 Bot: {bot.generate_cypher(user_input)}")
