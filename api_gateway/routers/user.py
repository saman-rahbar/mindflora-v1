from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    therapy_preference: Optional[str] = "cbt"

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    therapy_preference: str
    created_at: datetime

class TherapySession(BaseModel):
    user_id: str
    session_type: str
    content: str
    timestamp: datetime

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    session_type: str
    content: str
    timestamp: datetime

# In-memory storage (replace with database in production)
users_db = {}
sessions_db = {}

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "therapy_preference": user.therapy_preference,
        "created_at": datetime.utcnow()
    }
    users_db[user_id] = user_data
    return UserResponse(**user_data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**users_db[user_id])

@router.post("/{user_id}/sessions", response_model=SessionResponse)
async def create_therapy_session(user_id: str, session: TherapySession):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "session_type": session.session_type,
        "content": session.content,
        "timestamp": datetime.utcnow()
    }
    sessions_db[session_id] = session_data
    return SessionResponse(**session_data)

@router.get("/{user_id}/sessions", response_model=List[SessionResponse])
async def get_user_sessions(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_sessions = [
        SessionResponse(**session) 
        for session in sessions_db.values() 
        if session["user_id"] == user_id
    ]
    return user_sessions 