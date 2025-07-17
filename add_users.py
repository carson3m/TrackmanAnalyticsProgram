#!/usr/bin/env python3
"""
Script to add users to the deployed database
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.database import SessionLocal
from app.models.user import User

def add_users():
    """Add users to the database"""
    db = SessionLocal()
    try:
        # Check if test user exists
        test_user = db.query(User).filter(User.username == "Carson").first()
        if not test_user:
            print("Creating test user...")
            test_user = User(
                username="Carson",
                hashed_password=User.hash_password("192837465"),
                role="admin"
            )
            db.add(test_user)
            db.commit()
            print("✅ Test user created:")
            print("   Username: Carson")
            print("   Password: 192837465")
            print("   Role: admin")
        else:
            print("✅ Test user already exists")
            
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Creating admin user...")
            admin_user = User(
                username="admin",
                hashed_password=User.hash_password("admin123"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Role: admin")
        else:
            print("✅ Admin user already exists")
            
    except Exception as e:
        print(f"❌ Error adding users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_users() 