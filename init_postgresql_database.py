#!/usr/bin/env python3
"""
Initialize PostgreSQL database for MoundVision Analytics
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.models.database import Base
from app.models.user import User
from sqlalchemy.orm import sessionmaker

# Set the database URL
DATABASE_URL = "postgresql+psycopg2://admin:qyxry7-hivsyk-bySbej@moundvision-prod.cs7akq4aih2z.us-east-1.rds.amazonaws.com:5432/trackman"

def init_database():
    """Initialize the PostgreSQL database"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✅ Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            hashed_password=User.hash_password("admin123"),
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role: admin")
        
        # Create a test user
        test_user = User(
            username="test",
            hashed_password=User.hash_password("test123"),
            role="user"
        )
        
        db.add(test_user)
        db.commit()
        print("✅ Test user created successfully!")
        print("   Username: test")
        print("   Password: test123")
        print("   Role: user")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Initializing PostgreSQL database...")
    init_database()
    print("🎉 Database initialization complete!") 