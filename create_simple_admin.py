#!/usr/bin/env python3
"""
Create a simple admin user with a basic password
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Use the database that the backend is currently using
DATABASE_URL = "sqlite:///./app.db"

def create_simple_admin():
    """Create a simple admin user with password 'password'"""
    
    print("🔧 Creating simple admin user...")
    
    # Create engine for database
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if simple admin already exists
        simple_admin = db.query(User).filter(User.username == "simpleadmin").first()
        
        if simple_admin:
            print("✅ Simple admin user already exists")
            # Update password to make sure it's correct
            simple_admin.hashed_password = User.hash_password("password")
            db.commit()
            print("✅ Password updated to 'password'")
        else:
            print("👑 Creating simple admin user...")
            simple_admin = User(
                username="simpleadmin",
                hashed_password=User.hash_password("password"),
                role="admin"
            )
            db.add(simple_admin)
            db.commit()
            print("✅ Simple admin user created successfully!")
        
        # Verify the password works
        if simple_admin.verify_password("password"):
            print("✅ Password verification successful!")
        else:
            print("❌ Password verification failed!")
        
        print("\n🎉 Simple admin credentials:")
        print("   Username: simpleadmin")
        print("   Password: password")
        print("   Role: admin")
        
        # List all admin users
        print("\n📊 All admin users in database:")
        admin_users = db.query(User).filter(User.role == "admin").all()
        for user in admin_users:
            print(f"   - {user.username} ({user.role})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_simple_admin() 