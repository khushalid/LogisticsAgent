from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bots.interactive_bot import InteractiveBot

app = FastAPI()
bot = InteractiveBot()

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    user_input: str

@app.post("/chat")
async def chat_endpoint(req: QueryRequest):
    user_input = req.user_input
    if "hours" in user_input or "work" in user_input or "business" in user_input or "open" in user_input:
        answer = bot.generate_answer(user_input)
        return {"response": answer}
    else:
        cypher, cypher_answer = bot.generate_cypher(user_input)
        answer = bot.generate_answer(user_input, cypher, cypher_answer)
        return {"response": answer, "cypher": cypher, "cypher_answer": cypher_answer}
