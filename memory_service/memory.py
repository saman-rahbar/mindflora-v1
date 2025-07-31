from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
import asyncio

class MemoryService:
    """Service for managing therapy session memory and user data"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.session_history: Dict[str, List[str]] = {}  # user_id -> session_ids
        self.therapy_progress: Dict[str, Dict[str, Any]] = {}  # user_id -> progress_data
    
    async def store_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Store a therapy session in memory
        """
        try:
            session_id = str(uuid.uuid4())
            session_data["session_id"] = session_id
            session_data["user_id"] = user_id
            session_data["timestamp"] = datetime.utcnow().isoformat()
            
            self.sessions[session_id] = session_data
            
            if user_id not in self.session_history:
                self.session_history[user_id] = []
            self.session_history[user_id].append(session_id)
            
            # Update therapy progress
            await self._update_progress(user_id, session_data)
            
            return True
        except Exception as e:
            print(f"Error storing session: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str, therapy_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve user's therapy sessions, optionally filtered by therapy type
        """
        if user_id not in self.session_history:
            return []
        
        sessions = []
        for session_id in self.session_history[user_id]:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if therapy_type is None or session.get("therapy_type") == therapy_type:
                    sessions.append(session)
        
        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return sessions
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific session by ID
        """
        return self.sessions.get(session_id)
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Update user profile information
        """
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
        """
        Get user profile information
        """
        return self.user_profiles.get(user_id)
    
    async def get_therapy_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's therapy progress summary
        """
        if user_id not in self.therapy_progress:
            return {}
        
        progress = self.therapy_progress[user_id].copy()
        
        # Add session count
        session_count = len(self.session_history.get(user_id, []))
        progress["total_sessions"] = session_count
        
        # Add recent activity
        recent_sessions = await self.get_user_sessions(user_id)
        if recent_sessions:
            progress["last_session"] = recent_sessions[0].get("timestamp")
            progress["therapy_types_used"] = list(set(s.get("therapy_type") for s in recent_sessions))
        
        return progress
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific session
        """
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
    
    async def search_sessions(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Search user's sessions by content
        """
        sessions = await self.get_user_sessions(user_id)
        matching_sessions = []
        
        query_lower = query.lower()
        for session in sessions:
            content = session.get("content", "").lower()
            if query_lower in content:
                matching_sessions.append(session)
        
        return matching_sessions
    
    async def get_session_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about user's therapy sessions
        """
        sessions = await self.get_user_sessions(user_id)
        
        if not sessions:
            return {}
        
        # Count by therapy type
        therapy_counts = {}
        for session in sessions:
            therapy_type = session.get("therapy_type", "unknown")
            therapy_counts[therapy_type] = therapy_counts.get(therapy_type, 0) + 1
        
        # Calculate session frequency
        if len(sessions) > 1:
            first_session = datetime.fromisoformat(sessions[-1]["timestamp"])
            last_session = datetime.fromisoformat(sessions[0]["timestamp"])
            days_between = (last_session - first_session).days
            frequency = len(sessions) / max(days_between, 1)  # sessions per day
        else:
            frequency = 0
        
        return {
            "total_sessions": len(sessions),
            "therapy_type_distribution": therapy_counts,
            "session_frequency": frequency,
            "first_session": sessions[-1]["timestamp"],
            "last_session": sessions[0]["timestamp"]
        }
    
    async def _update_progress(self, user_id: str, session_data: Dict[str, Any]) -> None:
        """
        Update therapy progress based on session data
        """
        if user_id not in self.therapy_progress:
            self.therapy_progress[user_id] = {}
        
        therapy_type = session_data.get("therapy_type")
        if therapy_type:
            if "therapy_sessions" not in self.therapy_progress[user_id]:
                self.therapy_progress[user_id]["therapy_sessions"] = {}
            
            if therapy_type not in self.therapy_progress[user_id]["therapy_sessions"]:
                self.therapy_progress[user_id]["therapy_sessions"][therapy_type] = 0
            
            self.therapy_progress[user_id]["therapy_sessions"][therapy_type] += 1
        
        # Update last activity
        self.therapy_progress[user_id]["last_activity"] = datetime.utcnow().isoformat()
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data for privacy/deletion requests
        """
        return {
            "user_id": user_id,
            "profile": await self.get_user_profile(user_id),
            "sessions": await self.get_user_sessions(user_id),
            "progress": await self.get_therapy_progress(user_id),
            "statistics": await self.get_session_statistics(user_id),
            "export_timestamp": datetime.utcnow().isoformat()
        }
    
    async def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all data for a user (GDPR compliance)
        """
        try:
            # Delete sessions
            if user_id in self.session_history:
                for session_id in self.session_history[user_id]:
                    if session_id in self.sessions:
                        del self.sessions[session_id]
                del self.session_history[user_id]
            
            # Delete profile
            if user_id in self.user_profiles:
                del self.user_profiles[user_id]
            
            # Delete progress
            if user_id in self.therapy_progress:
                del self.therapy_progress[user_id]
            
            return True
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False 