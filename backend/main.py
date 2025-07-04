from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from auth import authenticate_user, create_access_token, pwd_context, oauth2_scheme, verify_token
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Conversation, ChatMessage as ChatMessageDB
from sqlalchemy.exc import IntegrityError
import re
from datetime import datetime


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

# Chat message schema
class ChatMessageSchema(BaseModel):
    role: str
    content: str

    class Config:
        orm_mode = True

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr       
    password: str
    confirm_password: str

class ConversationOut(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class ChatMessageSchema(BaseModel):
    id: Optional[int] = None          # make id optional when posting
    role: str
    content: str
    timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True

# helper function to get current user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT and return the corresponding user object."""
    username = verify_token(token)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/api/conversations", response_model=ConversationOut)
def new_conversation(
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = Conversation(user_id=current_user.id, title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@app.get("/api/conversations", response_model=List[ConversationOut])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@app.delete("/api/conversations/{conv_id}", status_code=204)
def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()

@app.post(
    "/api/conversations/{conv_id}/messages",
    response_model=ChatMessageSchema,
    status_code=201,
)
def add_message(
    conv_id: int,
    msg: ChatMessageSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Make sure conv belongs to user
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 2. Save user message
    user_msg = ChatMessageDB(
        user_id=current_user.id,
        conversation_id=conv_id,
        role="user",
        content=msg.content,
    )
    db.add(user_msg)
    db.flush()                       # so we know its id if needed

    # 3. Generate assistant reply (replace with real model)
    assistant_content = f"Echo: {msg.content}"
    assistant_msg = ChatMessageDB(
        user_id=current_user.id,
        conversation_id=conv_id,
        role="assistant",
        content=assistant_content,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg


@app.get(
    "/api/conversations/{conv_id}/messages",
    response_model=List[ChatMessageSchema],
)
def get_messages(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ChatMessageDB)
        .filter(
            ChatMessageDB.conversation_id == conv_id,
            ChatMessageDB.user_id == current_user.id,
        )
        .order_by(ChatMessageDB.timestamp)
        .all()
    )

@app.post("/api/chat", response_model=ChatMessageSchema)
async def chat(
    message: ChatMessageSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Receive a user message, store it, generate an assistant reply, store that, and return the reply."""
    # 1. Persist user's message
    user_msg = ChatMessageDB(
        user_id=current_user.id,
        role="user",
        content=message.content,
    )

    # 2. Generate assistant response (replace with real model later)
    assistant_content = f"Echo: {message.content}"
    assistant_msg = ChatMessageDB(
        user_id=current_user.id,
        role="assistant",
        content=assistant_content,
    )

    db.add_all([user_msg, assistant_msg])
    db.commit()

    return ChatMessageSchema(role="assistant", content=assistant_content)


@app.get("/api/chat/history", response_model=List[ChatMessageSchema])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all chat messages for the authenticated user, ordered chronologically."""
    messages = (
        db.query(ChatMessageDB)
        .filter(ChatMessageDB.user_id == current_user.id)
        .order_by(ChatMessageDB.timestamp)
        .all()
    )
    return [ChatMessageSchema(role=m.role, content=m.content) for m in messages]


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
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"message": "Registration successful"}