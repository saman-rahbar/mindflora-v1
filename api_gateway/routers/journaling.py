from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import random

router = APIRouter()

# Import authentication dependency
from .auth import get_current_user
from .gamification import award_xp, update_streak

# Import privacy utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from privacy_utils.ldp_utils import LDPUtils

# In-memory journal storage (replace with database in production)
user_journals = {}
mood_entries = {}
reflection_prompts = {}

# Initialize privacy utilities
ldp_utils = LDPUtils(epsilon=1.0)

class JournalEntry(BaseModel):
    content: str
    mood_rating: Optional[int] = None  # 1-10 scale
    tags: Optional[List[str]] = None
    is_private: bool = True
    reflection_type: Optional[str] = None  # "gratitude", "challenge", "growth", "freeform"

class MoodEntry(BaseModel):
    mood_rating: int  # 1-10 scale
    energy_level: Optional[int] = None  # 1-10 scale
    stress_level: Optional[int] = None  # 1-10 scale
    notes: Optional[str] = None
    activities: Optional[List[str]] = None

class ReflectionPrompt(BaseModel):
    prompt_id: str
    prompt_text: str
    category: str
    therapy_modality: str

class JournalResponse(BaseModel):
    entry_id: str
    user_id: str
    content: str
    mood_rating: Optional[int]
    tags: List[str]
    is_private: bool
    reflection_type: str
    timestamp: str
    word_count: int

# Reflection prompt templates
REFLECTION_PROMPTS = {
    "gratitude": [
        "What are three things you're grateful for today?",
        "Who made a positive impact on your life recently?",
        "What's something beautiful you noticed today?",
        "What's a challenge you overcame that you're thankful for?",
        "What's something you're looking forward to?"
    ],
    "challenge": [
        "What's a difficult situation you're facing? How are you coping?",
        "What's something that's been on your mind lately?",
        "What's a fear or worry you'd like to explore?",
        "What's a decision you're struggling with?",
        "What's something that's been challenging your beliefs?"
    ],
    "growth": [
        "What's something you learned about yourself recently?",
        "How have you grown in the past month?",
        "What's a goal you're working toward?",
        "What's something you'd like to improve about yourself?",
        "What's a skill you're developing?"
    ],
    "mindfulness": [
        "What's something you noticed about your thoughts today?",
        "How are you feeling in your body right now?",
        "What's something you observed about your environment?",
        "What's a moment of peace you experienced today?",
        "How did you practice self-care today?"
    ],
    "relationships": [
        "How are your relationships supporting your well-being?",
        "What's a meaningful conversation you had recently?",
        "How are you showing up for others?",
        "What's a relationship dynamic you'd like to improve?",
        "Who do you need to connect with more?"
    ]
}

def get_personalized_prompts(user_context: str = "") -> Dict[str, List[str]]:
    """Get personalized reflection prompts based on user context"""
    user_name = ""
    user_age = ""
    user_education = ""
    
    if user_context:
        context_lines = user_context.split('\n')
        for line in context_lines:
            if line.startswith('User:'):
                user_name = line.split(': ')[-1] if ': ' in line else ""
            elif line.startswith('Age:'):
                user_age = line.split(': ')[-1] if ': ' in line else ""
            elif line.startswith('Education:'):
                user_education = line.split(': ')[-1] if ': ' in line else ""
    
    personalized_prompts = REFLECTION_PROMPTS.copy()
    
    if user_name:
        # Add personalized prompts with user's name
        personalized_prompts["gratitude"].append(f"What's something {user_name} is grateful for today?")
        personalized_prompts["growth"].append(f"What's a goal {user_name} is working toward?")
        personalized_prompts["mindfulness"].append(f"How is {user_name} feeling in their body right now?")
    
    if user_age:
        age = int(user_age) if user_age.isdigit() else 0
        if age < 25:
            # Young adult prompts
            personalized_prompts["growth"].append("What's something you're learning about independence and adulthood?")
            personalized_prompts["relationships"].append("How are your friendships evolving as you grow?")
        elif age > 50:
            # Older adult prompts
            personalized_prompts["growth"].append("What wisdom have you gained that you'd like to share?")
            personalized_prompts["gratitude"].append("What life experiences are you most thankful for?")
    
    if user_education:
        if "Bachelor" in user_education or "Master" in user_education or "Doctorate" in user_education:
            # Higher education prompts
            personalized_prompts["growth"].append("How are you applying your education to your personal growth?")
            personalized_prompts["challenge"].append("What intellectual challenges are you currently facing?")
    
    return personalized_prompts

@router.post("/entry", response_model=JournalResponse)
async def create_journal_entry(
    entry_data: JournalEntry,
    current_user: dict = Depends(get_current_user)
):
    """Create a new journal entry"""
    user_id = current_user["id"]
    
    # Validate mood rating
    if entry_data.mood_rating is not None and (entry_data.mood_rating < 1 or entry_data.mood_rating > 10):
        raise HTTPException(
            status_code=400,
            detail="Mood rating must be between 1 and 10"
        )
    
    # Create entry
    entry_id = str(uuid.uuid4())
    entry = {
        "entry_id": entry_id,
        "user_id": user_id,
        "content": entry_data.content,
        "mood_rating": entry_data.mood_rating,
        "tags": entry_data.tags or [],
        "is_private": entry_data.is_private,
        "reflection_type": entry_data.reflection_type or "freeform",
        "timestamp": datetime.utcnow().isoformat(),
        "word_count": len(entry_data.content.split())
    }
    
    # Store entry
    if user_id not in user_journals:
        user_journals[user_id] = []
    user_journals[user_id].append(entry)
    
    # Award XP for journaling
    xp_amount = min(entry["word_count"] // 10, 20)  # Max 20 XP for long entries
    xp_result = award_xp(user_id, xp_amount, f"Journal entry: {entry_data.reflection_type}")
    
    # Update streak
    update_streak(user_id)
    
    # Track mood if provided
    if entry_data.mood_rating is not None:
        await track_mood(user_id, entry_data.mood_rating, entry_data.content)
    
    return JournalResponse(**entry)

@router.get("/entries", response_model=List[JournalResponse])
async def get_journal_entries(
    current_user: dict = Depends(get_current_user),
    reflection_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Get user's journal entries"""
    user_id = current_user["id"]
    
    if user_id not in user_journals:
        return []
    
    entries = user_journals[user_id]
    
    # Filter by reflection type if specified
    if reflection_type:
        entries = [e for e in entries if e["reflection_type"] == reflection_type]
    
    # Sort by timestamp (newest first)
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Apply pagination
    entries = entries[offset:offset + limit]
    
    return [JournalResponse(**entry) for entry in entries]

@router.get("/entry/{entry_id}")
async def get_journal_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific journal entry"""
    user_id = current_user["id"]
    
    if user_id not in user_journals:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Find the entry
    entry = None
    for e in user_journals[user_id]:
        if e["entry_id"] == entry_id:
            entry = e
            break
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return JournalResponse(**entry)

@router.delete("/entry/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a journal entry"""
    user_id = current_user["id"]
    
    if user_id not in user_journals:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Find and remove the entry
    for i, entry in enumerate(user_journals[user_id]):
        if entry["entry_id"] == entry_id:
            del user_journals[user_id][i]
            return {"message": "Entry deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Entry not found")

@router.post("/mood")
async def track_mood_entry(
    mood_data: MoodEntry,
    current_user: dict = Depends(get_current_user)
):
    """Track mood entry"""
    user_id = current_user["id"]
    
    # Validate ratings
    if mood_data.mood_rating < 1 or mood_data.mood_rating > 10:
        raise HTTPException(status_code=400, detail="Mood rating must be between 1 and 10")
    
    if mood_data.energy_level is not None and (mood_data.energy_level < 1 or mood_data.energy_level > 10):
        raise HTTPException(status_code=400, detail="Energy level must be between 1 and 10")
    
    if mood_data.stress_level is not None and (mood_data.stress_level < 1 or mood_data.stress_level > 10):
        raise HTTPException(status_code=400, detail="Stress level must be between 1 and 10")
    
    # Create mood entry
    entry_id = str(uuid.uuid4())
    entry = {
        "entry_id": entry_id,
        "user_id": user_id,
        "mood_rating": mood_data.mood_rating,
        "energy_level": mood_data.energy_level,
        "stress_level": mood_data.stress_level,
        "notes": mood_data.notes,
        "activities": mood_data.activities or [],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Store entry
    if user_id not in mood_entries:
        mood_entries[user_id] = []
    mood_entries[user_id].append(entry)
    
    # Award XP for mood tracking
    xp_result = award_xp(user_id, 5, "Mood tracking")
    
    return {
        "message": "Mood tracked successfully",
        "entry_id": entry_id,
        "xp_earned": 5
    }

@router.get("/mood/history")
async def get_mood_history(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """Get mood history for the specified number of days"""
    user_id = current_user["id"]
    
    if user_id not in mood_entries:
        return {"entries": [], "summary": {}}
    
    # Filter entries by date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    recent_entries = [
        entry for entry in mood_entries[user_id]
        if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
    ]
    
    # Calculate summary statistics
    if recent_entries:
        mood_ratings = [entry["mood_rating"] for entry in recent_entries]
        avg_mood = sum(mood_ratings) / len(mood_ratings)
        
        # Count mood levels
        mood_counts = {}
        for rating in mood_ratings:
            if rating <= 3:
                level = "low"
            elif rating <= 7:
                level = "medium"
            else:
                level = "high"
            mood_counts[level] = mood_counts.get(level, 0) + 1
        
        summary = {
            "total_entries": len(recent_entries),
            "average_mood": round(avg_mood, 2),
            "mood_distribution": mood_counts,
            "tracking_streak": calculate_mood_tracking_streak(user_id)
        }
    else:
        summary = {
            "total_entries": 0,
            "average_mood": 0,
            "mood_distribution": {},
            "tracking_streak": 0
        }
    
    return {
        "entries": recent_entries,
        "summary": summary
    }

@router.get("/prompts")
async def get_reflection_prompts(
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = None,
    therapy_modality: Optional[str] = None
):
    """Get personalized reflection prompts"""
    prompts = []
    
    # Get user context for personalization
    user_context = getUserContext(current_user)
    
    # Get personalized prompts
    personalized_prompts = get_personalized_prompts(user_context)
    
    for prompt_category, prompt_list in personalized_prompts.items():
        if category and prompt_category != category:
            continue
        
        for prompt_text in prompt_list:
            prompt = {
                "prompt_id": f"{prompt_category}_{len(prompts)}",
                "prompt_text": prompt_text,
                "category": prompt_category,
                "therapy_modality": map_category_to_modality(prompt_category)
            }
            
            if therapy_modality and prompt["therapy_modality"] != therapy_modality:
                continue
            
            prompts.append(prompt)
    
    # Randomize order
    random.shuffle(prompts)
    
    return {
        "prompts": prompts[:10],  # Return up to 10 prompts
        "total_available": len(prompts)
    }

@router.get("/analytics")
async def get_journal_analytics(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """Get journaling analytics with privacy protection"""
    user_id = current_user["id"]
    
    if user_id not in user_journals:
        return {"analytics": {}, "privacy_level": "high"}
    
    # Filter entries by date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    recent_entries = [
        entry for entry in user_journals[user_id]
        if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
    ]
    
    if not recent_entries:
        return {"analytics": {}, "privacy_level": "high"}
    
    # Calculate analytics
    total_entries = len(recent_entries)
    total_words = sum(entry["word_count"] for entry in recent_entries)
    avg_words_per_entry = total_words / total_entries if total_entries > 0 else 0
    
    # Reflection type distribution
    reflection_counts = {}
    for entry in recent_entries:
        reflection_type = entry["reflection_type"]
        reflection_counts[reflection_type] = reflection_counts.get(reflection_type, 0) + 1
    
    # Mood trends (if available)
    mood_entries_with_rating = [e for e in recent_entries if e["mood_rating"] is not None]
    mood_trend = None
    if mood_entries_with_rating:
        mood_ratings = [e["mood_rating"] for e in mood_entries_with_rating]
        avg_mood = sum(mood_ratings) / len(mood_ratings)
        mood_trend = "improving" if avg_mood > 6 else "stable" if avg_mood > 4 else "declining"
    
    # Apply privacy protection
    analytics = {
        "total_entries": ldp_utils.add_noise_to_numerical(total_entries, sensitivity=1.0),
        "total_words": ldp_utils.add_noise_to_numerical(total_words, sensitivity=10.0),
        "avg_words_per_entry": ldp_utils.add_noise_to_numerical(avg_words_per_entry, sensitivity=5.0),
        "reflection_type_distribution": reflection_counts,
        "mood_trend": mood_trend,
        "writing_streak": calculate_writing_streak(user_id),
        "most_productive_day": find_most_productive_day(recent_entries)
    }
    
    return {
        "analytics": analytics,
        "privacy_level": "high",
        "data_points": total_entries
    }

@router.get("/export")
async def export_journal_data(
    current_user: dict = Depends(get_current_user)
):
    """Export user's journal data (GDPR compliance)"""
    user_id = current_user["id"]
    
    journal_data = user_journals.get(user_id, [])
    mood_data = mood_entries.get(user_id, [])
    
    # Apply privacy protection to exported data
    protected_journal_data = []
    for entry in journal_data:
        protected_entry = entry.copy()
        # Anonymize content
        protected_entry["content"] = ldp_utils.anonymize_therapy_content(entry["content"])
        protected_journal_data.append(protected_entry)
    
    return {
        "user_id": user_id,
        "journal_entries": protected_journal_data,
        "mood_entries": mood_data,
        "export_timestamp": datetime.utcnow().isoformat(),
        "total_entries": len(protected_journal_data),
        "privacy_note": "Content has been anonymized for privacy protection"
    }

async def track_mood(user_id: str, mood_rating: int, context: str = ""):
    """Helper function to track mood from journal entries"""
    if user_id not in mood_entries:
        mood_entries[user_id] = []
    
    entry = {
        "entry_id": str(uuid.uuid4()),
        "user_id": user_id,
        "mood_rating": mood_rating,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    mood_entries[user_id].append(entry)

def map_category_to_modality(category: str) -> str:
    """Map reflection category to therapy modality"""
    mapping = {
        "gratitude": "positive_psychology",
        "challenge": "cbt",
        "growth": "logotherapy",
        "mindfulness": "cbt",
        "relationships": "dbt"
    }
    return mapping.get(category, "general")

def calculate_mood_tracking_streak(user_id: str) -> int:
    """Calculate consecutive days of mood tracking"""
    if user_id not in mood_entries:
        return 0
    
    entries = mood_entries[user_id]
    if not entries:
        return 0
    
    # Sort by date
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    
    streak = 0
    current_date = datetime.utcnow().date()
    
    for entry in entries:
        entry_date = datetime.fromisoformat(entry["timestamp"]).date()
        if entry_date == current_date - timedelta(days=streak):
            streak += 1
        else:
            break
    
    return streak

def calculate_writing_streak(user_id: str) -> int:
    """Calculate consecutive days of journaling"""
    if user_id not in user_journals:
        return 0
    
    entries = user_journals[user_id]
    if not entries:
        return 0
    
    # Sort by date
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    
    streak = 0
    current_date = datetime.utcnow().date()
    
    for entry in entries:
        entry_date = datetime.fromisoformat(entry["timestamp"]).date()
        if entry_date == current_date - timedelta(days=streak):
            streak += 1
        else:
            break
    
    return streak

def find_most_productive_day(entries: List[Dict[str, Any]]) -> Optional[str]:
    """Find the day with the most journaling activity"""
    if not entries:
        return None
    
    day_counts = {}
    for entry in entries:
        date = datetime.fromisoformat(entry["timestamp"]).date().isoformat()
        day_counts[date] = day_counts.get(date, 0) + 1
    
    if day_counts:
        return max(day_counts.items(), key=lambda x: x[1])[0]
    
    return None

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