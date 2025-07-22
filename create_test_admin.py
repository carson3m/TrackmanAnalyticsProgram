#!/usr/bin/env python3
"""
Create a test admin user with a very simple password
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Use the correct database
DATABASE_URL = "sqlite:///./trackman_analytics.db"

def create_test_admin():
    """Create a test admin user with password 'test'"""
    
    print("🔧 Creating test admin user...")
    
    # Create engine for database
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if test admin already exists
        test_admin = db.query(User).filter(User.username == "test").first()
        
        if test_admin:
            print("✅ Test admin user already exists")
            # Update password to make sure it's correct
            test_admin.hashed_password = User.hash_password("test")
            db.commit()
            print("✅ Password updated to 'test'")
        else:
            print("👑 Creating test admin user...")
            test_admin = User(
                username="test",
                hashed_password=User.hash_password("test"),
                role="admin"
            )
            db.add(test_admin)
            db.commit()
            print("✅ Test admin user created successfully!")
        
        # Verify the password works
        if test_admin.verify_password("test"):
            print("✅ Password verification successful!")
        else:
            print("❌ Password verification failed!")
        
        print("\n🎉 Test admin credentials:")
        print("   Username: test")
        print("   Password: test")
        print("   Role: admin")
        
        # Also create a backup admin with a different password
        backup_admin = db.query(User).filter(User.username == "backup").first()
        
        if backup_admin:
            print("✅ Backup admin user already exists")
            backup_admin.hashed_password = User.hash_password("backup")
            db.commit()
            print("✅ Backup password updated to 'backup'")
        else:
            print("👑 Creating backup admin user...")
            backup_admin = User(
                username="backup",
                hashed_password=User.hash_password("backup"),
                role="admin"
            )
            db.add(backup_admin)
            db.commit()
            print("✅ Backup admin user created successfully!")
        
        # List all admin users
        print("\n📊 All admin users in database:")
        admin_users = db.query(User).filter(User.role == "admin").all()
        for user in admin_users:
            print(f"   - {user.username} ({user.role})")
        
        print("\n💡 Try these logins:")
        print("   1. test / test")
        print("   2. backup / backup")
        print("   3. simpleadmin / password")
        print("   4. admin / admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_test_admin() 