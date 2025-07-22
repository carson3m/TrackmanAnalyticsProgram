#!/usr/bin/env python3
"""
Database management script for MoundVision Analytics
Provides utilities for backup, restore, and user management.
"""

import os
import sys
import shutil
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models.user import User
from app.config import DATABASE_URL

def backup_database():
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"trackman_analytics_backup_{timestamp}.db"
    
    if os.path.exists("trackman_analytics.db"):
        shutil.copy2("trackman_analytics.db", backup_file)
        print(f"✅ Database backed up to: {backup_file}")
    else:
        print("❌ Database file not found. Run init_database.py first.")

def restore_database(backup_file):
    """Restore database from backup"""
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return
    
    shutil.copy2(backup_file, "trackman_analytics.db")
    print(f"✅ Database restored from: {backup_file}")

def list_backups():
    """List available backup files"""
    backups = [f for f in os.listdir(".") if f.startswith("trackman_analytics_backup_") and f.endswith(".db")]
    
    if not backups:
        print("No backup files found.")
        return
    
    print("Available backups:")
    for backup in sorted(backups, reverse=True):
        size = os.path.getsize(backup)
        print(f"  - {backup} ({size} bytes)")

def list_users():
    """List all users in the database"""
    if not os.path.exists("trackman_analytics.db"):
        print("❌ Database not found. Run init_database.py first.")
        return
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        print(f"📊 Found {len(users)} users:")
        for user in users:
            print(f"  - {user.username} ({user.role})")
    except Exception as e:
        print(f"❌ Error reading users: {e}")
    finally:
        db.close()

def add_user(username, password, role):
    """Add a new user to the database"""
    if not os.path.exists("trackman_analytics.db"):
        print("❌ Database not found. Run init_database.py first.")
        return
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists.")
            return
        
        # Validate role
        valid_roles = ["admin", "coach", "user"]
        if role not in valid_roles:
            print(f"❌ Invalid role. Must be one of: {', '.join(valid_roles)}")
            return
        
        # Create user
        new_user = User(
            username=username,
            hashed_password=User.hash_password(password),
            role=role
        )
        db.add(new_user)
        db.commit()
        print(f"✅ User '{username}' created with role '{role}'")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

def show_help():
    """Show help information"""
    print("""
MoundVision Analytics Database Management

Usage: python3 manage_db.py <command> [options]

Commands:
  backup              Create a backup of the database
  restore <file>      Restore database from backup file
  list-backups        List available backup files
  list-users          List all users in the database
  add-user <user> <pass> <role>  Add a new user
  help                Show this help message

Examples:
  python3 manage_db.py backup
  python3 manage_db.py restore trackman_analytics_backup_20250101_120000.db
  python3 manage_db.py list-users
  python3 manage_db.py add-user john password123 coach
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        backup_database()
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Please specify backup file to restore from.")
            return
        restore_database(sys.argv[2])
    elif command == "list-backups":
        list_backups()
    elif command == "list-users":
        list_users()
    elif command == "add-user":
        if len(sys.argv) < 5:
            print("❌ Please specify username, password, and role.")
            return
        add_user(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main() 