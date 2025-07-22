from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User
from sqlalchemy import text

router = APIRouter()

@router.get("/debug/db-test")
def test_database_connection(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Test basic connection
        result = db.execute(text("SELECT 1 as test"))
        test_result = result.fetchone()
        
        # Check if users table exists and has data
        user_count = db.query(User).count()
        
        return {
            "status": "success",
            "database_connected": True,
            "test_query_result": test_result[0] if test_result else None,
            "user_count": user_count,
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "database_connected": False,
            "error": str(e),
            "message": "Database connection failed"
        }

@router.post("/debug/init-users")
def initialize_users(db: Session = Depends(get_db)):
    """Initialize admin and test users"""
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            return {
                "status": "success",
                "message": "Admin user already exists",
                "admin_exists": True
            }
        
        # Create admin user
        admin_user = User(
            username="admin",
            hashed_password=User.hash_password("admin123"),
            role="admin"
        )
        
        db.add(admin_user)
        
        # Create test user
        test_user = User(
            username="test",
            hashed_password=User.hash_password("test123"),
            role="user"
        )
        
        db.add(test_user)
        db.commit()
        
        return {
            "status": "success",
            "message": "Users created successfully",
            "admin_created": True,
            "test_created": True,
            "admin_credentials": {
                "username": "admin",
                "password": "admin123",
                "role": "admin"
            },
            "test_credentials": {
                "username": "test", 
                "password": "test123",
                "role": "user"
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to create users"
        }

@router.get("/debug/users")
def list_users(db: Session = Depends(get_db)):
    """List all users in the database"""
    try:
        users = db.query(User).all()
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "hashed_password": user.hashed_password[:20] + "..." if user.hashed_password else None
            })
        
        return {
            "status": "success",
            "user_count": len(user_list),
            "users": user_list
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to list users"
        } 