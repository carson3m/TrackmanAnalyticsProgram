from pydantic import BaseModel

# Request body for login
class UserLogin(BaseModel):
    email: str
    password: str

# User information
class UserInfo(BaseModel):
    id: int
    name: str
    email: str
    role: str
    team_id: int | None = None
    team_name: str | None = None

# Response for JWT token
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo
