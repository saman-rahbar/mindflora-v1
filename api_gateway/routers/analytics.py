from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
import math

router = APIRouter()

# Import authentication dependency
from .auth import get_current_user

# Import services
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from memory_service.memory import MemoryService
from privacy_utils.ldp_utils import LDPUtils

# Import data from other routers
# Note: These are in-memory stores that would be replaced with database in production
therapy_sessions = {}
user_therapy_history = {}
user_journals = {}
mood_entries = {}
user_progress = {}

# Initialize services
memory_service = MemoryService()
ldp_utils = LDPUtils(epsilon=1.0)

class AnalyticsRequest(BaseModel):
    time_period: str = "30d"  # "7d", "30d", "90d", "1y"
    include_mood: bool = True
    include_therapy: bool = True
    include_journaling: bool = True
    include_gamification: bool = True

class ProgressInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    confidence: float
    data_points: int
    trend: str  # "improving", "stable", "declining", "variable"

class TherapeuticOutcome(BaseModel):
    modality: str
    sessions_count: int
    average_mood_improvement: float
    engagement_score: float
    effectiveness_rating: float

@router.get("/overview")
async def get_analytics_overview(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """Get comprehensive analytics overview with privacy protection"""
    user_id = current_user["id"]
    
    # Get data for the specified period
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Collect data from different sources
    therapy_data = get_therapy_data(user_id, cutoff_date)
    journaling_data = get_journaling_data(user_id, cutoff_date)
    mood_data = get_mood_data(user_id, cutoff_date)
    gamification_data = get_gamification_data(user_id)
    
    # Apply privacy protection
    protected_analytics = apply_privacy_protection({
        "therapy": therapy_data,
        "journaling": journaling_data,
        "mood": mood_data,
        "gamification": gamification_data
    })
    
    # Generate insights
    insights = generate_comprehensive_insights({
        "therapy": therapy_data,
        "journaling": journaling_data,
        "mood": mood_data,
        "gamification": gamification_data
    })
    
    return {
        "period": f"Last {days} days",
        "data_summary": {
            "therapy_sessions": len(therapy_data.get("sessions", [])),
            "journal_entries": len(journaling_data.get("entries", [])),
            "mood_entries": len(mood_data.get("entries", [])),
            "total_activities": len(therapy_data.get("sessions", [])) + len(journaling_data.get("entries", []))
        },
        "analytics": protected_analytics,
        "insights": insights,
        "privacy_level": "high",
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/progress")
async def get_progress_analytics(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """Get detailed progress analytics"""
    user_id = current_user["id"]
    
    # Get therapy sessions
    sessions = []
    if user_id in user_therapy_history:
        for session_id in user_therapy_history[user_id]:
            if session_id in therapy_sessions:
                session = therapy_sessions[session_id]
                session_date = datetime.fromisoformat(session["timestamp"])
                if session_date >= datetime.utcnow() - timedelta(days=days):
                    sessions.append(session)
    
    # Calculate progress metrics
    progress_metrics = calculate_progress_metrics(sessions, user_id)
    
    # Apply privacy protection
    protected_metrics = apply_privacy_protection(progress_metrics)
    
    return {
        "progress_metrics": protected_metrics,
        "period": f"Last {days} days",
        "data_points": len(sessions),
        "privacy_level": "high"
    }

@router.get("/therapeutic-outcomes")
async def get_therapeutic_outcomes(
    current_user: dict = Depends(get_current_user),
    days: int = 90
):
    """Get therapeutic outcomes by modality"""
    user_id = current_user["id"]
    
    # Get therapy sessions
    sessions = []
    if user_id in user_therapy_history:
        for session_id in user_therapy_history[user_id]:
            if session_id in therapy_sessions:
                session = therapy_sessions[session_id]
                session_date = datetime.fromisoformat(session["timestamp"])
                if session_date >= datetime.utcnow() - timedelta(days=days):
                    sessions.append(session)
    
    # Analyze outcomes by modality
    outcomes = analyze_therapeutic_outcomes(sessions)
    
    # Apply privacy protection
    protected_outcomes = []
    for outcome in outcomes:
        protected_outcome = outcome.copy()
        protected_outcome["sessions_count"] = int(ldp_utils.add_noise_to_numerical(
            outcome["sessions_count"], sensitivity=1.0
        ))
        protected_outcome["average_mood_improvement"] = ldp_utils.add_noise_to_numerical(
            outcome["average_mood_improvement"], sensitivity=0.5
        )
        protected_outcomes.append(protected_outcome)
    
    return {
        "therapeutic_outcomes": protected_outcomes,
        "period": f"Last {days} days",
        "total_sessions": len(sessions),
        "privacy_level": "high"
    }

@router.get("/mood-trends")
async def get_mood_trends(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """Get detailed mood trend analysis"""
    user_id = current_user["id"]
    
    if user_id not in mood_entries:
        return {"trends": {}, "insights": [], "data_points": 0}
    
    # Filter entries by date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    recent_entries = [
        entry for entry in mood_entries[user_id]
        if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
    ]
    
    if not recent_entries:
        return {"trends": {}, "insights": [], "data_points": 0}
    
    # Analyze mood trends
    mood_trends = analyze_mood_trends(recent_entries)
    
    # Generate mood insights
    mood_insights = generate_mood_insights(recent_entries)
    
    # Apply privacy protection
    protected_trends = apply_privacy_protection(mood_trends)
    
    return {
        "trends": protected_trends,
        "insights": mood_insights,
        "data_points": len(recent_entries),
        "period": f"Last {days} days",
        "privacy_level": "high"
    }

@router.get("/engagement")
async def get_engagement_analytics(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """Get user engagement analytics"""
    user_id = current_user["id"]
    
    # Calculate engagement metrics
    engagement_metrics = calculate_engagement_metrics(user_id, days)
    
    # Apply privacy protection
    protected_metrics = apply_privacy_protection(engagement_metrics)
    
    return {
        "engagement_metrics": protected_metrics,
        "period": f"Last {days} days",
        "privacy_level": "high"
    }

@router.get("/insights")
async def get_insights(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """Get personalized insights and recommendations"""
    user_id = current_user["id"]
    
    # Collect all data
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    therapy_data = get_therapy_data(user_id, cutoff_date)
    journaling_data = get_journaling_data(user_id, cutoff_date)
    mood_data = get_mood_data(user_id, cutoff_date)
    gamification_data = get_gamification_data(user_id)
    
    # Generate insights
    insights = generate_comprehensive_insights({
        "therapy": therapy_data,
        "journaling": journaling_data,
        "mood": mood_data,
        "gamification": gamification_data
    })
    
    return {
        "insights": insights,
        "period": f"Last {days} days",
        "generated_at": datetime.utcnow().isoformat()
    }

def get_therapy_data(user_id: str, cutoff_date: datetime) -> Dict[str, Any]:
    """Get therapy data for analytics"""
    sessions = []
    if user_id in user_therapy_history:
        for session_id in user_therapy_history[user_id]:
            if session_id in therapy_sessions:
                session = therapy_sessions[session_id]
                session_date = datetime.fromisoformat(session["timestamp"])
                if session_date >= cutoff_date:
                    sessions.append(session)
    
    return {
        "sessions": sessions,
        "modality_usage": count_modality_usage(sessions),
        "mood_improvements": extract_mood_improvements(sessions)
    }

def get_journaling_data(user_id: str, cutoff_date: datetime) -> Dict[str, Any]:
    """Get journaling data for analytics"""
    entries = []
    if user_id in user_journals:
        for entry in user_journals[user_id]:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date >= cutoff_date:
                entries.append(entry)
    
    return {
        "entries": entries,
        "reflection_types": count_reflection_types(entries),
        "word_counts": [entry["word_count"] for entry in entries]
    }

def get_mood_data(user_id: str, cutoff_date: datetime) -> Dict[str, Any]:
    """Get mood data for analytics"""
    entries = []
    if user_id in mood_entries:
        for entry in mood_entries[user_id]:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date >= cutoff_date:
                entries.append(entry)
    
    return {
        "entries": entries,
        "ratings": [entry["mood_rating"] for entry in entries],
        "timestamps": [entry["timestamp"] for entry in entries]
    }

def get_gamification_data(user_id: str) -> Dict[str, Any]:
    """Get gamification data for analytics"""
    if user_id not in user_progress:
        return {}
    
    progress = user_progress[user_id]
    return {
        "total_xp": progress.get("total_xp", 0),
        "level": progress.get("level", 1),
        "current_streak": progress.get("current_streak", 0),
        "achievements": len(progress.get("achievements", [])),
        "missions_completed": len(progress.get("missions_completed", []))
    }

def count_modality_usage(sessions: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count therapy modality usage"""
    usage = {}
    for session in sessions:
        modality = session.get("therapy_type", "unknown")
        usage[modality] = usage.get(modality, 0) + 1
    return usage

def extract_mood_improvements(sessions: List[Dict[str, Any]]) -> List[float]:
    """Extract mood improvements from therapy sessions"""
    improvements = []
    for session in sessions:
        mood_before = session.get("mood_before")
        mood_after = session.get("mood_after")
        if mood_before is not None and mood_after is not None:
            improvements.append(mood_after - mood_before)
    return improvements

def count_reflection_types(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count journal reflection types"""
    types = {}
    for entry in entries:
        reflection_type = entry.get("reflection_type", "freeform")
        types[reflection_type] = types.get(reflection_type, 0) + 1
    return types

def calculate_progress_metrics(sessions: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
    """Calculate progress metrics from therapy sessions"""
    if not sessions:
        return {}
    
    # Calculate mood improvements
    mood_improvements = extract_mood_improvements(sessions)
    avg_mood_improvement = statistics.mean(mood_improvements) if mood_improvements else 0
    
    # Calculate session frequency
    session_dates = [datetime.fromisoformat(s["timestamp"]).date() for s in sessions]
    unique_days = len(set(session_dates))
    avg_sessions_per_day = len(sessions) / max(unique_days, 1)
    
    # Calculate modality diversity
    modalities = set(s.get("therapy_type") for s in sessions)
    modality_diversity = len(modalities)
    
    return {
        "total_sessions": len(sessions),
        "average_mood_improvement": avg_mood_improvement,
        "session_frequency": avg_sessions_per_day,
        "modality_diversity": modality_diversity,
        "unique_days": unique_days,
        "most_used_modality": max(count_modality_usage(sessions).items(), key=lambda x: x[1])[0] if sessions else None
    }

def analyze_therapeutic_outcomes(sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze therapeutic outcomes by modality"""
    outcomes = []
    
    # Group sessions by modality
    modality_sessions = {}
    for session in sessions:
        modality = session.get("therapy_type", "unknown")
        if modality not in modality_sessions:
            modality_sessions[modality] = []
        modality_sessions[modality].append(session)
    
    # Analyze each modality
    for modality, modality_sessions_list in modality_sessions.items():
        mood_improvements = extract_mood_improvements(modality_sessions_list)
        avg_improvement = statistics.mean(mood_improvements) if mood_improvements else 0
        
        # Calculate engagement score (sessions per week)
        session_dates = [datetime.fromisoformat(s["timestamp"]).date() for s in modality_sessions_list]
        unique_days = len(set(session_dates))
        engagement_score = len(modality_sessions_list) / max(unique_days / 7, 1)  # sessions per week
        
        # Calculate effectiveness rating
        effectiveness_rating = min(10, max(1, (avg_improvement + 2) * 2))  # Scale to 1-10
        
        outcomes.append({
            "modality": modality,
            "sessions_count": len(modality_sessions_list),
            "average_mood_improvement": avg_improvement,
            "engagement_score": engagement_score,
            "effectiveness_rating": effectiveness_rating
        })
    
    return outcomes

def analyze_mood_trends(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze mood trends from entries"""
    if not entries:
        return {}
    
    # Sort by timestamp
    entries.sort(key=lambda x: x["timestamp"])
    
    # Extract mood ratings and timestamps
    ratings = [entry["mood_rating"] for entry in entries]
    timestamps = [entry["timestamp"] for entry in entries]
    
    # Calculate basic statistics
    avg_mood = statistics.mean(ratings)
    mood_std = statistics.stdev(ratings) if len(ratings) > 1 else 0
    
    # Calculate trend
    if len(ratings) >= 2:
        # Simple linear trend calculation
        x_values = list(range(len(ratings)))
        slope = calculate_linear_trend(x_values, ratings)
        
        if slope > 0.1:
            trend = "improving"
        elif slope < -0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    # Calculate weekly averages
    weekly_averages = calculate_weekly_averages(entries)
    
    return {
        "average_mood": avg_mood,
        "mood_volatility": mood_std,
        "trend": trend,
        "total_entries": len(entries),
        "weekly_averages": weekly_averages,
        "mood_distribution": {
            "low": len([r for r in ratings if r <= 3]),
            "medium": len([r for r in ratings if 3 < r <= 7]),
            "high": len([r for r in ratings if r > 7])
        }
    }

def calculate_linear_trend(x_values: List[int], y_values: List[float]) -> float:
    """Calculate linear trend slope"""
    n = len(x_values)
    if n < 2:
        return 0
    
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x * x for x in x_values)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    return slope

def calculate_weekly_averages(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate weekly mood averages"""
    weekly_data = {}
    
    for entry in entries:
        date = datetime.fromisoformat(entry["timestamp"]).date()
        week_start = date - timedelta(days=date.weekday())
        week_key = week_start.isoformat()
        
        if week_key not in weekly_data:
            weekly_data[week_key] = []
        weekly_data[week_key].append(entry["mood_rating"])
    
    weekly_averages = []
    for week_start, ratings in weekly_data.items():
        weekly_averages.append({
            "week_start": week_start,
            "average_mood": statistics.mean(ratings),
            "entries_count": len(ratings)
        })
    
    return weekly_averages

def generate_mood_insights(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate insights from mood data"""
    insights = []
    
    if not entries:
        return insights
    
    ratings = [entry["mood_rating"] for entry in entries]
    avg_mood = statistics.mean(ratings)
    
    # Insight 1: Overall mood level
    if avg_mood >= 7:
        insights.append({
            "type": "positive",
            "title": "Strong Mood Foundation",
            "description": f"Your average mood of {avg_mood:.1f}/10 shows good emotional well-being.",
            "confidence": 0.8
        })
    elif avg_mood <= 4:
        insights.append({
            "type": "concern",
            "title": "Mood Support Needed",
            "description": f"Your average mood of {avg_mood:.1f}/10 suggests you might benefit from additional support.",
            "confidence": 0.7
        })
    
    # Insight 2: Consistency
    mood_std = statistics.stdev(ratings) if len(ratings) > 1 else 0
    if mood_std < 1.5:
        insights.append({
            "type": "observation",
            "title": "Stable Mood Pattern",
            "description": "Your mood has been quite consistent, which can indicate emotional stability.",
            "confidence": 0.6
        })
    elif mood_std > 2.5:
        insights.append({
            "type": "observation",
            "title": "Variable Mood Pattern",
            "description": "Your mood shows significant variation, which is normal but worth monitoring.",
            "confidence": 0.6
        })
    
    return insights

def calculate_engagement_metrics(user_id: str, days: int) -> Dict[str, Any]:
    """Calculate user engagement metrics"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Count activities
    therapy_count = 0
    if user_id in user_therapy_history:
        for session_id in user_therapy_history[user_id]:
            if session_id in therapy_sessions:
                session = therapy_sessions[session_id]
                if datetime.fromisoformat(session["timestamp"]) >= cutoff_date:
                    therapy_count += 1
    
    journal_count = 0
    if user_id in user_journals:
        for entry in user_journals[user_id]:
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date:
                journal_count += 1
    
    mood_count = 0
    if user_id in mood_entries:
        for entry in mood_entries[user_id]:
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date:
                mood_count += 1
    
    total_activities = therapy_count + journal_count + mood_count
    engagement_score = min(100, (total_activities / days) * 10)  # Scale to 0-100
    
    return {
        "total_activities": total_activities,
        "therapy_sessions": therapy_count,
        "journal_entries": journal_count,
        "mood_entries": mood_count,
        "engagement_score": engagement_score,
        "activity_frequency": total_activities / max(days, 1)
    }

def generate_comprehensive_insights(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate comprehensive insights from all data sources"""
    insights = []
    
    # Therapy insights
    therapy_data = data.get("therapy", {})
    therapy_sessions = therapy_data.get("sessions", [])
    
    if therapy_sessions:
        modality_usage = therapy_data.get("modality_usage", {})
        most_used = max(modality_usage.items(), key=lambda x: x[1])[0] if modality_usage else None
        
        insights.append({
            "type": "therapy",
            "title": "Therapy Engagement",
            "description": f"You've completed {len(therapy_sessions)} therapy sessions, with {most_used} being your preferred modality.",
            "confidence": 0.8
        })
    
    # Journaling insights
    journaling_data = data.get("journaling", {})
    journal_entries = journaling_data.get("entries", [])
    
    if journal_entries:
        total_words = sum(entry.get("word_count", 0) for entry in journal_entries)
        avg_words = total_words / len(journal_entries)
        
        insights.append({
            "type": "journaling",
            "title": "Reflection Practice",
            "description": f"You've written {len(journal_entries)} journal entries with an average of {avg_words:.0f} words each.",
            "confidence": 0.7
        })
    
    # Mood insights
    mood_data = data.get("mood", {})
    mood_entries = mood_data.get("entries", [])
    
    if mood_entries:
        ratings = mood_data.get("ratings", [])
        avg_mood = statistics.mean(ratings) if ratings else 0
        
        insights.append({
            "type": "mood",
            "title": "Mood Awareness",
            "description": f"You've tracked your mood {len(mood_entries)} times with an average rating of {avg_mood:.1f}/10.",
            "confidence": 0.6
        })
    
    return insights

def apply_privacy_protection(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply privacy protection to analytics data"""
    protected_data = {}
    
    for key, value in data.items():
        if isinstance(value, dict):
            protected_data[key] = apply_privacy_protection(value)
        elif isinstance(value, (int, float)):
            # Add noise to numerical values
            protected_data[key] = ldp_utils.add_noise_to_numerical(value, sensitivity=1.0)
        elif isinstance(value, list):
            # For lists, apply protection to numerical elements
            protected_data[key] = [
                ldp_utils.add_noise_to_numerical(item, sensitivity=1.0) if isinstance(item, (int, float)) else item
                for item in value
            ]
        else:
            protected_data[key] = value
    
    return protected_data 