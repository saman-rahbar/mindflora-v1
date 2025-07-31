from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agent_router_service.interfaces import TherapyRequest, TherapyResponse, AgentInterface
from memory_service.memory import MemoryService
import asyncio
from datetime import datetime

class BaseTherapyAgent(AgentInterface):
    """Base class for all therapy agents"""
    
    def __init__(self, agent_name: str, therapy_type: str):
        self.agent_name = agent_name
        self.therapy_type = therapy_type
        self.memory_service = MemoryService()
        self.is_healthy = True
    
    @abstractmethod
    async def process_therapy_request(self, request: TherapyRequest) -> Dict[str, Any]:
        """
        Process the actual therapy request - to be implemented by subclasses
        """
        pass
    
    async def process_request(self, request: TherapyRequest) -> TherapyResponse:
        """
        Main request processing method with common functionality
        """
        try:
            # Validate request
            if not self._validate_request(request):
                return TherapyResponse(
                    success=False,
                    message="Invalid request format",
                    response_data=None
                )
            
            # Store session in memory
            await self.memory_service.store_session(
                user_id=request.user_id,
                session_data={
                    "therapy_type": self.therapy_type,
                    "content": request.session_content,
                    "context": request.context,
                    "timestamp": request.timestamp.isoformat()
                }
            )
            
            # Process therapy request
            therapy_response = await self.process_therapy_request(request)
            
            return TherapyResponse(
                success=True,
                message="Therapy session processed successfully",
                response_data=therapy_response
            )
            
        except Exception as e:
            return TherapyResponse(
                success=False,
                message=f"Error processing therapy request: {str(e)}",
                response_data=None
            )
    
    def _validate_request(self, request: TherapyRequest) -> bool:
        """
        Validate incoming therapy request
        """
        if not request.user_id or not request.session_content:
            return False
        
        if request.therapy_type.lower() != self.therapy_type.lower():
            return False
        
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check agent health status
        """
        return {
            "agent_name": self.agent_name,
            "therapy_type": self.therapy_type,
            "status": "healthy" if self.is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent
        """
        return {
            "agent_name": self.agent_name,
            "therapy_type": self.therapy_type,
            "description": self._get_agent_description(),
            "capabilities": self._get_agent_capabilities()
        }
    
    @abstractmethod
    def _get_agent_description(self) -> str:
        """
        Get agent description - to be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def _get_agent_capabilities(self) -> List[str]:
        """
        Get agent capabilities - to be implemented by subclasses
        """
        pass
    
    async def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's therapy history
        """
        return await self.memory_service.get_user_sessions(user_id, self.therapy_type) 