from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

model = init_chat_model("gpt-4o-mini", model_provider="openai")

system_template = """
                  You are a helpful business assistant. 
                  You can answer questions about the business’s working hours
                  (e.g., 'We are open from 7 am to 6 pm, Monday to Friday.') 
                  and questions about the shipment 
                  (e.g., 'Tracking number 1234 was delivered to recipient in Los Angeles today.'). 
                  If the user asks anything else, politely say you can only answer questions about business hours and shipment status.
"""

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{question}")]
  )

while True:
  question = input("Ask me anything (Enter 1 if you want to exit): ")
  if question == "1":
    break
  
  prompt = prompt_template.invoke({"question": question})
  response = model.invoke(prompt)
  print(response.content)