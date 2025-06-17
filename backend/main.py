from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Allow React frontend to access this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # adjust to match frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat message model
class ChatMessage(BaseModel):
    role: str
    content: str

# Store chat history in memory (in a real app, you'd use a database)
chat_history: List[ChatMessage] = []

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.post("/api/chat")
async def chat(message: ChatMessage):
    # Add user message to history
    chat_history.append(message)
    
    # Simple echo response for now
    # In a real app, you'd integrate with an AI model here
    response = ChatMessage(
        role="assistant",
        content=f"Echo: {message.content}"
    )
    chat_history.append(response)
    return response

@app.get("/api/chat/history")
async def get_chat_history():
    return chat_history