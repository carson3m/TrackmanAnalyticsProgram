import os

# app/config.py
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://CarsonMorton:rehPij-7sadtu-nakgyb@awseb-e-emuy3q37ap-stack-awsebrdsdatabase-ok9z1grbxecn.c7c6uu2mwdha.us-west-2.rds.amazonaws.com:5432/ebdb")

print("DATABASE_URL in use:", DATABASE_URL)
