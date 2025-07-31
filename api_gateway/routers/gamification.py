from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import random

router = APIRouter()

# Import authentication dependency
from .auth import get_current_user

# In-memory gamification storage (replace with database in production)
user_progress = {}
achievements_db = {}
daily_missions = {}
streaks_db = {}

# Achievement definitions
ACHIEVEMENTS = {
    "first_session": {
        "id": "first_session",
        "name": "First Steps",
        "description": "Complete your first therapy session",
        "icon": "🌱",
        "xp_reward": 50,
        "category": "milestone"
    },
    "week_streak": {
        "id": "week_streak",
        "name": "Consistency Champion",
        "description": "Complete 7 days in a row",
        "icon": "🔥",
        "xp_reward": 100,
        "category": "streak"
    },
    "month_streak": {
        "id": "month_streak",
        "name": "Dedication Master",
        "description": "Complete 30 days in a row",
        "icon": "👑",
        "xp_reward": 500,
        "category": "streak"
    },
    "journal_master": {
        "id": "journal_master",
        "name": "Reflection Master",
        "description": "Write 10 journal entries",
        "icon": "📝",
        "xp_reward": 75,
        "category": "activity"
    },
    "mood_tracker": {
        "id": "mood_tracker",
        "name": "Mood Explorer",
        "description": "Track your mood for 5 consecutive days",
        "icon": "🌈",
        "xp_reward": 60,
        "category": "activity"
    },
    "therapy_explorer": {
        "id": "therapy_explorer",
        "name": "Therapy Explorer",
        "description": "Try 3 different therapy modalities",
        "icon": "🧠",
        "xp_reward": 150,
        "category": "exploration"
    },
    "self_care": {
        "id": "self_care",
        "name": "Self-Care Advocate",
        "description": "Complete 5 self-care activities",
        "icon": "💖",
        "xp_reward": 80,
        "category": "wellness"
    }
}

# Daily mission templates
DAILY_MISSION_TEMPLATES = [
    {
        "id": "gratitude_journal",
        "title": "Gratitude Reflection",
        "description": "Write down 3 things you're grateful for today",
        "xp_reward": 20,
        "category": "reflection",
        "therapy_modality": "positive_psychology"
    },
    {
        "id": "mindful_breathing",
        "title": "Mindful Breathing",
        "description": "Practice 5 minutes of mindful breathing",
        "xp_reward": 15,
        "category": "mindfulness",
        "therapy_modality": "cbt"
    },
    {
        "id": "thought_record",
        "title": "Thought Record",
        "description": "Record and challenge one negative thought",
        "xp_reward": 25,
        "category": "cbt",
        "therapy_modality": "cbt"
    },
    {
        "id": "value_exploration",
        "title": "Value Exploration",
        "description": "Reflect on what matters most to you",
        "xp_reward": 30,
        "category": "meaning",
        "therapy_modality": "logotherapy"
    },
    {
        "id": "body_scan",
        "title": "Body Awareness",
        "description": "Practice a 10-minute body scan meditation",
        "xp_reward": 20,
        "category": "somatic",
        "therapy_modality": "somotherapy"
    },
    {
        "id": "kindness_act",
        "title": "Random Act of Kindness",
        "description": "Perform one act of kindness for someone else",
        "xp_reward": 25,
        "category": "connection",
        "therapy_modality": "positive_psychology"
    }
]

class MissionCompletion(BaseModel):
    mission_id: str
    completion_notes: Optional[str] = None

class AchievementResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    xp_reward: int
    category: str
    unlocked_at: str

class UserProgress(BaseModel):
    user_id: str
    total_xp: int
    level: int
    current_streak: int
    longest_streak: int
    achievements_unlocked: int
    total_achievements: int
    missions_completed_today: int
    last_activity: str

def calculate_level(xp: int) -> int:
    """Calculate user level based on XP"""
    # Simple level calculation: every 100 XP = 1 level
    return max(1, xp // 100 + 1)

def get_xp_for_level(level: int) -> int:
    """Get XP required for a specific level"""
    return (level - 1) * 100

def get_xp_to_next_level(current_xp: int) -> int:
    """Get XP needed to reach next level"""
    current_level = calculate_level(current_xp)
    next_level_xp = get_xp_for_level(current_level + 1)
    return next_level_xp - current_xp

def initialize_user_progress(user_id: str):
    """Initialize user progress if not exists"""
    if user_id not in user_progress:
        user_progress[user_id] = {
            "user_id": user_id,
            "total_xp": 0,
            "level": 1,
            "current_streak": 0,
            "longest_streak": 0,
            "achievements": [],
            "missions_completed": [],
            "last_activity": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
    
    if user_id not in streaks_db:
        streaks_db[user_id] = {
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity_date": None
        }

def award_xp(user_id: str, xp_amount: int, reason: str):
    """Award XP to user"""
    initialize_user_progress(user_id)
    
    old_level = user_progress[user_id]["level"]
    user_progress[user_id]["total_xp"] += xp_amount
    user_progress[user_id]["level"] = calculate_level(user_progress[user_id]["total_xp"])
    user_progress[user_id]["last_activity"] = datetime.utcnow().isoformat()
    
    new_level = user_progress[user_id]["level"]
    
    return {
        "xp_awarded": xp_amount,
        "total_xp": user_progress[user_id]["total_xp"],
        "level_up": new_level > old_level,
        "old_level": old_level,
        "new_level": new_level,
        "xp_to_next_level": get_xp_to_next_level(user_progress[user_id]["total_xp"]),
        "reason": reason
    }

def check_achievements(user_id: str) -> List[Dict[str, Any]]:
    """Check and award achievements based on user progress"""
    initialize_user_progress(user_id)
    progress = user_progress[user_id]
    newly_unlocked = []
    
    # Check first session achievement
    if len(progress["missions_completed"]) >= 1 and "first_session" not in [a["id"] for a in progress["achievements"]]:
        achievement = ACHIEVEMENTS["first_session"].copy()
        achievement["unlocked_at"] = datetime.utcnow().isoformat()
        progress["achievements"].append(achievement)
        newly_unlocked.append(achievement)
        award_xp(user_id, achievement["xp_reward"], f"Achievement: {achievement['name']}")
    
    # Check week streak achievement
    if progress["current_streak"] >= 7 and "week_streak" not in [a["id"] for a in progress["achievements"]]:
        achievement = ACHIEVEMENTS["week_streak"].copy()
        achievement["unlocked_at"] = datetime.utcnow().isoformat()
        progress["achievements"].append(achievement)
        newly_unlocked.append(achievement)
        award_xp(user_id, achievement["xp_reward"], f"Achievement: {achievement['name']}")
    
    # Check month streak achievement
    if progress["current_streak"] >= 30 and "month_streak" not in [a["id"] for a in progress["achievements"]]:
        achievement = ACHIEVEMENTS["month_streak"].copy()
        achievement["unlocked_at"] = datetime.utcnow().isoformat()
        progress["achievements"].append(achievement)
        newly_unlocked.append(achievement)
        award_xp(user_id, achievement["xp_reward"], f"Achievement: {achievement['name']}")
    
    return newly_unlocked

def update_streak(user_id: str):
    """Update user streak based on activity"""
    initialize_user_progress(user_id)
    
    today = datetime.utcnow().date()
    last_activity = streaks_db[user_id]["last_activity_date"]
    
    if last_activity is None:
        # First activity
        streaks_db[user_id]["current_streak"] = 1
        streaks_db[user_id]["last_activity_date"] = today
    elif last_activity == today:
        # Already logged activity today
        pass
    elif last_activity == today - timedelta(days=1):
        # Consecutive day
        streaks_db[user_id]["current_streak"] += 1
        streaks_db[user_id]["last_activity_date"] = today
    else:
        # Streak broken
        streaks_db[user_id]["current_streak"] = 1
        streaks_db[user_id]["last_activity_date"] = today
    
    # Update longest streak
    if streaks_db[user_id]["current_streak"] > streaks_db[user_id]["longest_streak"]:
        streaks_db[user_id]["longest_streak"] = streaks_db[user_id]["current_streak"]
    
    # Update user progress
    user_progress[user_id]["current_streak"] = streaks_db[user_id]["current_streak"]
    user_progress[user_id]["longest_streak"] = streaks_db[user_id]["longest_streak"]

def generate_daily_missions(user_id: str) -> List[Dict[str, Any]]:
    """Generate daily missions for user"""
    today = datetime.utcnow().date().isoformat()
    
    if user_id not in daily_missions or daily_missions[user_id].get("date") != today:
        # Generate new missions for today
        selected_missions = random.sample(DAILY_MISSION_TEMPLATES, min(3, len(DAILY_MISSION_TEMPLATES)))
        
        daily_missions[user_id] = {
            "date": today,
            "missions": [
                {
                    **mission,
                    "completed": False,
                    "completion_time": None,
                    "completion_notes": None
                }
                for mission in selected_missions
            ]
        }
    
    return daily_missions[user_id]["missions"]

@router.get("/progress")
async def get_user_progress(current_user: dict = Depends(get_current_user)):
    """Get user's gamification progress"""
    user_id = current_user["id"]
    initialize_user_progress(user_id)
    
    progress = user_progress[user_id]
    
    return UserProgress(
        user_id=user_id,
        total_xp=progress["total_xp"],
        level=progress["level"],
        current_streak=progress["current_streak"],
        longest_streak=progress["longest_streak"],
        achievements_unlocked=len(progress["achievements"]),
        total_achievements=len(ACHIEVEMENTS),
        missions_completed_today=len([m for m in progress["missions_completed"] 
                                    if m["completed_date"] == datetime.utcnow().date().isoformat()]),
        last_activity=progress["last_activity"]
    )

@router.get("/achievements")
async def get_user_achievements(current_user: dict = Depends(get_current_user)):
    """Get user's achievements"""
    user_id = current_user["id"]
    initialize_user_progress(user_id)
    
    progress = user_progress[user_id]
    
    return {
        "unlocked_achievements": progress["achievements"],
        "available_achievements": [
            {**achievement, "unlocked": achievement["id"] in [a["id"] for a in progress["achievements"]]}
            for achievement in ACHIEVEMENTS.values()
        ],
        "total_unlocked": len(progress["achievements"]),
        "total_available": len(ACHIEVEMENTS)
    }

@router.get("/daily-missions")
async def get_daily_missions(current_user: dict = Depends(get_current_user)):
    """Get user's daily missions"""
    user_id = current_user["id"]
    missions = generate_daily_missions(user_id)
    
    return {
        "date": datetime.utcnow().date().isoformat(),
        "missions": missions,
        "completed_count": len([m for m in missions if m["completed"]]),
        "total_count": len(missions)
    }

@router.post("/complete-mission")
async def complete_mission(
    mission_data: MissionCompletion,
    current_user: dict = Depends(get_current_user)
):
    """Complete a daily mission"""
    user_id = current_user["id"]
    missions = generate_daily_missions(user_id)
    
    # Find the mission
    mission = None
    for m in missions:
        if m["id"] == mission_data.mission_id:
            mission = m
            break
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if mission["completed"]:
        raise HTTPException(status_code=400, detail="Mission already completed")
    
    # Mark mission as completed
    mission["completed"] = True
    mission["completion_time"] = datetime.utcnow().isoformat()
    mission["completion_notes"] = mission_data.completion_notes
    
    # Award XP
    xp_result = award_xp(user_id, mission["xp_reward"], f"Mission: {mission['title']}")
    
    # Update streak
    update_streak(user_id)
    
    # Check for new achievements
    new_achievements = check_achievements(user_id)
    
    # Record completion
    user_progress[user_id]["missions_completed"].append({
        "mission_id": mission["id"],
        "completed_date": datetime.utcnow().date().isoformat(),
        "xp_earned": mission["xp_reward"]
    })
    
    return {
        "message": "Mission completed successfully",
        "mission": mission,
        "xp_result": xp_result,
        "new_achievements": new_achievements
    }

@router.post("/award-xp")
async def award_xp_manual(
    xp_amount: int,
    reason: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually award XP (for testing or special events)"""
    user_id = current_user["id"]
    result = award_xp(user_id, xp_amount, reason)
    
    # Check for new achievements
    new_achievements = check_achievements(user_id)
    
    return {
        "message": f"Awarded {xp_amount} XP for: {reason}",
        "xp_result": result,
        "new_achievements": new_achievements
    }

@router.get("/leaderboard")
async def get_leaderboard(current_user: dict = Depends(get_current_user)):
    """Get leaderboard (top users by XP)"""
    # Sort users by XP
    sorted_users = sorted(
        user_progress.values(),
        key=lambda x: x["total_xp"],
        reverse=True
    )[:10]  # Top 10
    
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": user["user_id"],
                "total_xp": user["total_xp"],
                "level": user["level"],
                "current_streak": user["current_streak"]
            }
            for i, user in enumerate(sorted_users)
        ]
    }

@router.get("/stats")
async def get_gamification_stats(current_user: dict = Depends(get_current_user)):
    """Get detailed gamification statistics"""
    user_id = current_user["id"]
    initialize_user_progress(user_id)
    
    progress = user_progress[user_id]
    
    return {
        "xp_stats": {
            "total_xp": progress["total_xp"],
            "level": progress["level"],
            "xp_to_next_level": get_xp_to_next_level(progress["total_xp"]),
            "level_progress_percentage": (progress["total_xp"] % 100) / 100 * 100
        },
        "streak_stats": {
            "current_streak": progress["current_streak"],
            "longest_streak": progress["longest_streak"],
            "streak_rank": "🔥" * min(progress["current_streak"], 5)
        },
        "achievement_stats": {
            "unlocked": len(progress["achievements"]),
            "total": len(ACHIEVEMENTS),
            "completion_percentage": (len(progress["achievements"]) / len(ACHIEVEMENTS)) * 100
        },
        "activity_stats": {
            "missions_completed": len(progress["missions_completed"]),
            "last_activity": progress["last_activity"],
            "days_active": (datetime.utcnow() - datetime.fromisoformat(progress["created_at"])).days
        }
    } 