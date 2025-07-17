from pydantic import BaseModel

# Request body for login
class UserLogin(BaseModel):
    username: str
    password: str

# Response for JWT token
class Token(BaseModel):
    access_token: str
    token_type: str
