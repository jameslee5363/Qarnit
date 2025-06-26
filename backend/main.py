from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth import pwd_context
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from sqlalchemy.exc import IntegrityError
import re

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Store chat history in memory (use a database in a real app)
chat_history: List[ChatMessage] = []

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr        # ← new: ensures valid email format
    password: str
    confirm_password: str


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

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Password validation
    password = data.password
    if password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long and include at least one letter and one number.")
    # 1. Check username
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    # 2. Check email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # 3. Create user
    hashed_password = pwd_context.hash(data.password)
    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        # in case the DB-level unique constraint fires first
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"message": "Registration successful"}