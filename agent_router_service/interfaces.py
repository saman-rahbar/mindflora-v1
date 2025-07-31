from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class TherapyRequest(BaseModel):
    """Request model for therapy sessions"""
    user_id: str
    therapy_type: str
    session_content: str
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class TherapyResponse(BaseModel):
    """Response model for therapy sessions"""
    success: bool
    message: str
    response_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class AgentInterface(ABC):
    """Abstract interface for therapy agents"""
    
    @abstractmethod
    async def process_request(self, request: TherapyRequest) -> TherapyResponse:
        """Process a therapy request and return a response"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the agent"""
        pass
    
    @abstractmethod
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        pass

class MemoryInterface(ABC):
    """Abstract interface for memory operations"""
    
    @abstractmethod
    async def store_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Store a therapy session in memory"""
        pass
    
    @abstractmethod
    async def retrieve_user_history(self, user_id: str) -> list:
        """Retrieve user's therapy history"""
        pass
    
    @abstractmethod
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile information"""
        pass 