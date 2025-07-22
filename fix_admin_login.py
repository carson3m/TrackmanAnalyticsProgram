#!/usr/bin/env python3
"""
Fix admin login by adding admin user to the old database
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Use the old database that the backend is currently using
OLD_DATABASE_URL = "sqlite:///./app.db"

def fix_admin_login():
    """Add admin user to the old database"""
    
    print("🔧 Fixing admin login in old database...")
    
    # Create engine for old database
    engine = create_engine(OLD_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if admin_user:
            print("✅ Admin user already exists in old database")
            print(f"   Username: {admin_user.username}")
            print(f"   Role: {admin_user.role}")
        else:
            print("👑 Creating admin user in old database...")
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
        
        # List all users in old database
        print("\n📊 Current users in old database:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.username} ({user.role})")
        
        print("\n🎉 Admin login should now work!")
        print("💡 Try logging in with: admin / admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_login() 