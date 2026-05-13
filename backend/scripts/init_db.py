#!/usr/bin/env python
"""
Database initialization script
"""

import sys
from models.database import init_db, engine
from models.models import Base

if __name__ == "__main__":
    try:
        print("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)
