#!/usr/bin/env python3
"""
Test Database Connection
"""

import sys
import os
sys.path.append('.')

from database.connection import get_db, init_db
from database.models import User

def test_database():
    """Test database connection and user creation"""
    print("🧪 Testing Database Connection")
    print("=" * 40)
    
    try:
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Test creating a user
        db = next(get_db())
        try:
            # Check if demo_user exists
            user = db.query(User).filter(User.id == "demo_user").first()
            
            if not user:
                print("Creating demo user...")
                user = User(
                    id="demo_user",
                    username="demo_user",
                    email="demo@example.com",
                    hashed_password="demo_password",
                    first_name="Demo",
                    last_name="User"
                )
                db.add(user)
                db.commit()
                print("✅ Demo user created")
            else:
                print(f"✅ Demo user exists: {user.username}")
                print(f"   Phone: {user.phone_number}")
                print(f"   Email: {user.email}")
            
            # Test updating phone number
            user.phone_number = "1234567890"
            db.commit()
            print("✅ Phone number updated to: 1234567890")
            
            # Verify the update
            updated_user = db.query(User).filter(User.id == "demo_user").first()
            print(f"✅ Verified phone number: {updated_user.phone_number}")
            
        finally:
            db.close()
            
        print("✅ Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()
