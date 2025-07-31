from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import asyncio
import logging

router = APIRouter()

# Import authentication dependency
from .auth import get_current_user
try:
    from .gamification import award_xp, update_streak
except ImportError:
    # Fallback functions if gamification is not available
    def award_xp(user_id: str, xp: int, reason: str):
        return {"xp_awarded": xp, "reason": reason}
    
    def update_streak(user_id: str):
        return {"streak_updated": True}

# Import therapy services
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agent_router_service.router import agent_router
from agent_router_service.interfaces import TherapyRequest, TherapyResponse
# Import smart router with proper path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from agent_router_service.smart_router import smart_router
    print("✅ Smart router imported successfully")
except ImportError as e:
    print(f"Warning: Could not import smart_router: {e}")
    smart_router = None
from memory_service.memory import MemoryService

# In-memory session storage (replace with database in production)
therapy_sessions = {}
user_therapy_history = {}

class TherapySessionRequest(BaseModel):
    therapy_type: Optional[str] = None  # Optional for smart therapy
    session_content: str
    mood_before: Optional[int] = None  # 1-10 scale
    mood_after: Optional[int] = None   # 1-10 scale
    context: Optional[Dict[str, Any]] = None

class TherapySessionResponse(BaseModel):
    session_id: str
    user_id: str
    therapy_type: str
    ai_response: Dict[str, Any]
    mood_before: Optional[int]
    mood_after: Optional[int]
    timestamp: str
    xp_earned: int

class SessionHistory(BaseModel):
    session_id: str
    therapy_type: str
    timestamp: str
    mood_before: Optional[int]
    mood_after: Optional[int]
    summary: str

class OnboardingSurvey(BaseModel):
    age: int
    gender: Optional[str] = None
    primary_concerns: List[str]
    therapy_experience: str  # "none", "some", "extensive"
    preferred_modalities: List[str]
    goals: List[str]
    availability: str  # "daily", "weekly", "as_needed"
    privacy_preferences: Dict[str, Any]

class UserProfile(BaseModel):
    therapy_preferences: Dict[str, Any]
    goals: List[str]
    progress_metrics: Dict[str, Any]
    recommended_modalities: List[str]

# Initialize memory service
memory_service = MemoryService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/session", response_model=TherapySessionResponse)
async def create_therapy_session(
    session_data: TherapySessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new therapy session with AI agent"""
    user_id = current_user["id"]
    
    # Validate therapy type
    available_therapies = agent_router.get_available_therapies()
    if session_data.therapy_type.lower() not in [t.lower() for t in available_therapies]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported therapy type. Available: {available_therapies}"
        )
    
    # Create therapy request
    therapy_request = TherapyRequest(
        user_id=user_id,
        therapy_type=session_data.therapy_type,
        session_content=session_data.session_content,
        context=session_data.context or {}
    )
    
    # Route to appropriate agent
    try:
        response = await agent_router.route_therapy_request(therapy_request)
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Therapy session failed: {response.message}"
            )
        
        # Create session record
        session_id = str(uuid.uuid4())
        session_record = {
            "session_id": session_id,
            "user_id": user_id,
            "therapy_type": session_data.therapy_type,
            "content": session_data.session_content,
            "ai_response": response.response_data,
            "mood_before": session_data.mood_before,
            "mood_after": session_data.mood_after,
            "context": session_data.context,
            "timestamp": datetime.utcnow().isoformat(),
            "xp_earned": 25  # Base XP for therapy session
        }
        
        # Store session
        therapy_sessions[session_id] = session_record
        
        # Update user history
        if user_id not in user_therapy_history:
            user_therapy_history[user_id] = []
        user_therapy_history[user_id].append(session_id)
        
        # Store in memory service
        await memory_service.store_session(user_id, session_record)
        
        # Award XP and update gamification
        xp_result = award_xp(user_id, session_record["xp_earned"], f"Therapy session: {session_data.therapy_type}")
        update_streak(user_id)
        
        return TherapySessionResponse(
            session_id=session_id,
            user_id=user_id,
            therapy_type=session_data.therapy_type,
            ai_response=response.response_data,
            mood_before=session_data.mood_before,
            mood_after=session_data.mood_after,
            timestamp=session_record["timestamp"],
            xp_earned=session_record["xp_earned"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing therapy session: {str(e)}"
        )

@router.get("/test-smart")
async def test_smart_endpoint():
    """Test endpoint to verify router registration"""
    return {"message": "Smart endpoint is working!"}

@router.post("/test-smart-simple")
async def test_smart_simple(
    request: TherapySessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Simple test endpoint for smart therapy"""
    try:
        return {
            "message": "Simple smart endpoint working!",
            "user_id": current_user["id"],
            "content": request.session_content,
            "mood": request.mood_before
        }
    except Exception as e:
        print(f"Error in simple test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simple test failed: {str(e)}")

@router.post("/smart-session")
async def create_smart_therapy_session(
    request: TherapySessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a therapy session with automatic modality selection"""
    user_id = current_user["id"]
    
    try:
        # Simple content analysis for therapy type
        content_lower = request.session_content.lower()
        
        # Get user context for personalization
        user_context = request.context or {}
        user_name = user_context.get('User', 'there').split(': ')[-1] if 'User:' in str(user_context) else 'there'
        user_age = user_context.get('Age', '') if 'Age:' in str(user_context) else ''
        user_education = user_context.get('Education', '') if 'Education:' in str(user_context) else ''
        
        # Create personalized greeting
        personalized_greeting = f"Hello {user_name}! "
        
        # Determine therapy type based on content and user context
        if any(word in content_lower for word in ["meaning", "purpose", "pointless", "empty", "void"]):
            recommended_therapy = "logotherapy"
            therapy_name = "Logotherapy (Meaning-Centered Therapy)"
            personalized_message = f"{personalized_greeting}I hear you're searching for meaning and purpose. Logotherapy can help you discover what truly matters to you."
        elif any(word in content_lower for word in ["anxiety", "worry", "stress", "overwhelm", "panic"]):
            recommended_therapy = "cbt"
            therapy_name = "Cognitive Behavioral Therapy (CBT)"
            personalized_message = f"{personalized_greeting}I notice you're experiencing anxiety and worry. CBT can help you identify and challenge negative thought patterns."
        else:
            recommended_therapy = "cbt"
            therapy_name = "Cognitive Behavioral Therapy (CBT)"
            personalized_message = f"{personalized_greeting}Based on what you've shared, CBT can help you identify and change the thought patterns that may be contributing to your distress."
        
        # Create session record
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "therapy_type": recommended_therapy,
            "session_content": request.session_content,
            "mood_before": request.mood_before,
            "mood_after": None,
            "timestamp": datetime.utcnow().isoformat(),
            "xp_earned": 30
        }
        
        # Store session
        therapy_sessions[session_id] = session_data
        
        # Update user history
        if user_id not in user_therapy_history:
            user_therapy_history[user_id] = []
        user_therapy_history[user_id].append(session_id)
        
        # Award XP for smart session (with error handling)
        try:
            award_xp(user_id, session_data["xp_earned"], f"Smart therapy session: {recommended_therapy}")
            update_streak(user_id)
        except Exception as e:
            print(f"Gamification error (non-critical): {str(e)}")
        
        # Create routing analysis
        routing_analysis = {
            "primary_therapy": recommended_therapy,
            "secondary_therapies": [],
            "analysis": {
                recommended_therapy: {"score": 3, "confidence": 0.8}
            },
            "recommendation": {
                "therapy_info": {
                    "name": therapy_name,
                    "description": f"{therapy_name} helps address your specific needs."
                },
                "personalized_message": personalized_message
            },
            "confidence": 0.8
        }
        
        # Create AI response with personalization
        ai_response = {
            "therapy_type": recommended_therapy,
            "analysis": {
                "distortions_found": ["catastrophizing"] if "anxiety" in content_lower else [],
                "thought_patterns": {"negative_thoughts": 2, "positive_thoughts": 0, "thought_balance": "negative"},
                "emotion_analysis": {"primary_emotion": "anxiety", "intensity": 6}
            },
            "intervention": {
                "techniques": ["Cognitive restructuring", "Thought record"],
                "response": f"Hello {user_name}! I notice you're experiencing some challenging thoughts. Let's explore these together and find strategies that work for you.",
                "homework": {"type": "gratitude_journal", "description": f"Write down three things you're grateful for each day, {user_name}. This simple practice can help shift your perspective.", "duration": "1 week"}
            }
        }
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "recommended_therapy": recommended_therapy,
            "confidence": 0.8,
            "routing_analysis": routing_analysis,
            "ai_response": ai_response,
            "mood_before": request.mood_before,
            "mood_after": None,
            "timestamp": session_data["timestamp"],
            "xp_earned": session_data["xp_earned"]
        }
            
    except Exception as e:
        print(f"Error in smart session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Smart therapy session failed: {str(e)}")

@router.get("/sessions", response_model=List[SessionHistory])
async def get_user_sessions(
    current_user: dict = Depends(get_current_user),
    therapy_type: Optional[str] = None,
    limit: int = 20
):
    """Get user's therapy session history"""
    user_id = current_user["id"]
    
    if user_id not in user_therapy_history:
        return []
    
    sessions = []
    for session_id in user_therapy_history[user_id][-limit:]:  # Get most recent
        if session_id in therapy_sessions:
            session = therapy_sessions[session_id]
            
            # Filter by therapy type if specified
            if therapy_type and session["therapy_type"].lower() != therapy_type.lower():
                continue
            
            sessions.append(SessionHistory(
                session_id=session["session_id"],
                therapy_type=session["therapy_type"],
                timestamp=session["timestamp"],
                mood_before=session["mood_before"],
                mood_after=session["mood_after"],
                summary=session["ai_response"].get("intervention", {}).get("response", "Session completed")
            ))
    
    return sessions[::-1]  # Return in reverse chronological order

@router.get("/session/{session_id}")
async def get_session_details(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific session"""
    if session_id not in therapy_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = therapy_sessions[session_id]
    
    # Verify user owns this session
    if session["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return session

@router.post("/onboarding")
async def complete_onboarding(
    survey_data: OnboardingSurvey,
    current_user: dict = Depends(get_current_user)
):
    """Complete user onboarding survey"""
    user_id = current_user["id"]
    
    # Analyze survey data to determine optimal therapy approach
    recommended_modalities = analyze_onboarding_survey(survey_data)
    
    # Update user profile
    user_profile = {
        "onboarding_completed": True,
        "survey_data": survey_data.dict(),
        "recommended_modalities": recommended_modalities,
        "therapy_goals": survey_data.goals,
        "preferred_schedule": survey_data.availability,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store in memory service
    await memory_service.update_user_profile(user_id, user_profile)
    
    # Award XP for completing onboarding
    xp_result = award_xp(user_id, 100, "Completed onboarding survey")
    
    return {
        "message": "Onboarding completed successfully",
        "recommended_modalities": recommended_modalities,
        "therapy_goals": survey_data.goals,
        "xp_earned": 100
    }

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user's therapy profile and recommendations"""
    user_id = current_user["id"]
    
    # Get profile from memory service
    profile = await memory_service.get_user_profile(user_id)
    
    if not profile:
        return {
            "onboarding_completed": False,
            "recommended_modalities": ["cbt", "logotherapy"],
            "goals": [],
            "progress_metrics": {}
        }
    
    # Get therapy history for progress metrics
    sessions = await memory_service.get_user_sessions(user_id)
    
    progress_metrics = {
        "total_sessions": len(sessions),
        "sessions_by_modality": {},
        "average_mood_improvement": 0,
        "most_used_modality": None
    }
    
    if sessions:
        # Calculate modality usage
        modality_counts = {}
        mood_improvements = []
        
        for session in sessions:
            modality = session.get("therapy_type", "unknown")
            modality_counts[modality] = modality_counts.get(modality, 0) + 1
            
            # Calculate mood improvement
            mood_before = session.get("mood_before")
            mood_after = session.get("mood_after")
            if mood_before and mood_after:
                mood_improvements.append(mood_after - mood_before)
        
        progress_metrics["sessions_by_modality"] = modality_counts
        progress_metrics["average_mood_improvement"] = sum(mood_improvements) / len(mood_improvements) if mood_improvements else 0
        progress_metrics["most_used_modality"] = max(modality_counts.items(), key=lambda x: x[1])[0] if modality_counts else None
    
    return {
        "onboarding_completed": profile.get("onboarding_completed", False),
        "recommended_modalities": profile.get("recommended_modalities", ["cbt", "logotherapy"]),
        "goals": profile.get("therapy_goals", []),
        "progress_metrics": progress_metrics,
        "preferred_schedule": profile.get("preferred_schedule", "as_needed")
    }

@router.get("/available-modalities")
async def get_available_modalities():
    """Get list of available therapy modalities"""
    modalities = agent_router.get_available_therapies()
    
    modality_descriptions = {
        "cbt": {
            "name": "Cognitive Behavioral Therapy",
            "description": "Focuses on identifying and challenging negative thought patterns",
            "best_for": ["Anxiety", "Depression", "Negative thinking", "Stress management"],
            "duration": "10-20 minutes per session"
        },
        "logotherapy": {
            "name": "Logotherapy",
            "description": "Meaning-centered therapy that helps find purpose and meaning in life",
            "best_for": ["Existential questions", "Life transitions", "Finding purpose", "Coping with suffering"],
            "duration": "15-25 minutes per session"
        },
        "act": {
            "name": "Acceptance and Commitment Therapy",
            "description": "Helps accept difficult thoughts and feelings while committing to value-based actions",
            "best_for": ["Anxiety", "Depression", "Stress", "Life changes"],
            "duration": "15-20 minutes per session"
        },
        "dbt": {
            "name": "Dialectical Behavior Therapy",
            "description": "Teaches emotional regulation and interpersonal effectiveness skills",
            "best_for": ["Emotional regulation", "Relationships", "Impulse control", "Borderline personality"],
            "duration": "20-30 minutes per session"
        },
        "somotherapy": {
            "name": "Somotherapy",
            "description": "Body-centered therapy for trauma recovery and somatic awareness",
            "best_for": ["Trauma", "Body awareness", "Stress", "Physical symptoms"],
            "duration": "15-25 minutes per session"
        },
        "positive_psychology": {
            "name": "Positive Psychology",
            "description": "Focuses on strengths, gratitude, and building positive emotions",
            "best_for": ["Well-being", "Gratitude", "Strengths", "Happiness"],
            "duration": "10-15 minutes per session"
        }
    }
    
    return {
        "modalities": [
            {
                "id": modality,
                **modality_descriptions.get(modality, {
                    "name": modality.title(),
                    "description": "Therapy modality",
                    "best_for": [],
                    "duration": "15-20 minutes per session"
                })
            }
            for modality in modalities
        ]
    }

@router.get("/recommendations")
async def get_therapy_recommendations(current_user: dict = Depends(get_current_user)):
    """Get personalized therapy recommendations"""
    user_id = current_user["id"]
    
    # Get user profile and history
    profile = await memory_service.get_user_profile(user_id)
    sessions = await memory_service.get_user_sessions(user_id)
    
    # Generate recommendations based on history and profile
    recommendations = generate_therapy_recommendations(profile, sessions)
    
    return {
        "recommendations": recommendations,
        "based_on": {
            "session_history": len(sessions),
            "profile_data": profile is not None,
            "mood_trends": analyze_mood_trends(sessions)
        }
    }

@router.post("/chat")
async def chat_with_therapist(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Chat with AI therapist and get personalized responses"""
    try:
        # Extract user context for personalization
        user_context = getUserContext(current_user)
        
        # Create personalized chat request
        chat_request = {
            "message": request.get("message"),
            "session_id": request.get("session_id"),
            "therapist_personality": request.get("therapist_personality", {
                "name": "Dr. Sarah",
                "style": "compassionate",
                "approach": "evidence-based"
            }),
            "conversation_history": request.get("conversation_history", []),
            "user_context": user_context
        }
        
        # Get AI response from therapy agent
        from therapy_agent_services.cbt_agent import CBTAgent
        agent = CBTAgent()
        
        response = await agent.process_chat_request(chat_request)
        
        # Extract action items from response
        action_items = extract_action_items(response.get("content", ""))
        
        return {
            "success": True,
            "content": response.get("content"),
            "action_items": action_items,
            "session_id": request.get("session_id")
        }
    except Exception as e:
        logger.error(f"Error in chat with therapist: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing chat request")

@router.get("/assignments")
async def get_assignments(
    current_user: dict = Depends(get_current_user)
):
    """Get user's assignments"""
    try:
        # Mock assignments data - in production, this would come from database
        assignments = [
            {
                "id": "1",
                "title": "Daily Mood Check-in",
                "description": "Take 5 minutes to reflect on your mood and write down 3 things you're grateful for.",
                "category": "homework",
                "status": "active",
                "estimated_duration": 15,
                "deadline": (datetime.now() + timedelta(days=1)).isoformat(),
                "progress": 0,
                "instructions": "Find a quiet place, take deep breaths, and reflect on your day.",
                "materials": ["Journal", "Quiet space"],
                "progress_questions": [
                    "How are you feeling about this assignment?",
                    "What challenges did you encounter?",
                    "What insights did you gain?",
                    "How can you apply this learning?"
                ]
            },
            {
                "id": "2",
                "title": "Mindfulness Meditation",
                "description": "Practice mindfulness meditation for 10 minutes focusing on your breath.",
                "category": "meditation",
                "status": "pending",
                "estimated_duration": 10,
                "deadline": (datetime.now() + timedelta(days=2)).isoformat(),
                "progress": 0,
                "instructions": "Sit comfortably, close your eyes, and focus on your breathing.",
                "materials": ["Comfortable space", "Timer"],
                "progress_questions": [
                    "How did you feel during the meditation?",
                    "What thoughts came up?",
                    "How did you handle distractions?",
                    "What did you learn about your mind?"
                ]
            }
        ]
        
        return {"success": True, "data": assignments}
    except Exception as e:
        logger.error(f"Error getting assignments: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving assignments")

@router.post("/assignments")
async def create_assignment(
    assignment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new assignment"""
    try:
        # In production, save to database
        assignment = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "title": assignment_data.get("title"),
            "description": assignment_data.get("description"),
            "category": assignment_data.get("category", "general"),
            "status": "pending",
            "estimated_duration": assignment_data.get("estimated_duration", 30),
            "deadline": assignment_data.get("deadline"),
            "progress": 0,
            "created_at": datetime.now().isoformat()
        }
        
        return {"success": True, "data": assignment}
    except Exception as e:
        logger.error(f"Error creating assignment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating assignment")

@router.put("/assignments/{assignment_id}")
async def update_assignment(
    assignment_id: str,
    assignment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update an assignment"""
    try:
        # In production, update in database
        return {"success": True, "data": assignment_data}
    except Exception as e:
        logger.error(f"Error updating assignment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating assignment")

@router.post("/action-items")
async def create_action_item(
    action_item_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new action item from chat"""
    try:
        action_item = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "title": action_item_data.get("title", "Action Item"),
            "description": action_item_data.get("description"),
            "deadline": action_item_data.get("deadline"),
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "session_id": action_item_data.get("session_id")
        }
        
        return {"success": True, "data": action_item}
    except Exception as e:
        logger.error(f"Error creating action item: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating action item")

@router.put("/action-items/{item_id}")
async def update_action_item(
    item_id: str,
    action_item_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update an action item"""
    try:
        # In production, update in database
        return {"success": True, "data": action_item_data}
    except Exception as e:
        logger.error(f"Error updating action item: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating action item")

@router.delete("/action-items/{item_id}")
async def delete_action_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an action item"""
    try:
        # In production, delete from database
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting action item: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting action item")

def analyze_onboarding_survey(survey: OnboardingSurvey) -> List[str]:
    """Analyze onboarding survey to recommend therapy modalities"""
    recommendations = []
    
    # Base recommendations
    if "anxiety" in [concern.lower() for concern in survey.primary_concerns]:
        recommendations.extend(["cbt", "act"])
    
    if "depression" in [concern.lower() for concern in survey.primary_concerns]:
        recommendations.extend(["cbt", "positive_psychology"])
    
    if "trauma" in [concern.lower() for concern in survey.primary_concerns]:
        recommendations.append("somotherapy")
    
    if "meaning" in [concern.lower() for concern in survey.primary_concerns] or "purpose" in [concern.lower() for concern in survey.primary_concerns]:
        recommendations.append("logotherapy")
    
    if "relationships" in [concern.lower() for concern in survey.primary_concerns]:
        recommendations.append("dbt")
    
    # Add user preferences
    recommendations.extend(survey.preferred_modalities)
    
    # Remove duplicates and limit to top 3
    unique_recommendations = list(dict.fromkeys(recommendations))
    return unique_recommendations[:3]

def generate_therapy_recommendations(profile: Dict[str, Any], sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate personalized therapy recommendations"""
    recommendations = []
    
    if not sessions:
        # New user recommendations
        recommendations.append({
            "modality": "cbt",
            "reason": "Great starting point for most mental health concerns",
            "confidence": 0.8
        })
        recommendations.append({
            "modality": "positive_psychology",
            "reason": "Builds positive habits and well-being",
            "confidence": 0.7
        })
    else:
        # Analyze session history
        modality_usage = {}
        mood_improvements = {}
        
        for session in sessions:
            modality = session.get("therapy_type", "unknown")
            modality_usage[modality] = modality_usage.get(modality, 0) + 1
            
            # Track mood improvements
            mood_before = session.get("mood_before")
            mood_after = session.get("mood_after")
            if mood_before and mood_after:
                if modality not in mood_improvements:
                    mood_improvements[modality] = []
                mood_improvements[modality].append(mood_after - mood_before)
        
        # Recommend modalities with good mood improvements
        for modality, improvements in mood_improvements.items():
            avg_improvement = sum(improvements) / len(improvements)
            if avg_improvement > 1:  # Significant improvement
                recommendations.append({
                    "modality": modality,
                    "reason": f"Shows {avg_improvement:.1f} point mood improvement on average",
                    "confidence": min(0.9, 0.6 + avg_improvement * 0.1)
                })
        
        # Recommend trying new modalities if user has been using the same one
        if len(modality_usage) <= 2:
            available_modalities = ["cbt", "logotherapy", "act", "dbt", "somotherapy", "positive_psychology"]
            unused_modalities = [m for m in available_modalities if m not in modality_usage]
            
            if unused_modalities:
                recommendations.append({
                    "modality": unused_modalities[0],
                    "reason": "Try a different approach to expand your therapeutic toolkit",
                    "confidence": 0.6
                })
    
    return recommendations[:3]  # Return top 3 recommendations

def analyze_mood_trends(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze mood trends from therapy sessions"""
    if not sessions:
        return {"trend": "no_data", "average_improvement": 0}
    
    mood_improvements = []
    for session in sessions:
        mood_before = session.get("mood_before")
        mood_after = session.get("mood_after")
        if mood_before and mood_after:
            mood_improvements.append(mood_after - mood_before)
    
    if not mood_improvements:
        return {"trend": "no_mood_data", "average_improvement": 0}
    
    avg_improvement = sum(mood_improvements) / len(mood_improvements)
    
    if avg_improvement > 1:
        trend = "improving"
    elif avg_improvement > 0:
        trend = "slightly_improving"
    elif avg_improvement > -1:
        trend = "stable"
    else:
        trend = "declining"
    
    return {
        "trend": trend,
        "average_improvement": avg_improvement,
        "sessions_with_mood_data": len(mood_improvements)
    } 

def extract_action_items(content):
    """Extract action items from AI response"""
    action_items = []
    
    # Simple extraction logic - in production, use more sophisticated NLP
    lines = content.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in ['try', 'practice', 'do', 'complete', 'schedule']):
            action_items.append({
                "title": "Action Item",
                "description": line.strip(),
                "icon": "fas fa-lightbulb"
            })
    
    return action_items

def getUserContext(current_user: dict) -> str:
    """Get user context string for personalization"""
    context_parts = []
    
    # Add user name
    if current_user.get("first_name"):
        if current_user.get("last_name"):
            context_parts.append(f"User: {current_user['first_name']} {current_user['last_name']}")
        else:
            context_parts.append(f"User: {current_user['first_name']}")
    elif current_user.get("username"):
        context_parts.append(f"User: {current_user['username']}")
    
    # Add age
    if current_user.get("age"):
        context_parts.append(f"Age: {current_user['age']}")
    
    # Add education
    if current_user.get("education_level"):
        education_map = {
            'high_school': 'High School',
            'some_college': 'Some College',
            'associates': "Associate's Degree",
            'bachelors': "Bachelor's Degree",
            'masters': "Master's Degree",
            'doctorate': 'Doctorate',
            'other': 'Other'
        }
        education = education_map.get(current_user['education_level'], current_user['education_level'])
        context_parts.append(f"Education: {education}")
    
    return "\n".join(context_parts) 