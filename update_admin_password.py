#!/usr/bin/env python3
"""
Update admin password in the old database
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Use the old database that the backend is currently using
OLD_DATABASE_URL = "sqlite:///./app.db"

def update_admin_password():
    """Update admin password in the old database"""
    
    print("🔧 Updating admin password in old database...")
    
    # Create engine for old database
    engine = create_engine(OLD_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("❌ Admin user not found in old database")
            return
        
        # Update password
        admin_user.hashed_password = User.hash_password("admin123")
        db.commit()
        
        print("✅ Admin password updated successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role: admin")
        
        # Verify the update
        print("\n🔍 Verifying password update...")
        if admin_user.verify_password("admin123"):
            print("✅ Password verification successful!")
        else:
            print("❌ Password verification failed!")
        
        print("\n🎉 Admin login should now work!")
        print("💡 Try logging in with: admin / admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_password() 