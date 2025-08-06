from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import sessionmaker, relationship
from app.models.base import Base
from app.models.player import Player
from app.config import DATABASE_URL
from datetime import datetime

# Create engine with appropriate settings for SQLite or PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific settings
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL settings (no special connect_args needed)
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    organization = Column(String)

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    date = Column(String)  # Use Date if you want strict typing
    opponent = Column(String)
    team_id = Column(Integer, ForeignKey('teams.id'))
    result = Column(String)  # 'W'/'L' or score
    team = relationship('Team')

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(String)  # Use DateTime if you want strict typing
    game = relationship('Game')
    uploader = relationship('User')

class BattingStats(Base):
    __tablename__ = 'batting_stats'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    AB = Column(Integer)
    H = Column(Integer)
    HR = Column(Integer)
    RBI = Column(Integer)
    BB = Column(Integer)
    K = Column(Integer)
    PA = Column(Integer)
    AVG = Column(String)  # Use Float if you want strict typing
    OBP = Column(String)
    SLG = Column(String)
    OPS = Column(String)
    player = relationship('Player')
    game = relationship('Game')

class GameData(Base):
    __tablename__ = 'game_data'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    player_id = Column(Integer, ForeignKey('players.id'), nullable=True)  # Pitcher or batter
    row_type = Column(String)  # 'pitching' or 'batting' or other
    # Common fields from CSVs (add/adjust as needed)
    inning = Column(String)
    pitcher = Column(String)
    batter = Column(String)
    pitch_type = Column(String)
    result = Column(String)
    pitch_speed = Column(String)
    exit_velocity = Column(String)
    play_result = Column(String)
    # Add more columns as needed for your CSV structure
    team = relationship('Team')
    game = relationship('Game')
    player = relationship('Player')

class CSVFile(Base):
    __tablename__ = 'csv_files'
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)  # Size in bytes
    row_count = Column(Integer)  # Number of rows in the CSV
    game_date = Column(String)  # Extracted from filename or user input
    opponent = Column(String)  # User input
    game_result = Column(String)  # W/L or score
    notes = Column(Text)  # Optional notes about the game
    is_processed = Column(Integer, default=0)  # 0 = not processed, 1 = processed
    
    # Relationships
    team = relationship('Team')
    uploader = relationship('User')

class CSVData(Base):
    __tablename__ = 'csv_data'
    id = Column(Integer, primary_key=True)
    csv_file_id = Column(Integer, ForeignKey('csv_files.id'), nullable=False)
    row_number = Column(Integer, nullable=False)  # Row number in the original CSV
    data_json = Column(Text, nullable=False)  # Store row data as JSON
    
    # Relationship
    csv_file = relationship('CSVFile')

class TeamMetricTargets(Base):
    __tablename__ = 'team_metric_targets'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    metric_name = Column(String, nullable=False)  # e.g., 'chase_rate', 'strike_percentage'
    target_value = Column(Integer, nullable=False)  # Target value as integer (multiply by 10 for decimals)
    priority = Column(String, default='Medium')  # High, Medium, Low
    description = Column(Text)  # Description of the metric and target
    lower_is_better = Column(Integer, default=0)  # 0 = higher is better, 1 = lower is better
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    team = relationship('Team')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
