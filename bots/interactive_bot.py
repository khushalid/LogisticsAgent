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
        cypher = self.few_shot_bot.generate_cypher(query)
        cypher_answer = self.execute_cypher(cypher)
        return cypher, cypher_answer
    def generate_answer(self, questions, cypher=None, cypher_answer=None):
        prompt = f"""
            You are a helpful business assistant that answers question about Logistics or business. 
            You can answer questions about the business’s working hours
            (e.g., 'We are open from 7 am to 6 pm, Monday to Friday.') 
            If the user is asking about a shipment details then
            Here is the cypher generted for it: {cypher}
            Here is the answer from executing that cypher on the knowledge graph: {cypher_answer}
            Answer the user query: {questions}
        """
        response = self.llm.invoke(prompt)
        return response.content

    
if __name__ == "__main__":
    bot = InteractiveBot()
    while True:
        user_input = input("Ask me anything (exit to quit): ")
        if user_input == "exit":
            break
        if "hours" in user_input or "work" in user_input or "business" in user_input or "open" in user_input:
            print(f"🤖 Bot: {bot.generate_answer(user_input)}")
        else:
            cypher, cypher_answer = bot.generate_cypher(user_input)
            print(f"🤖 Bot: {bot.generate_answer(user_input, cypher, cypher_answer)}")
