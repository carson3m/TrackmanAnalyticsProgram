import os

# app/config.py
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trackman_analytics.db")
