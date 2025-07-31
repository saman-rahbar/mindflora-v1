from typing import Dict, Any, List, Optional
from interfaces import MemoryInterface
import json
import asyncio
from datetime import datetime
import uuid

class SessionMemory:
    """In-memory storage for therapy sessions and user data"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.session_history: Dict[str, List[str]] = {}  # user_id -> session_ids
    
    async def store_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Store a therapy session"""
        try:
            session_id = str(uuid.uuid4())
            session_data["session_id"] = session_id
            session_data["user_id"] = user_id
            session_data["timestamp"] = datetime.utcnow().isoformat()
            
            self.sessions[session_id] = session_data
            
            if user_id not in self.session_history:
                self.session_history[user_id] = []
            self.session_history[user_id].append(session_id)
            
            return True
        except Exception as e:
            print(f"Error storing session: {e}")
            return False
    
    async def retrieve_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user's therapy history"""
        if user_id not in self.session_history:
            return []
        
        history = []
        for session_id in self.session_history[user_id]:
            if session_id in self.sessions:
                history.append(self.sessions[session_id])
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return history
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile information"""
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {}
            
            self.user_profiles[user_id].update(profile_data)
            self.user_profiles[user_id]["last_updated"] = datetime.utcnow().isoformat()
            
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        return self.user_profiles.get(user_id)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session by ID"""
        return self.sessions.get(session_id)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        try:
            if session_id in self.sessions:
                user_id = self.sessions[session_id].get("user_id")
                if user_id and user_id in self.session_history:
                    self.session_history[user_id].remove(session_id)
                del self.sessions[session_id]
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

# Global memory instance
session_memory = SessionMemory() 