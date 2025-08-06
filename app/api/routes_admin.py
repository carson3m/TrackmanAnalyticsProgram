from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.database import get_db, Team
from app.core.security import require_admin
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    team_id: Optional[int] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    team_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    team_id: Optional[int] = None
    team_name: Optional[str] = None

class TeamCreate(BaseModel):
    name: str
    organization: Optional[str] = None

class TeamResponse(BaseModel):
    id: int
    name: str
    organization: Optional[str] = None
    user_count: int

    class Config:
        from_attributes = True

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only)
    """
    users = db.query(User).all()
    user_responses = []
    
    for user in users:
        team_name = None
        if user.team_id:
            team = db.query(Team).filter(Team.id == user.team_id).first()
            team_name = team.name if team else None
        
        user_responses.append(UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            team_id=user.team_id,
            team_name=team_name
        ))
    
    return user_responses

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new user (admin only)
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Validate role
    valid_roles = ["admin", "coach", "user"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Validate team_id if provided
    if user_data.team_id is not None:
        team = db.query(Team).filter(Team.id == user_data.team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid team_id"
            )
    
    # Create new user
    hashed_password = User.hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        team_id=user_data.team_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    team_name = None
    if new_user.team_id:
        team = db.query(Team).filter(Team.id == new_user.team_id).first()
        team_name = team.name if team else None
    
    return UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        team_id=new_user.team_id,
        team_name=team_name
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if trying to update to existing username
    if user_data.email and user_data.email != user.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
    # Validate role if provided
    if user_data.role:
        valid_roles = ["admin", "coach", "user"]
        if user_data.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
    
    # Validate team_id if provided
    if user_data.team_id is not None:
        team = db.query(Team).filter(Team.id == user_data.team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid team_id"
            )
    
    # Update user fields
    if user_data.name:
        user.name = user_data.name
    if user_data.email:
        user.email = user_data.email
    if user_data.password:
        user.password_hash = User.hash_password(user_data.password)
    if user_data.role:
        user.role = user_data.role
    if hasattr(user_data, 'team_id'):
        user.team_id = user_data.team_id
    
    db.commit()
    db.refresh(user)
    
    team_name = None
    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        team_name = team.name if team else None
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        team_id=user.team_id,
        team_name=team_name
    )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get admin dashboard statistics
    """
    total_users = db.query(User).count()
    admin_users = db.query(User).filter(User.role == "admin").count()
    coach_users = db.query(User).filter(User.role == "coach").count()
    regular_users = db.query(User).filter(User.role == "user").count()
    
    return {
        "total_users": total_users,
        "admin_users": admin_users,
        "coach_users": coach_users,
        "regular_users": regular_users
    } 

@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all teams (admin only)
    """
    teams = db.query(Team).all()
    team_responses = []
    
    for team in teams:
        user_count = db.query(User).filter(User.team_id == team.id).count()
        team_responses.append(TeamResponse(
            id=team.id,
            name=team.name,
            organization=team.organization,
            user_count=user_count
        ))
    
    return team_responses

@router.post("/teams", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new team (admin only)
    """
    # Check if team name already exists
    existing_team = db.query(Team).filter(Team.name == team_data.name).first()
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team name already exists"
        )
    
    # Create new team
    new_team = Team(
        name=team_data.name,
        organization=team_data.organization
    )
    
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    return TeamResponse(
        id=new_team.id,
        name=new_team.name,
        organization=new_team.organization,
        user_count=0
    )

@router.put("/users/{user_id}/assign-team")
async def assign_user_to_team(
    user_id: int,
    team_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Assign a user to a team (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if team_id is not None:
        # Verify team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        user.team_id = team_id
    else:
        # Remove user from team
        user.team_id = None
    
    db.commit()
    db.refresh(user)
    
    team_name = None
    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        team_name = team.name if team else None
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        team_id=user.team_id,
        team_name=team_name
    ) 