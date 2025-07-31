from sqlalchemy.orm import Session
from .models import User, GamificationData, TherapySession, JournalEntry, MoodEntry
from datetime import datetime, timedelta
import json

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, hashed_password: str, **kwargs) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            **kwargs
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create gamification data for new user
        gamification_data = GamificationData(user_id=user.id)
        self.db.add(gamification_data)
        self.db.commit()
        
        return user
    
    def get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> User:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def update_last_login(self, user_id: str):
        """Update user's last login time"""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
    
    def create_therapy_session(self, user_id: str, therapy_type: str, session_content: str, 
                             mood_before: int = None, mood_after: int = None, 
                             ai_response: dict = None, xp_earned: int = 0) -> TherapySession:
        """Create a new therapy session"""
        session = TherapySession(
            user_id=user_id,
            therapy_type=therapy_type,
            session_content=session_content,
            mood_before=mood_before,
            mood_after=mood_after,
            ai_response=json.dumps(ai_response) if ai_response else None,
            xp_earned=xp_earned
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_user_therapy_sessions(self, user_id: str, limit: int = 20) -> list:
        """Get user's therapy sessions"""
        return self.db.query(TherapySession).filter(
            TherapySession.user_id == user_id
        ).order_by(TherapySession.created_at.desc()).limit(limit).all()
    
    def create_journal_entry(self, user_id: str, content: str, reflection_type: str = "freeform", 
                           mood_rating: int = None) -> JournalEntry:
        """Create a new journal entry"""
        entry = JournalEntry(
            user_id=user_id,
            content=content,
            reflection_type=reflection_type,
            mood_rating=mood_rating
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
    
    def get_user_journal_entries(self, user_id: str, limit: int = 20) -> list:
        """Get user's journal entries"""
        return self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).order_by(JournalEntry.created_at.desc()).limit(limit).all()
    
    def create_mood_entry(self, user_id: str, mood_rating: int, notes: str = None) -> MoodEntry:
        """Create a new mood entry"""
        entry = MoodEntry(
            user_id=user_id,
            mood_rating=mood_rating,
            notes=notes
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
    
    def get_user_gamification_data(self, user_id: str) -> GamificationData:
        """Get user's gamification data"""
        return self.db.query(GamificationData).filter(
            GamificationData.user_id == user_id
        ).first()
    
    def update_gamification_data(self, user_id: str, **kwargs):
        """Update user's gamification data"""
        gamification_data = self.get_user_gamification_data(user_id)
        if gamification_data:
            for key, value in kwargs.items():
                if hasattr(gamification_data, key):
                    setattr(gamification_data, key, value)
            gamification_data.updated_at = datetime.utcnow()
            self.db.commit()
    
    def award_xp(self, user_id: str, xp_amount: int):
        """Award XP to user"""
        gamification_data = self.get_user_gamification_data(user_id)
        if gamification_data:
            gamification_data.total_xp += xp_amount
            gamification_data.updated_at = datetime.utcnow()
            
            # Check for level up (every 100 XP = 1 level)
            new_level = (gamification_data.total_xp // 100) + 1
            if new_level > gamification_data.level:
                gamification_data.level = new_level
            
            self.db.commit()
    
    def update_streak(self, user_id: str):
        """Update user's streak"""
        gamification_data = self.get_user_gamification_data(user_id)
        if gamification_data:
            today = datetime.utcnow().date()
            last_activity = gamification_data.last_activity_date.date() if gamification_data.last_activity_date else None
            
            if last_activity is None or last_activity < today:
                if last_activity and (today - last_activity).days == 1:
                    # Consecutive day
                    gamification_data.current_streak += 1
                else:
                    # Reset streak
                    gamification_data.current_streak = 1
                
                gamification_data.last_activity_date = datetime.utcnow()
                gamification_data.updated_at = datetime.utcnow()
                
                # Update longest streak
                if gamification_data.current_streak > gamification_data.longest_streak:
                    gamification_data.longest_streak = gamification_data.current_streak
                
                self.db.commit() 