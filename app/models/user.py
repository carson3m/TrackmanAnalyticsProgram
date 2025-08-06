from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default='coach')  # 'admin', 'coach', 'player'
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    team = relationship('Team')

    def verify_password(self, password: str) -> bool:
        # Ensure self.hashed_password is a string, not a column object
        hashed = self.password_hash if isinstance(self.password_hash, str) else str(self.password_hash)
        return pwd_context.verify(password, hashed)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)
