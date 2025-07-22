#!/usr/bin/env python3
"""
Database initialization script for MoundVision Analytics
This script sets up the database with persistent storage and creates initial users.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models.user import User
from app.config import DATABASE_URL

def init_database():
    """Initialize the database with tables and initial data"""
    
    print("🔧 Initializing MoundVision Analytics Database...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("👑 Creating initial admin user...")
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
            print("   ⚠️  Please change the password after first login!")
        else:
            print("✅ Admin user already exists")
        
        # Check if demo coach user exists
        coach_user = db.query(User).filter(User.username == "coach").first()
        
        if not coach_user:
            print("🏃 Creating demo coach user...")
            coach_user = User(
                username="coach",
                hashed_password=User.hash_password("coach123"),
                role="coach"
            )
            db.add(coach_user)
            db.commit()
            print("✅ Coach user created successfully!")
            print("   Username: coach")
            print("   Password: coach123")
        else:
            print("✅ Coach user already exists")
        
        # Check if demo regular user exists
        demo_user = db.query(User).filter(User.username == "user").first()
        
        if not demo_user:
            print("👤 Creating demo regular user...")
            demo_user = User(
                username="user",
                hashed_password=User.hash_password("user123"),
                role="user"
            )
            db.add(demo_user)
            db.commit()
            print("✅ Regular user created successfully!")
            print("   Username: user")
            print("   Password: user123")
        else:
            print("✅ Regular user already exists")
        
        # Display all users
        print("\n📊 Current users in database:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.username} ({user.role})")
        
        print("\n🎉 Database initialization completed successfully!")
        print("💡 You can now start the application and log in with any of the above users.")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 