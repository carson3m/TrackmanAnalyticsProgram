# # app/api/routes_auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.database import get_db, Team
from app.models.user import User
from app.core.security import create_access_token, authenticate_user, get_current_user, require_admin
from app.schemas import UserLogin, Token
from pydantic import BaseModel

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
            "team_id": user.team_id
        }
    )
    # Get team information if user has a team
    team_name = None
    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        team_name = team.name if team else None
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "team_id": user.team_id,
            "team_name": team_name
        }
    }

@router.post("/init-db")
def initialize_database(db: Session = Depends(get_db)):
    """Initialize database with default users"""
    try:
        # Remove any existing test user with this email
        existing = db.query(User).filter(User.email == "cmorton@moundvision.com").first()
        if existing:
            db.delete(existing)
            db.commit()
        # Now create the test user
        test_user = User(
            name="Carson",
            email="cmorton@moundvision.com",
            password_hash=User.hash_password("192837465"),
            role="admin"
        )
        db.add(test_user)
        print("✅ Test user created (reset)")
            
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin",
                email="admin@example.com",
                password_hash=User.hash_password("admin123"),
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
    email: str,
    name: str,
    password: str,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new coach user (Admin only)"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
            
        # Create new coach user
        coach_user = User(
            name=name,
            email=email,
            password_hash=User.hash_password(password),
            role="coach"
        )
        db.add(coach_user)
        db.commit()
        
        return {
            "message": "Coach user created successfully",
            "email": email,
            "role": "coach"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating coach user: {str(e)}"
        )

class SetPasswordRequest(BaseModel):
    email: str
    password: str

@router.post("/debug/set-password")
def set_password(req: SetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        return {"status": "error", "message": "User not found"}
    user.password_hash = User.hash_password(req.password)
    db.commit()
    return {"status": "success", "message": f"Password updated for {req.email}"}

@router.get("/debug/list-users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role, "team_id": u.team_id} for u in users]

@router.get("/debug/list-teams")
def list_teams(db: Session = Depends(get_db)):
    """Debug endpoint to list all teams"""
    teams = db.query(Team).all()
    return [{"id": t.id, "name": t.name, "organization": t.organization} for t in teams]

@router.post("/debug/create-test-teams")
def create_test_teams(db: Session = Depends(get_db)):
    """Debug endpoint to create test teams"""
    try:
        # Create test teams if they don't exist
        team_names = ["Test Team 1", "Test Team 2", "Demo Team"]
        created_teams = []
        
        for team_name in team_names:
            existing_team = db.query(Team).filter(Team.name == team_name).first()
            if not existing_team:
                new_team = Team(name=team_name, organization="Test Organization")
                db.add(new_team)
                created_teams.append(team_name)
        
        db.commit()
        return {"message": f"Created teams: {created_teams}", "teams_created": len(created_teams)}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating test teams: {str(e)}"
        )
