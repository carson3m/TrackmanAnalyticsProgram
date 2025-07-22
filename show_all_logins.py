#!/usr/bin/env python3
"""
Show all user login credentials from the database
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Use the database that the backend is currently using
DATABASE_URL = "sqlite:///./app.db"

def show_all_logins():
    """Show all user login credentials"""
    
    print("🔍 Checking all user login credentials...")
    
    # Create engine for database
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        if not users:
            print("❌ No users found in database")
            return
        
        print(f"\n📊 Found {len(users)} users in the system:")
        print("=" * 50)
        
        for user in users:
            print(f"👤 Username: {user.username}")
            print(f"   Role: {user.role}")
            
            # Test common passwords to find the actual password
            test_passwords = [
                "admin123", "admin", "password", "123456",
                "Potterup123", "coach123", "user123",
                "Carson", "Nate", "Kujawski"
            ]
            
            found_password = None
            for test_pwd in test_passwords:
                if user.verify_password(test_pwd):
                    found_password = test_pwd
                    break
            
            if found_password:
                print(f"   Password: {found_password}")
            else:
                print(f"   Password: Unknown (hash: {user.hashed_password[:20]}...)")
            
            print("-" * 30)
        
        print("\n💡 Login Instructions:")
        print("1. Go to https://moundvision.com")
        print("2. Use any of the credentials above")
        print("3. Admin users can access the Admin Panel")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    show_all_logins() 