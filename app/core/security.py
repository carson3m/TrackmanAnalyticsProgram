from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.database import get_db
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(f"DEBUG: Token received: {token}")
    print(f"DEBUG: SECRET_KEY: {SECRET_KEY}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        print(f"DEBUG: Decoded email: {email}")
        if email is None:
            print("DEBUG: Email is None")
            raise credentials_exception
    except JWTError as e:
        print(f"DEBUG: JWT decode error: {e}")
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    print(f"DEBUG: User found: {user}")
    if user is None:
        print("DEBUG: User not found in database")
        raise credentials_exception
    return user

def require_role(required_role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if getattr(user, 'role', None) != required_role:
            raise HTTPException(status_code=403, detail="Not authorized")
        return user
    return role_checker

def require_any_role(allowed_roles: list[str]):
    def role_checker(user: User = Depends(get_current_user)):
        if getattr(user, 'role', None) not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker

# Common role combinations
require_admin = require_role("admin")
require_coach_or_admin = require_any_role(["coach", "admin"])
require_authenticated = get_current_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.verify_password(password):
        return None
    return user
