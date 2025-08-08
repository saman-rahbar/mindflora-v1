#!/usr/bin/env python3
"""
Test database connection and operations
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from database.connection import get_db, init_db
from database.user_service import UserService
from passlib.context import CryptContext

def test_database():
    """Test database operations"""
    print("🔧 Testing database operations...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Test user service
        user_service = UserService(db)
        
        # Create a test user with unique data
        import uuid
        import time
        
        unique_id = str(uuid.uuid4())[:8]
        timestamp = int(time.time())
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("testpass123")
        
        user = user_service.create_user(
            username=f"test_user_{unique_id}",
            email=f"test_{timestamp}@example.com",
            hashed_password=hashed_password
        )
        
        print(f"✅ User created: {user.username} ({user.id})")
        
        # Test retrieving user
        retrieved_user = user_service.get_user_by_email(f"test_{timestamp}@example.com")
        if retrieved_user:
            print(f"✅ User retrieved: {retrieved_user.username}")
        else:
            print("❌ User not found")
            
        # Test gamification data
        gamification_data = user_service.get_user_gamification_data(user.id)
        if gamification_data:
            print(f"✅ Gamification data created: Level {gamification_data.level}, XP {gamification_data.total_xp}")
        else:
            print("❌ Gamification data not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_database() 