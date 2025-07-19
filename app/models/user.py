from sqlalchemy import Column, Integer, String
from app.models.database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    def verify_password(self, password: str) -> bool:
        # Ensure self.hashed_password is a string, not a column object
        hashed = self.hashed_password if isinstance(self.hashed_password, str) else str(self.hashed_password)
        return pwd_context.verify(password, hashed)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)
