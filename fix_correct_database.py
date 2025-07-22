#!/usr/bin/env python3
"""
Add simple admin user to the correct database (trackman_analytics.db)
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Use the correct database that the backend is actually using
CORRECT_DATABASE_URL = "sqlite:///./trackman_analytics.db"

def fix_correct_database():
    """Add simple admin user to the correct database"""
    
    print("🔧 Adding simple admin to the correct database...")
    
    # Create engine for correct database
    engine = create_engine(CORRECT_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if simple admin already exists
        simple_admin = db.query(User).filter(User.username == "simpleadmin").first()
        
        if simple_admin:
            print("✅ Simple admin user already exists in correct database")
            # Update password to make sure it's correct
            simple_admin.hashed_password = User.hash_password("password")
            db.commit()
            print("✅ Password updated to 'password'")
        else:
            print("👑 Creating simple admin user in correct database...")
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
        
        # List all users in correct database
        print("\n📊 All users in correct database:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.username} ({user.role})")
        
        # Also update the admin user password to admin123
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            admin_user.hashed_password = User.hash_password("admin123")
            db.commit()
            print("\n✅ Updated admin user password to 'admin123'")
        
        print("\n💡 Try these logins:")
        print("   1. simpleadmin / password")
        print("   2. admin / admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    fix_correct_database() 