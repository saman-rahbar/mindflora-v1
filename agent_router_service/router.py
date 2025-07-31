from typing import Dict, Any, Optional
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from interfaces import TherapyRequest, TherapyResponse, AgentInterface
from therapy_agent_services.cbt_agent import CBTAgent
from therapy_agent_services.logotherapy_agent import LogotherapyAgent

class AgentRouter:
    def __init__(self):
        self.agents: Dict[str, AgentInterface] = {
            "cbt": CBTAgent(),
            "logotherapy": LogotherapyAgent()
        }
    
    async def route_therapy_request(self, request: TherapyRequest) -> TherapyResponse:
        """
        Route therapy requests to appropriate agents based on therapy type
        """
        agent = self.agents.get(request.therapy_type.lower())
        
        if not agent:
            return TherapyResponse(
                success=False,
                message=f"Unsupported therapy type: {request.therapy_type}",
                response_data=None
            )
        
        try:
            # Route to appropriate agent
            response = await agent.process_request(request)
            return response
        except Exception as e:
            return TherapyResponse(
                success=False,
                message=f"Error processing request: {str(e)}",
                response_data=None
            )
    
    def get_available_therapies(self) -> list:
        """
        Return list of available therapy types
        """
        return list(self.agents.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of all agents
        """
        health_status = {}
        for therapy_type, agent in self.agents.items():
            try:
                health_status[therapy_type] = await agent.health_check()
            except Exception as e:
                health_status[therapy_type] = {"status": "unhealthy", "error": str(e)}
        
        return health_status

# Global router instance
agent_router = AgentRouter() 