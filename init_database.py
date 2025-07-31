#!/usr/bin/env python3
"""
Database initialization script for MindFlora
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(__file__))

from database.connection import init_db, reset_db
from database.models import Base

def main():
    """Initialize the database"""
    print("🔧 Initializing MindFlora Database...")
    
    try:
        # Initialize database tables
        init_db()
        print("✅ Database initialized successfully!")
        print("📁 Database file: mindflora.db")
        print("🗂️  Tables created:")
        
        # List all tables
        for table in Base.metadata.tables:
            print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 