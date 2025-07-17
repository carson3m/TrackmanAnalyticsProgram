#!/usr/bin/env python3
"""
Database initialization script for Trackman Analytics API
"""
from app.models.database import engine, SessionLocal
from app.models.user import User, Base
from app.models.user import User, Base

def init_db():
    """Initialize the database with tables and default user"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Creating default admin user...")
            admin_user = User(
                username="admin",
                hashed_password=User.hash_password("admin123"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Role: admin")
        else:
            print("✅ Admin user already exists")
            
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
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 