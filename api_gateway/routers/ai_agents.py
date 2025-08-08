from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import sys
import os

# Add the agent_router_service to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'agent_router_service'))

from agent_router_service.smart_router import SmartTherapyRouter
from agent_router_service.interfaces import TherapyRequest, TherapyResponse
from agent_router_service.enhanced_agents import EnhancedAIAgent

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Agents"])

# Initialize the smart router and enhanced AI agent
smart_router = SmartTherapyRouter()
enhanced_agent = EnhancedAIAgent()

class AgentRequest(BaseModel):
    """Request model for AI agent interactions"""
    user_id: str
    message: str
    therapy_type: Optional[str] = "cbt"
    mood_rating: Optional[int] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Response model for AI agent interactions"""
    success: bool
    message: str
    therapy: Optional[Dict[str, Any]] = None
    automation: Optional[Dict[str, Any]] = None
    confidence: float
    action_items: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime = datetime.utcnow()

@router.post("/comprehensive-session")
async def process_comprehensive_session(request: AgentRequest) -> AgentResponse:
    """Process a comprehensive session with therapy and automation agents"""
    try:
        logger.info(f"Processing comprehensive session for user {request.user_id}")
        
        # Process with smart router for therapy
        therapy_request = TherapyRequest(
            user_id=request.user_id,
            therapy_type=request.therapy_type,
            session_content=request.message,
            context=request.context or {}
        )
        
        # Route therapy request
        result = await smart_router.route_therapy_request(therapy_request)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Processing failed"))
        
        # Extract action items from responses
        action_items = []
        
        # From therapy response
        therapy_data = result.get("ai_response", {})
        if therapy_data.get("intervention", {}).get("techniques"):
            for technique in therapy_data["intervention"]["techniques"]:
                action_items.append({
                    "type": "therapy_technique",
                    "title": technique,
                    "description": f"Practice {technique} technique"
                })
        
        # Add homework as action items
        homework = therapy_data.get("homework", {})
        if homework.get("assignments"):
            for assignment in homework["assignments"]:
                action_items.append({
                    "type": "homework",
                    "title": assignment.get("title", "Therapy Homework"),
                    "description": assignment.get("description", "Complete therapy homework")
                })
        
        return AgentResponse(
            success=True,
            message=result.get("recommendation", {}).get("personalized_message", "Session processed successfully"),
            therapy={
                "type": result.get("therapy_type", "unknown"),
                "confidence": result.get("routing_analysis", {}).get("confidence", 0.5),
                "intervention": therapy_data.get("intervention", {}),
                "homework": homework
            },
            automation=None,
            confidence=result.get("routing_analysis", {}).get("confidence", 0.5),
            action_items=action_items
        )
        
    except Exception as e:
        logger.error(f"Error in comprehensive session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/calendar-automation")
async def process_calendar_automation(request: AgentRequest) -> AgentResponse:
    """Process calendar automation tasks"""
    try:
        logger.info(f"Processing calendar automation for user {request.user_id}")
        
        # Create therapy request
        therapy_request = TherapyRequest(
            user_id=request.user_id,
            therapy_type=request.therapy_type,
            session_content=request.message,
            context=request.context or {}
        )
        
        # Get calendar agent
        calendar_agent = smart_router.automation_agents.get("calendar")
        if not calendar_agent:
            raise HTTPException(status_code=500, detail="Calendar agent not available")
        
        # Process with calendar agent
        response = await calendar_agent.process_request(therapy_request)
        
        return AgentResponse(
            success=response.success,
            message=response.message,
            confidence=0.8,
            action_items=response.response_data.get("action_items", []) if response.response_data else []
        )
        
    except Exception as e:
        logger.error(f"Error in calendar automation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Calendar automation error: {str(e)}")

@router.post("/email-automation")
async def process_email_automation(request: AgentRequest) -> AgentResponse:
    """Process email automation tasks"""
    try:
        logger.info(f"Processing email automation for user {request.user_id}")
        
        # Create therapy request
        therapy_request = TherapyRequest(
            user_id=request.user_id,
            therapy_type=request.therapy_type,
            session_content=request.message,
            context=request.context or {}
        )
        
        # Get email agent
        email_agent = smart_router.automation_agents.get("email")
        if not email_agent:
            raise HTTPException(status_code=500, detail="Email agent not available")
        
        # Process with email agent
        response = await email_agent.process_request(therapy_request)
        
        return AgentResponse(
            success=response.success,
            message=response.message,
            confidence=0.8,
            action_items=response.response_data.get("action_items", []) if response.response_data else []
        )
        
    except Exception as e:
        logger.error(f"Error in email automation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email automation error: {str(e)}")

@router.post("/notification-automation")
async def process_notification_automation(request: AgentRequest) -> AgentResponse:
    """Process notification automation tasks"""
    try:
        logger.info(f"Processing notification automation for user {request.user_id}")
        
        # Create therapy request
        therapy_request = TherapyRequest(
            user_id=request.user_id,
            therapy_type=request.therapy_type,
            session_content=request.message,
            context=request.context or {}
        )
        
        # Get notification agent
        notification_agent = smart_router.automation_agents.get("notification")
        if not notification_agent:
            raise HTTPException(status_code=500, detail="Notification agent not available")
        
        # Process with notification agent
        response = await notification_agent.process_request(therapy_request)
        
        return AgentResponse(
            success=response.success,
            message=response.message,
            confidence=0.8,
            action_items=response.response_data.get("action_items", []) if response.response_data else []
        )
        
    except Exception as e:
        logger.error(f"Error in notification automation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Notification automation error: {str(e)}")

@router.get("/agents/health")
async def get_agents_health() -> Dict[str, Any]:
    """Get health status of all agents"""
    try:
        health_status = {}
        
        # Check available therapy types
        available_therapies = smart_router.available_therapies
        for therapy_type in available_therapies:
            try:
                health_status[therapy_type] = {
                    "status": "healthy",
                    "type": "therapy",
                    "available": True
                }
            except Exception as e:
                health_status[therapy_type] = {
                    "status": "error", 
                    "error": str(e),
                    "type": "therapy",
                    "available": False
                }
        
        return {
            "success": True,
            "agents": health_status,
            "total_agents": len(health_status),
            "available_therapies": available_therapies
        }
        
    except Exception as e:
        logger.error(f"Error checking agent health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")

@router.get("/agents/info")
async def get_agents_info() -> Dict[str, Any]:
    """Get information about all available agents"""
    try:
        agents_info = {}
        
        # Get therapy agents info
        available_therapies = smart_router.available_therapies
        therapy_info = smart_router.therapy_info
        
        for therapy_type in available_therapies:
            try:
                agents_info[therapy_type] = {
                    "type": "therapy",
                    "name": therapy_type.upper(),
                    "description": therapy_info.get(therapy_type, {}).get("description", f"{therapy_type.upper()} therapy"),
                    "available": True
                }
            except Exception as e:
                agents_info[therapy_type] = {"error": str(e)}
        
        return {
            "success": True,
            "agents": agents_info,
            "therapy_agents": available_therapies,
            "automation_agents": []
        }
        
    except Exception as e:
        logger.error(f"Error getting agents info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agents info error: {str(e)}")

@router.post("/analyze-intent")
async def analyze_user_intent(request: AgentRequest) -> Dict[str, Any]:
    """Analyze user intent for therapy and automation needs"""
    try:
        logger.info(f"Analyzing intent for user {request.user_id}")
        
        # Analyze and route
        analysis_result = await smart_router.analyze_and_route(
            user_input=request.message,
            mood_rating=request.mood_rating
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "therapy_recommendation": analysis_result.get("therapy", {}),
            "automation_tasks": analysis_result.get("automation", {}).get("tasks", []),
            "overall_confidence": analysis_result.get("overall_confidence", 0.5)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing intent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Intent analysis error: {str(e)}")

@router.post("/enhanced-chat")
async def enhanced_ai_chat(request: AgentRequest) -> Dict[str, Any]:
    """Enhanced AI chat with SMS, Email, and personalization capabilities"""
    try:
        logger.info(f"Processing enhanced chat for user {request.user_id}")
        
        # Process with enhanced AI agent
        result = await enhanced_agent.process_user_request(
            user_id=request.user_id,
            message=request.message,
            context=request.context
        )
        
        return {
            "success": result["success"],
            "response": result["response"],
            "intent": result.get("intent", {}),
            "tool_actions": result.get("tool_actions", {}),
            "user_profile_updated": result.get("user_profile_updated", False)
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced chat error: {str(e)}")

@router.post("/send-sms")
async def send_sms(request: AgentRequest) -> Dict[str, Any]:
    """Send SMS to user"""
    try:
        logger.info(f"Sending SMS for user {request.user_id}")
        
        result = await enhanced_agent.send_sms(
            user_id=request.user_id,
            message=request.message
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SMS error: {str(e)}")

@router.post("/send-email")
async def send_email(request: AgentRequest) -> Dict[str, Any]:
    """Send email to user"""
    try:
        logger.info(f"Sending email for user {request.user_id}")
        
        # Extract subject from context or use default
        subject = request.context.get("subject", "Your AI Assistant Update") if request.context else "Your AI Assistant Update"
        
        result = await enhanced_agent.send_email(
            user_id=request.user_id,
            subject=subject,
            message=request.message
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email error: {str(e)}")

@router.post("/update-preferences")
async def update_user_preferences(request: AgentRequest) -> Dict[str, Any]:
    """Update user AI agent preferences"""
    try:
        logger.info(f"Updating preferences for user {request.user_id}")
        
        preferences = request.context or {}
        
        result = await enhanced_agent.update_user_preferences(
            user_id=request.user_id,
            preferences=preferences
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Preferences update error: {str(e)}")

@router.post("/test-sms")
async def test_sms(request: AgentRequest) -> Dict[str, Any]:
    """Test SMS functionality"""
    try:
        logger.info(f"Testing SMS for user {request.user_id}")
        
        # Test with a simple message
        result = await enhanced_agent.send_sms(
            user_id=request.user_id,
            message="This is a test SMS from your AI assistant! 🤖"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing SMS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SMS test error: {str(e)}") 