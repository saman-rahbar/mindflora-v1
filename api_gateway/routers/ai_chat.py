from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm_service.llm_client import create_llm_client
from database.user_service import UserService
from database.connection import get_db

router = APIRouter(tags=["AI Chat"])

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    therapy_type: Optional[str] = "cbt"
    user_context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    action_items: Optional[List[Dict[str, Any]]] = None
    therapy_insights: Optional[Dict[str, Any]] = None
    suggested_topics: Optional[List[str]] = None

class ChatSession(BaseModel):
    session_id: str
    user_id: str
    start_time: datetime
    messages: List[Dict[str, Any]]
    therapy_type: str
    action_items: List[Dict[str, Any]]
    insights: Dict[str, Any]

# Initialize LLM client using config
from config import Config

try:
    llm_config = Config.get_llm_config()
    llm_client = create_llm_client(**llm_config)
    print(f"✅ LLM client initialized: {llm_config['client_type']}")
except Exception as e:
    print(f"⚠️  Failed to initialize LLM client: {e}")
    print("🔄 Falling back to mock client")
    llm_client = create_llm_client("mock")

# Store active sessions (in production, use Redis or database)
active_sessions = {}

@router.post("/send-message", response_model=ChatResponse)
async def send_chat_message(
    chat_message: ChatMessage,
    user_service: UserService = Depends(get_db)
) -> ChatResponse:
    """Send a message to the AI therapist and get a response"""
    try:
        # Create or get session
        session_id = chat_message.session_id or f"session_{datetime.now().timestamp()}"
        
        if session_id not in active_sessions:
            active_sessions[session_id] = {
                "messages": [],
                "therapy_type": chat_message.therapy_type,
                "start_time": datetime.now(),
                "action_items": [],
                "insights": {}
            }
        
        session = active_sessions[session_id]
        
        # Add user message to session
        user_msg = {
            "role": "user",
            "content": chat_message.message,
            "timestamp": datetime.now()
        }
        session["messages"].append(user_msg)
        
        # Prepare context for LLM
        context = {
            "therapy_type": chat_message.therapy_type,
            "user_context": chat_message.user_context or {},
            "session_history": session["messages"][-10:],  # Last 10 messages for context
            "action_items": session["action_items"]
        }
        
        # Generate AI response
        print(f"🤖 Generating response for therapy type: {chat_message.therapy_type}")
        print(f"📝 User message: {chat_message.message[:100]}...")
        
        try:
            ai_response = await llm_client.generate_response(
                prompt=chat_message.message,
                context=context
            )
            print(f"✅ AI response generated: {ai_response[:100]}...")
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            # Fallback response
            ai_response = "I'm here to support you. Let's work together to explore what's on your mind. What would be most helpful for you right now?"
        
        # Add AI response to session
        ai_msg = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now()
        }
        session["messages"].append(ai_msg)
        
        # Extract action items and insights (simplified for now)
        action_items = extract_action_items(ai_response)
        insights = extract_insights(ai_response, chat_message.message)
        
        # Update session
        session["action_items"].extend(action_items)
        session["insights"].update(insights)
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            action_items=action_items,
            therapy_insights=insights,
            suggested_topics=generate_suggested_topics(ai_response)
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Invalid request data: {str(e)}")
    except Exception as e:
        print(f"❌ Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

@router.get("/session/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session details"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return {
        "session_id": session_id,
        "start_time": session["start_time"],
        "messages": session["messages"],
        "therapy_type": session["therapy_type"],
        "action_items": session["action_items"],
        "insights": session["insights"]
    }

@router.post("/session/{session_id}/action-items")
async def add_action_item(
    session_id: str,
    action_item: Dict[str, Any]
):
    """Add an action item to a chat session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    session["action_items"].append(action_item)
    
    return {"message": "Action item added successfully"}

@router.delete("/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session"""
    if session_id in active_sessions:
        del active_sessions[session_id]
    
    return {"message": "Session deleted successfully"}

@router.get("/therapy-types")
async def get_therapy_types():
    """Get available therapy types"""
    return {
        "therapy_types": [
            {
                "id": "cbt",
                "name": "Cognitive Behavioral Therapy",
                "description": "Focus on identifying and changing negative thought patterns",
                "icon": "🧠"
            },
            {
                "id": "logotherapy",
                "name": "Logotherapy",
                "description": "Help find meaning and purpose in life experiences",
                "icon": "🎯"
            },
            {
                "id": "act",
                "name": "Acceptance and Commitment Therapy",
                "description": "Accept difficult thoughts and commit to value-based actions",
                "icon": "🌱"
            },
            {
                "id": "dbt",
                "name": "Dialectical Behavior Therapy",
                "description": "Balance acceptance and change through mindfulness",
                "icon": "⚖️"
            },
            {
                "id": "somotherapy",
                "name": "Somotherapy",
                "description": "Body-centered therapy for mind-body integration",
                "icon": "💆"
            },
            {
                "id": "positive_psychology",
                "name": "Positive Psychology",
                "description": "Build on strengths and cultivate positive emotions",
                "icon": "✨"
            }
        ]
    }

def extract_action_items(response: str) -> List[Dict[str, Any]]:
    """Extract action items from AI response - only when explicitly suggested"""
    action_items = []
    
    # Only extract action items when the AI explicitly suggests them
    explicit_action_phrases = [
        "try this exercise:", "practice this technique:", "here's an exercise:",
        "i suggest you try:", "let's practice:", "here's what you can do:",
        "try this activity:", "practice this skill:", "here's a technique:"
    ]
    
    response_lower = response.lower()
    
    # Check for explicit action suggestions
    for phrase in explicit_action_phrases:
        if phrase in response_lower:
            # Find the sentence containing the action
            sentences = response.split('.')
            for sentence in sentences:
                sentence_lower = sentence.strip().lower()
                if any(indicator in sentence_lower for indicator in ["try", "practice", "exercise", "activity", "technique"]):
                    if len(sentence.strip()) > 10:  # Only if it's a substantial suggestion
                        action_items.append({
                            "description": sentence.strip().capitalize(),
                            "created_at": datetime.now().isoformat(),
                            "completed": False
                        })
                        break
    
    return action_items[:2]  # Limit to 2 action items

def extract_insights(ai_response: str, user_message: str) -> Dict[str, Any]:
    """Extract therapeutic insights from the conversation"""
    insights = {
        "mood_indicators": [],
        "cognitive_patterns": [],
        "strengths_identified": [],
        "areas_for_growth": []
    }
    
    # Simple keyword-based analysis
    user_lower = user_message.lower()
    ai_lower = ai_response.lower()
    
    # Mood indicators
    mood_words = ["anxious", "stressed", "sad", "happy", "excited", "worried", "calm"]
    for word in mood_words:
        if word in user_lower:
            insights["mood_indicators"].append(word)
    
    # Cognitive patterns
    cognitive_patterns = ["always", "never", "everyone", "nobody", "should", "must"]
    for pattern in cognitive_patterns:
        if pattern in user_lower:
            insights["cognitive_patterns"].append(pattern)
    
    # Strengths (look for positive language in AI response)
    strength_words = ["strength", "capable", "resilient", "courageous", "determined"]
    for word in strength_words:
        if word in ai_lower:
            insights["strengths_identified"].append(word)
    
    return insights

def generate_suggested_topics(ai_response: str) -> List[str]:
    """Generate suggested follow-up topics based on AI response"""
    topics = []
    
    # Simple topic generation based on keywords
    topic_keywords = {
        "stress": "Stress Management Techniques",
        "anxiety": "Anxiety Coping Strategies", 
        "depression": "Mood Improvement Activities",
        "relationships": "Interpersonal Skills",
        "goals": "Goal Setting and Achievement",
        "mindfulness": "Mindfulness Practices",
        "gratitude": "Gratitude and Appreciation",
        "self-care": "Self-Care Strategies"
    }
    
    response_lower = ai_response.lower()
    for keyword, topic in topic_keywords.items():
        if keyword in response_lower:
            topics.append(topic)
    
    return topics[:3]  # Return top 3 topics 