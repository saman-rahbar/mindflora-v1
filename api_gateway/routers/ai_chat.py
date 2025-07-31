from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime, timedelta
import sys
import os
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm_service.llm_client import create_llm_client
from database.user_service import UserService
from database.connection import get_db
from config import Config

router = APIRouter(prefix="/api/v1/ai-chat", tags=["AI Chat"])

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

# Initialize LLM client with proper error handling
try:
    # Try to use Ollama with llama2 model
    llm_client = create_llm_client("ollama", model="llama2:7b")
    print("✅ LLM client initialized: Ollama (llama2:7b)")
except Exception as e:
    print(f"⚠️  Failed to initialize Ollama client: {e}")
    try:
        # Try OpenAI as fallback
        llm_config = Config.get_llm_config()
        llm_client = create_llm_client(**llm_config)
        print(f"✅ LLM client initialized: {llm_config['client_type']}")
    except Exception as e2:
        print(f"⚠️  Failed to initialize OpenAI client: {e2}")
        try:
            # Try Anthropic as second fallback
            llm_client = create_llm_client("anthropic")
            print("✅ LLM client initialized: Anthropic")
        except Exception as e3:
            print(f"⚠️  Failed to initialize Anthropic client: {e3}")
            print("🔄 Falling back to mock client temporarily")
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
        # Prepare context for LLM
        context = {
            "therapy_type": chat_message.therapy_type or "cbt",
            "session_id": chat_message.session_id,
            "user_context": chat_message.user_context or {}
        }
        
        print(f"🤖 Generating response for therapy type: {chat_message.therapy_type}")
        print(f"📝 User message: {chat_message.message[:100]}...")
        
        try:
            # Generate AI response
            ai_response = await llm_client.generate_response(
                prompt=chat_message.message,
                context=context
            )
            print(f"✅ AI response generated: {ai_response[:100]}...")
            
            # Extract action items (exercises) and insights
            action_items = extract_action_items(ai_response)
            insights = extract_insights(ai_response)
            
            # Generate suggested topics based on the conversation
            suggested_topics = generate_suggested_topics(ai_response, chat_message.message)
            
            return ChatResponse(
                response=ai_response,
                session_id=chat_message.session_id or f"session_{int(time.time())}",
                action_items=action_items,
                therapy_insights=insights,
                suggested_topics=suggested_topics
            )
            
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            # Fallback response
            return ChatResponse(
                response="I'm here to support you. Let's work together to explore what's on your mind. What would be most helpful for you right now?",
                session_id=chat_message.session_id or f"session_{int(time.time())}",
                action_items=[],
                therapy_insights={"themes": [], "mood": None, "progress_notes": []},
                suggested_topics=[]
            )
            
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid request data: {str(e)}")
    except Exception as e:
        print(f"❌ Error processing chat message: {e}")
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
    """Extract action items from AI response, focusing on exercises and practice tasks"""
    action_items = []
    
    # Exercise-specific indicators
    exercise_indicators = [
        "exercise:", "practice:", "try this:", "homework:", "assignment:",
        "try the following", "practice this", "complete this exercise",
        "do this activity", "your task is"
    ]
    
    sentences = response.split('.')
    current_item = None
    
    for sentence in sentences:
        sentence = sentence.strip().lower()
        
        # Check if this sentence starts a new exercise
        is_exercise = any(sentence.startswith(indicator) for indicator in exercise_indicators)
        contains_exercise = any(indicator in sentence for indicator in exercise_indicators)
        
        if is_exercise or contains_exercise:
            if current_item:
                action_items.append(current_item)
            
            # Clean up the sentence
            for indicator in exercise_indicators:
                if indicator in sentence:
                    sentence = sentence.replace(indicator, '').strip()
                    break
            
            current_item = {
                "type": "exercise",
                "title": "Therapeutic Exercise",
                "description": sentence.capitalize(),
                "created_at": datetime.now().isoformat(),
                "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
                "completed": False
            }
        elif current_item and len(sentence) > 10:  # Continue previous exercise description
            current_item["description"] += ". " + sentence.capitalize()
    
    if current_item:
        action_items.append(current_item)
    
    return action_items

def extract_insights(response: str) -> Dict[str, Any]:
    """Extract therapeutic insights from AI response"""
    insights = {
        "themes": [],
        "mood": None,
        "progress_notes": []
    }
    
    # Extract themes
    theme_indicators = ["notice that", "seems like", "appears to be", "might be feeling"]
    for indicator in theme_indicators:
        if indicator in response.lower():
            start_idx = response.lower().find(indicator)
            end_idx = response.find(".", start_idx)
            if end_idx != -1:
                theme = response[start_idx:end_idx].strip()
                insights["themes"].append(theme)
    
    # Extract mood if mentioned
    mood_indicators = ["feeling", "mood seems", "emotional state"]
    for indicator in mood_indicators:
        if indicator in response.lower():
            start_idx = response.lower().find(indicator)
            end_idx = response.find(".", start_idx)
            if end_idx != -1:
                insights["mood"] = response[start_idx:end_idx].strip()
                break
    
    return insights

def generate_suggested_topics(ai_response: str, user_message: str) -> List[str]:
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