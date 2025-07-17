#!/usr/bin/env python3
"""
Script to add a coach user to the database
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.database import SessionLocal
from app.models.user import User

def add_coach():
    """Add a coach user to the database"""
    db = SessionLocal()
    try:
        # Check if coach user exists
        coach = db.query(User).filter(User.username == "Nate Kujawski").first()
        if not coach:
            print("Creating coach user...")
            coach = User(
                username="Nate Kujawski",
                hashed_password=User.hash_password("Potterup123"),
                role="coach"
            )
            db.add(coach)
            db.commit()
            print("✅ Coach user created:")
            print("   Username: Nate Kujawski")
            print("   Password: Potterup123")
            print("   Role: coach")
        else:
            print("✅ Coach user already exists")
            
    except Exception as e:
        print(f"❌ Error adding coach user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_coach() 