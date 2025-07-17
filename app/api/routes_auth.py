# # app/api/routes_auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User
from app.core.security import create_access_token, authenticate_user, get_current_user, require_admin
from app.schemas import UserLogin, Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/init-db")
def initialize_database(db: Session = Depends(get_db)):
    """Initialize database with default users"""
    try:
        # Check if test user exists
        test_user = db.query(User).filter(User.username == "Carson").first()
        if not test_user:
            test_user = User(
                username="Carson",
                hashed_password=User.hash_password("192837465"),
                role="admin"
            )
            db.add(test_user)
            print("✅ Test user created")
        else:
            print("✅ Test user already exists")
            
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                hashed_password=User.hash_password("admin123"),
                role="admin"
            )
            db.add(admin_user)
            print("✅ Admin user created")
        else:
            print("✅ Admin user already exists")
            
        db.commit()
        return {"message": "Database initialized successfully", "users_created": True}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing database: {str(e)}"
        )

@router.post("/create-coach")
def create_coach_user(
    username: str,
    password: str,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new coach user (Admin only)"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
            
        # Create new coach user
        coach_user = User(
            username=username,
            hashed_password=User.hash_password(password),
            role="coach"
        )
        db.add(coach_user)
        db.commit()
        
        return {
            "message": "Coach user created successfully",
            "username": username,
            "role": "coach"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating coach user: {str(e)}"
        )
