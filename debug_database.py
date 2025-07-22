#!/usr/bin/env python3
"""
Debug database connection and verify which database is being used
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.config import DATABASE_URL

def debug_database():
    """Debug database connection and users"""
    
    print("🔍 Debugging database connection...")
    print(f"📋 DATABASE_URL from config: {DATABASE_URL}")
    
    # Test the configured database URL
    try:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("✅ Database connection successful!")
        
        # Check if users table exists
        try:
            users = db.query(User).all()
            print(f"📊 Found {len(users)} users in database:")
            
            for user in users:
                print(f"   - {user.username} ({user.role})")
                
                # Test password verification for simpleadmin
                if user.username == "simpleadmin":
                    if user.verify_password("password"):
                        print(f"      ✅ Password 'password' works for {user.username}")
                    else:
                        print(f"      ❌ Password 'password' does NOT work for {user.username}")
                        print(f"      🔍 Hash: {user.hashed_password}")
                        
                        # Test what password actually works
                        test_passwords = ["password", "admin123", "admin", "123456", "simpleadmin"]
                        for test_pwd in test_passwords:
                            if user.verify_password(test_pwd):
                                print(f"      ✅ Password '{test_pwd}' works for {user.username}")
                                break
                
        except Exception as e:
            print(f"❌ Error querying users: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Also test with absolute path
    print("\n🔍 Testing with absolute path...")
    current_dir = os.getcwd()
    absolute_db_path = f"sqlite:///{current_dir}/trackman_analytics.db"
    print(f"📋 Absolute path: {absolute_db_path}")
    
    try:
        engine = create_engine(absolute_db_path, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        users = db.query(User).all()
        print(f"📊 Found {len(users)} users with absolute path:")
        
        for user in users:
            print(f"   - {user.username} ({user.role})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Absolute path connection failed: {e}")

if __name__ == "__main__":
    debug_database() 