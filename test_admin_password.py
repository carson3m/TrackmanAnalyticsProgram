#!/usr/bin/env python3
"""
Test different passwords for the admin user
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Use the database that the backend is currently using
DATABASE_URL = "sqlite:///./app.db"

def test_admin_password():
    """Test different passwords for admin user"""
    
    print("🔍 Testing passwords for admin user...")
    
    # Create engine for database
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("❌ Admin user not found")
            return
        
        print(f"👤 Testing passwords for user: {admin_user.username}")
        print(f"   Current hash: {admin_user.hashed_password}")
        
        # Test various passwords
        test_passwords = [
            "admin123", "admin", "password", "123456", "admin123!",
            "Admin123", "ADMIN123", "admin1234", "admin12",
            "trackman", "analytics", "baseball", "pitcher",
            "coach", "user", "test", "demo"
        ]
        
        print("\n🔑 Testing passwords:")
        print("-" * 30)
        
        for password in test_passwords:
            if admin_user.verify_password(password):
                print(f"✅ MATCH FOUND: '{password}'")
                print(f"   Username: admin")
                print(f"   Password: {password}")
                print(f"   Role: {admin_user.role}")
                return
            else:
                print(f"❌ '{password}' - No match")
        
        print("\n❌ No matching password found in test list")
        print("💡 The password might be something else or the hash is corrupted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_password() 