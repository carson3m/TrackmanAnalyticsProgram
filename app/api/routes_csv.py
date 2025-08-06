from fastapi import APIRouter, UploadFile, File, HTTPException, Security, Depends, Form
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.models.database import get_db, GameData, Game, CSVFile, CSVData, Team, TeamMetricTargets
from app.core.security import get_current_user, require_coach_or_admin, require_admin
import pandas as pd
import os
import json
import io
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from urllib.parse import unquote

router = APIRouter()

# OAuth2 scheme for explicit Swagger token inclusion
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Temp file storage (keeping for backward compatibility)
TEMP_CSV_PATH = "temp_uploaded.csv"
uploaded_df = None  # In-memory store for CSV data

# Team name mapping for CSV data
TEAM_NAME_MAPPING = {
    "Lincoln Potters": ["LIN_POT", "Lincoln Potters", "Potters", "LIN"],
    "Potters": ["LIN_POT", "Lincoln Potters", "Potters", "LIN"],  # Add mapping for "Potters" team name
    "Medford Rogues": ["MED_ROG", "Medford Rogues", "Rogues", "MED"],
    "Healdsburg Prune Packers": ["HEA_PRU", "Healdsburg Prune Packers", "Prune Packers", "HEA", "PRU"],
    "McBean": ["McBean", "MCBEAN", "MC_BEAN"],
    # Add more team mappings as needed
}

def get_team_variations(team_name):
    """
    Get all possible variations of a team name for matching in CSV data.
    """
    if team_name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[team_name]
    else:
        # If no mapping exists, return the original name and common variations
        return [team_name, team_name.upper(), team_name.replace(" ", "_"), team_name.replace(" ", "")]

def get_player_name_variations(player_name):
    """Get all possible variations of a player name for deduplication"""
    if not player_name:
        return []
    
    variations = [player_name]
    
    # Common name variations mapping
    name_variations = {
        'john': ['johnny', 'jon', 'jonny'],
        'johnny': ['john', 'jon', 'jonny'],
        'jon': ['john', 'johnny', 'jonny'],
        'jonny': ['john', 'johnny', 'jon'],
        'josh': ['joshua'],
        'joshua': ['josh'],
        'ken': ['kenan', 'kenneth'],
        'kenan': ['ken', 'kenneth'],
        'kenneth': ['ken', 'kenan'],
        'connor': ['conner'],
        'conner': ['connor'],
        'tanner': ['tanar'],
        'tanar': ['tanner'],
        'evan': ['even'],
        'even': ['evan'],
        'dawson': ['dawsonl'],
        'dawsonl': ['dawson'],
        'williams': ['william'],
        'william': ['williams']
    }
    
    # Split name into parts and generate variations
    name_parts = player_name.lower().split()
    for i, part in enumerate(name_parts):
        if part in name_variations:
            for variation in name_variations[part]:
                new_parts = name_parts.copy()
                new_parts[i] = variation
                variations.append(' '.join(new_parts))
    
    # Also add capitalized versions
    capitalized_variations = []
    for variation in variations:
        # Handle "Last, First" format
        if ',' in variation:
            parts = variation.split(',')
            if len(parts) == 2:
                last = parts[0].strip().title()
                first = parts[1].strip().title()
                capitalized_variations.append(f"{last}, {first}")
        else:
            # Handle "First Last" format
            capitalized_variations.append(variation.title())
    
    variations.extend(capitalized_variations)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for variation in variations:
        if variation not in seen:
            seen.add(variation)
            unique_variations.append(variation)
    
    return unique_variations

# Pydantic models for CSV management
class CSVFileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    team_id: int
    uploaded_by: int
    uploaded_at: datetime
    file_size: int
    row_count: int
    game_date: Optional[str] = None
    opponent: Optional[str] = None
    game_result: Optional[str] = None
    notes: Optional[str] = None
    is_processed: int
    uploader_name: str
    team_name: str

    class Config:
        from_attributes = True

class CSVUploadRequest(BaseModel):
    game_date: Optional[str] = None
    opponent: Optional[str] = None
    game_result: Optional[str] = None
    notes: Optional[str] = None

@router.post(
    "/upload",
    summary="Upload CSV (Coach/Admin only)",
    description="Upload a CSV file to process Trackman data. Coach or Admin role required."
)
async def upload_csv(
    file: UploadFile = File(...),
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV file, parse it, and store each row in the GameData table for the user's team.
    """
    if not (hasattr(file, "filename") and str(file.filename).lower().endswith(".csv")):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    # Create a new Game entry for this upload (could be improved to match existing games)
    new_game = Game(date="unknown", opponent="unknown", team_id=user.team_id, result=None)
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    # Store each row in GameData
    for _, row in df.iterrows():
        game_data = GameData(
            team_id=user.team_id,
            game_id=new_game.id,
            # player_id can be set if you have logic to match player names to Player.id
            row_type="pitching" if "Pitcher" in row else "batting",
            inning=str(row.get("Inning", "")),
            pitcher=str(row.get("Pitcher", "")),
            batter=str(row.get("Batter", "")),
            pitch_type=str(row.get("PitchType", "")),
            result=str(row.get("Result", "")),
            pitch_speed=str(row.get("RelSpeed", "")),
            exit_velocity=str(row.get("ExitSpeed", "")),
            play_result=str(row.get("PlayResult", "")),
        )
        db.add(game_data)
    db.commit()

    return {"message": "✅ CSV uploaded and data saved to database for your team.", "game_id": new_game.id, "row_count": len(df)}

@router.post(
    "/upload-persistent",
    summary="Upload CSV with persistent storage",
    description="Upload a CSV file with persistent storage and metadata. Coach or Admin role required."
)
async def upload_csv_persistent(
    file: UploadFile = File(...),
    game_date: Optional[str] = Form(None),
    opponent: Optional[str] = Form(None),
    game_result: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV file with persistent storage and metadata.
    """
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a team.")
    
    if not (hasattr(file, "filename") and str(file.filename).lower().endswith(".csv")):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    try:
        # Read the file contents
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{user.team_id}_{timestamp}_{file.filename}"
        
        # Create CSVFile record
        csv_file = CSVFile(
            filename=unique_filename,
            original_filename=file.filename,
            team_id=user.team_id,
            uploaded_by=user.id,
            file_size=len(contents),
            row_count=len(df),
            game_date=game_date,
            opponent=opponent,
            game_result=game_result,
            notes=notes,
            is_processed=0
        )
        
        db.add(csv_file)
        db.commit()
        db.refresh(csv_file)
        
        # Store each row as JSON in CSVData
        for index, row in df.iterrows():
            row_data = row.to_dict()
            # Handle NaN values by converting them to None
            for key, value in row_data.items():
                if pd.isna(value):
                    row_data[key] = None
            csv_data = CSVData(
                csv_file_id=csv_file.id,
                row_number=index + 1,
                data_json=json.dumps(row_data)
            )
            db.add(csv_data)
        
        # Mark file as processed
        csv_file.is_processed = 1
        
        db.commit()
        
        return {
            "message": "✅ CSV uploaded successfully with persistent storage.",
            "file_id": csv_file.id,
            "filename": csv_file.original_filename,
            "row_count": csv_file.row_count,
            "uploaded_at": csv_file.uploaded_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading CSV: {str(e)}")

@router.get(
    "/files",
    summary="List CSV files for team",
    description="Get all CSV files uploaded for the current user's team."
)
async def list_csv_files(
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    List all CSV files for the current user's team.
    """
    # Handle users without a team_id (admin users)
    if not user.team_id:
        # For admin users, show all CSV files
        csv_files = db.query(CSVFile).order_by(CSVFile.uploaded_at.desc()).all()
    else:
        # Get CSV files for the user's team
        csv_files = db.query(CSVFile).filter(CSVFile.team_id == user.team_id).order_by(CSVFile.uploaded_at.desc()).all()
    
    # Get uploader names
    from app.models.user import User as UserModel
    uploader_names = {}
    for csv_file in csv_files:
        if csv_file.uploaded_by not in uploader_names:
            uploader = db.query(UserModel).filter(UserModel.id == csv_file.uploaded_by).first()
            uploader_names[csv_file.uploaded_by] = uploader.name if uploader else "Unknown"
    
    # Build response
    response_files = []
    for csv_file in csv_files:
        response_files.append(CSVFileResponse(
            id=csv_file.id,
            filename=csv_file.filename,
            original_filename=csv_file.original_filename,
            team_id=csv_file.team_id,
            uploaded_by=csv_file.uploaded_by,
            uploaded_at=csv_file.uploaded_at,
            file_size=csv_file.file_size,
            row_count=csv_file.row_count,
            game_date=csv_file.game_date,
            opponent=csv_file.opponent,
            game_result=csv_file.game_result,
            notes=csv_file.notes,
            is_processed=csv_file.is_processed,
            uploader_name=uploader_names.get(csv_file.uploaded_by, "Unknown"),
            team_name=csv_file.team.name
        ))
    
    return response_files

@router.get(
    "/files/{file_id}",
    summary="Get CSV file data",
    description="Get the data from a specific CSV file."
)
async def get_csv_file_data(
    file_id: int,
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get the data from a specific CSV file.
    """
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a team.")
    
    # Get the CSV file
    csv_file = db.query(CSVFile).filter(
        CSVFile.id == file_id,
        CSVFile.team_id == user.team_id
    ).first()
    
    if not csv_file:
        raise HTTPException(status_code=404, detail="CSV file not found.")
    
    # Get the CSV data
    csv_data = db.query(CSVData).filter(CSVData.csv_file_id == file_id).order_by(CSVData.row_number).all()
    
    # Convert JSON data back to rows
    rows = []
    for data_row in csv_data:
        row_data = json.loads(data_row.data_json)
        rows.append(row_data)
    
    return {
        "file_info": {
            "id": csv_file.id,
            "filename": csv_file.original_filename,
            "uploaded_at": csv_file.uploaded_at.isoformat(),
            "row_count": csv_file.row_count,
            "game_date": csv_file.game_date,
            "opponent": csv_file.opponent,
            "game_result": csv_file.game_result,
            "notes": csv_file.notes
        },
        "data": rows
    }

@router.delete(
    "/files/{file_id}",
    summary="Delete CSV file",
    description="Delete a CSV file and its data."
)
async def delete_csv_file(
    file_id: int,
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a CSV file and its data.
    """
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a team.")
    
    # Get the CSV file
    csv_file = db.query(CSVFile).filter(
        CSVFile.id == file_id,
        CSVFile.team_id == user.team_id
    ).first()
    
    if not csv_file:
        raise HTTPException(status_code=404, detail="CSV file not found.")
    
    try:
        # Delete CSV data first
        db.query(CSVData).filter(CSVData.csv_file_id == file_id).delete()
        
        # Delete CSV file
        db.delete(csv_file)
        db.commit()
        
        return {"message": "CSV file deleted successfully."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting CSV file: {str(e)}")

@router.put(
    "/files/{file_id}/metadata",
    summary="Update CSV file metadata",
    description="Update metadata for a CSV file (game date, opponent, result, notes)."
)
async def update_csv_metadata(
    file_id: int,
    game_date: Optional[str] = Form(None),
    opponent: Optional[str] = Form(None),
    game_result: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Update metadata for a CSV file.
    """
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a team.")
    
    # Get the CSV file
    csv_file = db.query(CSVFile).filter(
        CSVFile.id == file_id,
        CSVFile.team_id == user.team_id
    ).first()
    
    if not csv_file:
        raise HTTPException(status_code=404, detail="CSV file not found.")
    
    try:
        # Update metadata
        if game_date is not None:
            csv_file.game_date = game_date
        if opponent is not None:
            csv_file.opponent = opponent
        if game_result is not None:
            csv_file.game_result = game_result
        if notes is not None:
            csv_file.notes = notes
        
        db.commit()
        
        return {"message": "CSV file metadata updated successfully."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating CSV file metadata: {str(e)}")


@router.get(
    "/team_pitchers",
    summary="Get pitchers for a team",
    description="Returns all pitchers for a given team from the uploaded CSV."
)
async def get_team_pitchers(
    team: str,
    user: User = Depends(require_coach_or_admin)
):
    """
    Return all pitchers for a given team.
    """
    print(f"DEBUG: Token received in get_team_pitchers: {user}")  # Debug token

    global uploaded_df
    if uploaded_df is None and os.path.exists(TEMP_CSV_PATH):
        uploaded_df = pd.read_csv(TEMP_CSV_PATH)

    if uploaded_df is None:
        raise HTTPException(status_code=404, detail="No CSV uploaded yet.")

    if 'Pitcher' not in uploaded_df.columns or 'PitcherTeam' not in uploaded_df.columns:
        return {"pitchers": []}

    # Ensure we are working with a pandas Series before calling dropna
    pitcher_series = uploaded_df.loc[uploaded_df['PitcherTeam'] == team, 'Pitcher']
    pitchers = pd.Series(pitcher_series).dropna().unique().tolist()
    return {"pitchers": pitchers}

@router.get(
    "/file/{file_id}/teams",
    summary="Get teams from a specific CSV file",
    description="Returns all teams found in a specific CSV file."
)
async def get_file_teams(
    file_id: int,
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get all teams found in a specific CSV file.
    """
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a team.")
    
    # Get the CSV file
    csv_file = db.query(CSVFile).filter(
        CSVFile.id == file_id,
        CSVFile.team_id == user.team_id
    ).first()
    
    if not csv_file:
        raise HTTPException(status_code=404, detail="CSV file not found.")
    
    # Get the CSV data
    csv_data = db.query(CSVData).filter(CSVData.csv_file_id == file_id).all()
    
    # Extract unique team names
    teams = set()
    for data_row in csv_data:
        try:
            row_data = json.loads(data_row.data_json)
            
            # Check for team fields
            if 'PitcherTeam' in row_data and row_data['PitcherTeam']:
                teams.add(row_data['PitcherTeam'])
            if 'BatterTeam' in row_data and row_data['BatterTeam']:
                teams.add(row_data['BatterTeam'])
            if 'Team' in row_data and row_data['Team']:
                teams.add(row_data['Team'])
        except (json.JSONDecodeError, KeyError):
            continue
    
    return {"teams": list(teams)}

@router.get(
    "/file/{file_id}/pitchers",
    summary="Get pitchers from a specific CSV file",
    description="Returns all pitchers found in a specific CSV file, optionally filtered by team."
)
async def get_file_pitchers(
    file_id: int,
    team: Optional[str] = None,
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get all pitchers found in a specific CSV file, optionally filtered by team.
    """
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a team.")
    
    # Get the CSV file
    csv_file = db.query(CSVFile).filter(
        CSVFile.id == file_id,
        CSVFile.team_id == user.team_id
    ).first()
    
    if not csv_file:
        raise HTTPException(status_code=404, detail="CSV file not found.")
    
    # Get the CSV data
    csv_data = db.query(CSVData).filter(CSVData.csv_file_id == file_id).all()
    
    # Extract unique pitcher names, filtered by team if specified
    pitchers = set()
    for data_row in csv_data:
        try:
            row_data = json.loads(data_row.data_json)
            
            # Check for pitcher fields
            if 'Pitcher' in row_data and row_data['Pitcher']:
                pitcher_name = row_data['Pitcher']
                pitcher_team = row_data.get('PitcherTeam')
                
                # Only include pitchers from the specified team (if team parameter is provided)
                if pitcher_name.lower() not in ['undefined', 'undefine', 'null', '']:
                    if team is None or pitcher_team == team:
                        pitchers.add(pitcher_name)
        except (json.JSONDecodeError, KeyError):
            continue
    
    return {"pitchers": list(pitchers)}

@router.get(
    "/my_team_pitchers",
    summary="Get pitchers for the current user's team",
    description="Returns all pitchers for the authenticated user's team from the database."
)
async def get_my_team_pitchers(
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Return all pitchers for the current user's team from the database.
    """
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a team.")
    
    # Get all unique pitchers from GameData (old system)
    pitchers_game_data = db.query(GameData.pitcher).filter(
        GameData.team_id == user.team_id,
        GameData.pitcher.isnot(None),
        GameData.pitcher != ""
    ).distinct().all()
    
    # Get user's team name
    user_team = db.query(Team).filter(Team.id == user.team_id).first()
    team_name = user_team.name if user_team else "Unknown"
    team_variations = get_team_variations(team_name)
    
    # Get all unique pitchers from CSVData (new persistent system)
    pitchers_csv_data = db.query(CSVData).join(CSVFile).filter(
        CSVFile.team_id == user.team_id,
        CSVData.data_json.isnot(None)
    ).all()
    
    # Extract pitcher names from CSVData JSON
    csv_pitchers = set()
    
    for csv_row in pitchers_csv_data:
        try:
            row_data = json.loads(csv_row.data_json)
            
            # Check if this row belongs to the user's team by checking team-related fields
            row_team = None
            if 'PitcherTeam' in row_data:
                row_team = row_data['PitcherTeam']
            elif 'BatterTeam' in row_data:
                row_team = row_data['BatterTeam']
            elif 'Team' in row_data:
                row_team = row_data['Team']
            
            # Only include players if the row belongs to the user's team
            if row_team and any(variation in str(row_team) for variation in team_variations):
                if 'Pitcher' in row_data and row_data['Pitcher'] and row_data['Pitcher'].lower() not in ['undefined', 'undefine', 'null', '']:
                    csv_pitchers.add(row_data['Pitcher'])
        except (json.JSONDecodeError, KeyError):
            continue
    
    # Combine both sources
    pitcher_list = list(set([pitcher[0] for pitcher in pitchers_game_data if pitcher[0]] + list(csv_pitchers)))
    return {"pitchers": pitcher_list}

@router.get(
    "/roster",
    summary="Get team roster",
    description="Returns all players (pitchers and batters) for the current user's team."
)
async def get_team_roster(
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """
    Return all players for the current user's team from the database.
    """
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a team.")
    
    # Get all unique pitchers from GameData (old system)
    pitchers_game_data = db.query(GameData.pitcher).filter(
        GameData.team_id == user.team_id,
        GameData.pitcher.isnot(None),
        GameData.pitcher != ""
    ).distinct().all()
    
    # Get all unique batters from GameData (old system)
    batters_game_data = db.query(GameData.batter).filter(
        GameData.team_id == user.team_id,
        GameData.batter.isnot(None),
        GameData.batter != ""
    ).distinct().all()
    
    print(f"DEBUG: Found {len(pitchers_game_data)} pitchers and {len(batters_game_data)} batters from GameData (old system)")
    
    # Get user's team name
    user_team = db.query(Team).filter(Team.id == user.team_id).first()
    team_name = user_team.name if user_team else "Unknown"
    team_variations = get_team_variations(team_name)
    
    # Debug logging
    print(f"DEBUG: User team_id: {user.team_id}")
    print(f"DEBUG: User team name: {team_name}")
    print(f"DEBUG: Team variations: {team_variations}")
    
    # Get all unique pitchers from CSVData (new persistent system)
    pitchers_csv_data = db.query(CSVData).join(CSVFile).filter(
        CSVFile.team_id == user.team_id,
        CSVData.data_json.isnot(None)
    ).all()
    
    # Get all unique batters from CSVData (new persistent system)
    batters_csv_data = db.query(CSVData).join(CSVFile).filter(
        CSVFile.team_id == user.team_id,
        CSVData.data_json.isnot(None)
    ).all()
    
    # Extract pitcher and batter names from CSVData JSON
    csv_pitchers = set()
    csv_batters = set()
    
    print(f"DEBUG: Processing {len(pitchers_csv_data)} CSV rows for team_id: {user.team_id}")
    
    for csv_row in pitchers_csv_data:
        try:
            row_data = json.loads(csv_row.data_json)
            
            # Check pitcher team and batter team separately
            pitcher_team = row_data.get('PitcherTeam')
            batter_team = row_data.get('BatterTeam')
            
            # Debug: Print team info for first few rows
            if len(csv_pitchers) < 5:  # Only print first few for debugging
                print(f"DEBUG: PitcherTeam: {pitcher_team}, BatterTeam: {batter_team}, User team variations: {team_variations}")
            
            # Check if pitcher belongs to user's team
            pitcher_team_match = pitcher_team and any(variation in str(pitcher_team) for variation in team_variations)
            
            # Check if batter belongs to user's team
            batter_team_match = batter_team and any(variation in str(batter_team) for variation in team_variations)
            
            # Add pitcher if they belong to user's team
            if pitcher_team_match and 'Pitcher' in row_data and row_data['Pitcher'] and row_data['Pitcher'].lower() not in ['undefined', 'undefine', 'null', '']:
                csv_pitchers.add(row_data['Pitcher'])
                if len(csv_pitchers) <= 5:  # Debug first few additions
                    print(f"DEBUG: ADDING pitcher: {row_data['Pitcher']} from team: {pitcher_team}")
            
            # Add batter if they belong to user's team
            if batter_team_match and 'Batter' in row_data and row_data['Batter'] and row_data['Batter'].lower() not in ['undefined', 'undefine', 'null', '']:
                csv_batters.add(row_data['Batter'])
                if len(csv_batters) <= 5:  # Debug first few additions
                    print(f"DEBUG: ADDING batter: {row_data['Batter']} from team: {batter_team}")
                    
        except (json.JSONDecodeError, KeyError):
            continue
    
    # Combine all sources
    pitcher_list = list(set([pitcher[0] for pitcher in pitchers_game_data if pitcher[0]] + list(csv_pitchers)))
    batter_list = list(set([batter[0] for batter in batters_game_data if batter[0]] + list(csv_batters)))
    
    print(f"DEBUG: Final results - Pitchers from GameData: {[pitcher[0] for pitcher in pitchers_game_data if pitcher[0]]}")
    print(f"DEBUG: Final results - Pitchers from CSVData: {list(csv_pitchers)}")
    print(f"DEBUG: Final results - Combined pitchers: {pitcher_list}")
    
    # Combine and deduplicate
    all_players = list(set(pitcher_list + batter_list))
    
    return {
        "team_id": user.team_id,
        "pitchers": pitcher_list,
        "batters": batter_list,
        "all_players": all_players
    }

@router.get(
    "/request_to_csv",
    summary="Convert Requested Data to CSV reporting tool",
    description="Returns a CSV file with the requested data."
)
async def request_to_csv(
    user: User = Depends(require_coach_or_admin)
):
    """
    Convert the uploaded CSV data to a formatted CSV for reporting.
    """
    print(f"DEBUG: Token received in request_to_csv: {user}")  # Debug token

    global uploaded_df
    if uploaded_df is None and os.path.exists(TEMP_CSV_PATH):
        uploaded_df = pd.read_csv(TEMP_CSV_PATH)

    if uploaded_df is None:
        raise HTTPException(status_code=404, detail="No CSV uploaded yet.")

    # For now, return the data as is
    # You can add specific formatting logic here based on your requirements
    return {
        "message": "✅ CSV data retrieved successfully",
        "row_count": len(uploaded_df),
        "columns": uploaded_df.columns.tolist(),
        "data_preview": uploaded_df.head().to_dict('records')
    }

@router.get(
    "/games",
    summary="List all games for the current user's team",
    description="Returns all games uploaded for the authenticated user's team."
)
async def list_team_games(user: User = Depends(require_coach_or_admin), db: Session = Depends(get_db)):
    games = db.query(Game).filter(Game.team_id == user.team_id).all()
    return [{
        "id": g.id,
        "date": g.date,
        "opponent": g.opponent,
        "result": g.result
    } for g in games]

@router.get(
    "/game_data/{game_id}",
    summary="Get all GameData rows for a specific game",
    description="Returns all parsed CSV rows (GameData) for a given game ID, for the current user's team."
)
async def get_game_data(game_id: int, user: User = Depends(require_coach_or_admin), db: Session = Depends(get_db)):
    # Ensure the game belongs to the user's team
    game = db.query(Game).filter(Game.id == game_id, Game.team_id == user.team_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found or not authorized.")
    rows = db.query(GameData).filter(GameData.game_id == game_id, GameData.team_id == user.team_id).all()
    return [
        {
            "id": row.id,
            "row_type": row.row_type,
            "inning": row.inning,
            "pitcher": row.pitcher,
            "batter": row.batter,
            "pitch_type": row.pitch_type,
            "result": row.result,
            "pitch_speed": row.pitch_speed,
            "exit_velocity": row.exit_velocity,
            "play_result": row.play_result
        }
        for row in rows
    ]

@router.get(
    "/game-report/{file_id}",
    summary="Get detailed game report",
    description="Get a comprehensive report for a specific game including pitching and batting statistics."
)
async def get_game_report(
    file_id: int, 
    user: User = Depends(require_coach_or_admin), 
    db: Session = Depends(get_db)
):
    """Get detailed report for a specific game"""
    try:
        # Get the CSV file
        csv_file = db.query(CSVFile).filter(CSVFile.id == file_id).first()
        if not csv_file:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Check if user has access to this team's data
        if user.role != 'admin' and csv_file.team_id != user.team_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all CSV data for this file
        csv_data = db.query(CSVData).filter(CSVData.csv_file_id == file_id).order_by(CSVData.row_number).all()
        
        if not csv_data:
            raise HTTPException(status_code=404, detail="No data found for this game")
        
        # Parse the data
        pitches = []
        pitchers = {}
        batters = {}
        game_summary = {
            'total_pitches': 0,
            'total_innings': 0,
            'home_team': '',
            'away_team': '',
            'game_date': csv_file.game_date,
            'opponent': csv_file.opponent,
            'result': csv_file.game_result,
            'notes': csv_file.notes
        }
        
        for row in csv_data:
            try:
                data = json.loads(row.data_json)
                pitches.append(data)
                
                # Track pitchers
                if 'Pitcher' in data and data['Pitcher'] and data['Pitcher'].lower() not in ['undefined', 'undefine', 'null', '']:
                    pitcher_name = data['Pitcher']
                    if pitcher_name not in pitchers:
                        pitchers[pitcher_name] = {
                            'name': pitcher_name,
                            'team': data.get('PitcherTeam', 'Unknown'),
                            'throws': data.get('PitcherThrows', 'Unknown'),
                            'pitches': 0,
                            'strikes': 0,
                            'balls': 0,
                            'strikeouts': 0,
                            'walks': 0,
                            'hits': 0,
                            'runs': 0,
                            'avg_speed': 0,
                            'pitch_types': {}
                        }
                    
                    pitchers[pitcher_name]['pitches'] += 1
                    
                    # Track pitch types
                    pitch_type = data.get('AutoPitchType', 'Unknown')
                    if pitch_type not in pitchers[pitcher_name]['pitch_types']:
                        pitchers[pitcher_name]['pitch_types'][pitch_type] = 0
                    pitchers[pitcher_name]['pitch_types'][pitch_type] += 1
                    
                    # Track pitch outcomes
                    pitch_call = data.get('PitchCall', '')
                    if 'Strike' in pitch_call:
                        pitchers[pitcher_name]['strikes'] += 1
                    elif 'Ball' in pitch_call:
                        pitchers[pitcher_name]['balls'] += 1
                    
                    # Track results
                    kor_bb = data.get('KorBB', '')
                    if 'Strikeout' in kor_bb:
                        pitchers[pitcher_name]['strikeouts'] += 1
                    elif 'Walk' in kor_bb:
                        pitchers[pitcher_name]['walks'] += 1
                    
                    # Track hits and runs
                    play_result = data.get('PlayResult', '')
                    if play_result in ['Single', 'Double', 'Triple', 'HomeRun']:
                        pitchers[pitcher_name]['hits'] += 1
                    
                    runs_scored = data.get('RunsScored', 0)
                    if runs_scored:
                        pitchers[pitcher_name]['runs'] += int(runs_scored)
                    
                    # Track speed
                    rel_speed = data.get('RelSpeed')
                    if rel_speed and rel_speed != 'Undefined':
                        try:
                            speed = float(rel_speed)
                            current_avg = pitchers[pitcher_name]['avg_speed']
                            total_pitches = pitchers[pitcher_name]['pitches']
                            pitchers[pitcher_name]['avg_speed'] = ((current_avg * (total_pitches - 1)) + speed) / total_pitches
                        except (ValueError, TypeError):
                            pass
                
                # Track batters
                if 'Batter' in data and data['Batter'] and data['Batter'].lower() not in ['undefined', 'undefine', 'null', '']:
                    batter_name = data['Batter']
                    if batter_name not in batters:
                        batters[batter_name] = {
                            'name': batter_name,
                            'team': data.get('BatterTeam', 'Unknown'),
                            'side': data.get('BatterSide', 'Unknown'),
                            'at_bats': 0,
                            'hits': 0,
                            'walks': 0,
                            'strikeouts': 0,
                            'runs': 0,
                            'avg_exit_velocity': 0,
                            'hit_types': {}
                        }
                    
                    # Track at-bats and results
                    play_result = data.get('PlayResult', '')
                    kor_bb = data.get('KorBB', '')
                    
                    if play_result in ['Single', 'Double', 'Triple', 'HomeRun', 'Out']:
                        batters[batter_name]['at_bats'] += 1
                        if play_result in ['Single', 'Double', 'Triple', 'HomeRun']:
                            batters[batter_name]['hits'] += 1
                    elif 'Walk' in kor_bb:
                        batters[batter_name]['walks'] += 1
                    elif 'Strikeout' in kor_bb:
                        batters[batter_name]['strikeouts'] += 1
                    
                    # Track runs
                    runs_scored = data.get('RunsScored', 0)
                    if runs_scored:
                        batters[batter_name]['runs'] += int(runs_scored)
                    
                    # Track exit velocity
                    exit_speed = data.get('ExitSpeed')
                    if exit_speed and exit_speed != 'Undefined':
                        try:
                            speed = float(exit_speed)
                            current_avg = batters[batter_name]['avg_exit_velocity']
                            total_hits = batters[batter_name]['hits']
                            if total_hits > 0:
                                batters[batter_name]['avg_exit_velocity'] = ((current_avg * (total_hits - 1)) + speed) / total_hits
                        except (ValueError, TypeError):
                            pass
                    
                    # Track hit types
                    hit_type = data.get('TaggedHitType', '')
                    if hit_type and hit_type != 'Undefined':
                        if hit_type not in batters[batter_name]['hit_types']:
                            batters[batter_name]['hit_types'][hit_type] = 0
                        batters[batter_name]['hit_types'][hit_type] += 1
                
                # Track game summary
                game_summary['total_pitches'] += 1
                
                # Track teams
                if not game_summary['home_team'] and data.get('HomeTeam'):
                    game_summary['home_team'] = data['HomeTeam']
                if not game_summary['away_team'] and data.get('AwayTeam'):
                    game_summary['away_team'] = data['AwayTeam']
                
                # Track innings
                inning = data.get('Inning', 0)
                if inning:
                    try:
                        inning_num = int(inning)
                        game_summary['total_innings'] = max(game_summary['total_innings'], inning_num)
                    except (ValueError, TypeError):
                        pass
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing row {row.row_number}: {e}")
                continue
        
        # Calculate additional stats
        for pitcher in pitchers.values():
            if pitcher['pitches'] > 0:
                pitcher['strike_percentage'] = (pitcher['strikes'] / pitcher['pitches']) * 100
                pitcher['ball_percentage'] = (pitcher['balls'] / pitcher['pitches']) * 100
        
        for batter in batters.values():
            if batter['at_bats'] > 0:
                batter['batting_average'] = (batter['hits'] / batter['at_bats']) * 1000  # Format as .XXX
            else:
                batter['batting_average'] = 0
        
        return {
            "game_summary": game_summary,
            "pitchers": list(pitchers.values()),
            "batters": list(batters.values()),
            "pitches": pitches[:100]  # Limit to first 100 pitches for performance
        }
        
    except Exception as e:
        print(f"Error generating game report: {e}")
        raise HTTPException(status_code=500, detail="Error generating game report")

@router.get(
    "/game-report/{file_id}/pitcher/{pitcher_name}",
    summary="Get detailed game report for a specific pitcher",
    description="Get a comprehensive report for a specific pitcher in a specific game."
)
async def get_pitcher_game_report(
    file_id: int,
    pitcher_name: str,
    user: User = Depends(require_coach_or_admin), 
    db: Session = Depends(get_db)
):
    """Get detailed report for a specific pitcher in a specific game"""
    try:
        # URL decode the pitcher name
        pitcher_name = unquote(pitcher_name)
        print(f"DEBUG: Processing pitcher game report for file_id={file_id}, pitcher={pitcher_name}")
        
        # Get the CSV file
        csv_file = db.query(CSVFile).filter(CSVFile.id == file_id).first()
        if not csv_file:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Check if user has access to this team's data
        if user.role != 'admin' and csv_file.team_id != user.team_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all CSV data for this file
        csv_data = db.query(CSVData).filter(CSVData.csv_file_id == file_id).order_by(CSVData.row_number).all()
        print(f"DEBUG: Found {len(csv_data)} rows of CSV data")
        
        if not csv_data:
            raise HTTPException(status_code=404, detail="No data found for this game")
        
        # Filter data for the specific pitcher
        pitcher_pitches = []
        pitcher_stats = {
            'name': pitcher_name,
            'team': '',
            'throws': '',
            'pitches': 0,
            'strikes': 0,
            'balls': 0,
            'strikeouts': 0,
            'walks': 0,
            'hits': 0,
            'runs': 0,
            'avg_speed': 0,
            'pitch_types': {},
            'innings_pitched': 0,
            'current_inning': 0
        }
        
        for row in csv_data:
            try:
                data = json.loads(row.data_json)
                
                # Only include pitches from this specific pitcher
                if 'Pitcher' in data and data['Pitcher'] == pitcher_name:
                    pitcher_pitches.append(data)
                    
                    # Track basic stats
                    pitcher_stats['pitches'] += 1
                    
                    # Set team and throws info
                    if not pitcher_stats['team']:
                        pitcher_stats['team'] = data.get('PitcherTeam', 'Unknown')
                    if not pitcher_stats['throws']:
                        pitcher_stats['throws'] = data.get('PitcherThrows', 'Unknown')
                    
                    # Track pitch types
                    pitch_type = data.get('AutoPitchType', 'Unknown')
                    if pitch_type not in pitcher_stats['pitch_types']:
                        pitcher_stats['pitch_types'][pitch_type] = 0
                    pitcher_stats['pitch_types'][pitch_type] += 1
                    
                    # Track pitch outcomes
                    pitch_call = data.get('PitchCall', '')
                    if 'Strike' in pitch_call:
                        pitcher_stats['strikes'] += 1
                    elif 'Ball' in pitch_call:
                        pitcher_stats['balls'] += 1
                    
                    # Track results
                    kor_bb = data.get('KorBB', '')
                    if 'Strikeout' in kor_bb:
                        pitcher_stats['strikeouts'] += 1
                    elif 'Walk' in kor_bb:
                        pitcher_stats['walks'] += 1
                    
                    # Track hits and runs
                    play_result = data.get('PlayResult', '')
                    if play_result in ['Single', 'Double', 'Triple', 'HomeRun']:
                        pitcher_stats['hits'] += 1
                    
                    runs_scored = data.get('RunsScored', 0)
                    if runs_scored:
                        pitcher_stats['runs'] += int(runs_scored)
                    
                    # Track speed
                    rel_speed = data.get('RelSpeed')
                    if rel_speed and rel_speed != 'Undefined':
                        try:
                            speed = float(rel_speed)
                            current_avg = pitcher_stats['avg_speed']
                            total_pitches = pitcher_stats['pitches']
                            pitcher_stats['avg_speed'] = ((current_avg * (total_pitches - 1)) + speed) / total_pitches
                        except (ValueError, TypeError):
                            pass
                    
                    # Track innings
                    inning = data.get('Inning', 0)
                    if inning and inning != pitcher_stats['current_inning']:
                        pitcher_stats['current_inning'] = inning
                        pitcher_stats['innings_pitched'] += 1
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"DEBUG: Error processing row {row.row_number}: {str(e)}")
                continue
        
        print(f"DEBUG: Found {len(pitcher_pitches)} pitches for pitcher {pitcher_name}")
        
        if not pitcher_pitches:
            raise HTTPException(status_code=404, detail=f"No data found for pitcher {pitcher_name} in this game")
        
        # Calculate additional stats
        if pitcher_stats['pitches'] > 0:
            pitcher_stats['strike_percentage'] = (pitcher_stats['strikes'] / pitcher_stats['pitches']) * 100
            pitcher_stats['ball_percentage'] = (pitcher_stats['balls'] / pitcher_stats['pitches']) * 100
        
        # Calculate detailed per-pitch metrics using PlayerMetricsAnalyzer
        try:
            from PythonFiles.core.player_metrics import PlayerMetricsAnalyzer
            df = pd.DataFrame(pitcher_pitches)
            analyzer = PlayerMetricsAnalyzer(df, pitcher_name)
            per_pitch_df = analyzer.per_pitch_type_metrics_df()
            
            # Convert DataFrame to list of dictionaries for JSON serialization
            per_pitch_metrics = []
            for _, row in per_pitch_df.iterrows():
                row_dict = {}
                for col in per_pitch_df.columns:
                    value = row[col]
                    # Handle NaN values
                    if pd.isna(value):
                        row_dict[col] = None
                    else:
                        row_dict[col] = value
                per_pitch_metrics.append(row_dict)
            
            pitcher_stats['per_pitch_metrics'] = per_pitch_metrics
            print(f"DEBUG: Calculated per-pitch metrics: {len(per_pitch_metrics)} rows")
            
        except Exception as e:
            print(f"DEBUG: Error calculating per-pitch metrics: {str(e)}")
            pitcher_stats['per_pitch_metrics'] = []
        
        game_summary = {
            'total_pitches': len(pitcher_pitches),
            'game_date': csv_file.game_date,
            'opponent': csv_file.opponent,
            'result': csv_file.game_result,
            'notes': csv_file.notes,
            'pitcher_name': pitcher_name
        }
        
        print(f"DEBUG: Returning game report with {len(pitcher_pitches)} pitches")
        
        return {
            "game_summary": game_summary,
            "pitcher_stats": pitcher_stats,
            "pitches": pitcher_pitches
        }
        
    except Exception as e:
        print(f"Error in get_pitcher_game_report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating pitcher report: {str(e)}")

@router.get(
    "/game-report/{file_id}/pitcher/{pitcher_name}/pdf",
    summary="Download PDF report for a specific pitcher in a specific game",
    description="Generate and download a PDF report for a specific pitcher in a specific game."
)
async def download_pitcher_game_report_pdf(
    file_id: int,
    pitcher_name: str,
    user: User = Depends(require_coach_or_admin), 
    db: Session = Depends(get_db)
):
    """Download PDF report for a specific pitcher in a specific game."""
    from PythonFiles.summary.export import export_summary_to_pdf
    from PythonFiles.core.player_metrics import PlayerMetricsAnalyzer
    
    try:
        # URL decode the pitcher name
        pitcher_name = unquote(pitcher_name)
        print(f"DEBUG: Processing PDF download for file_id={file_id}, pitcher={pitcher_name}")
        
        # Get the CSV file
        csv_file = db.query(CSVFile).filter(CSVFile.id == file_id).first()
        if not csv_file:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Check if user has access to this team's data
        if user.role != 'admin' and csv_file.team_id != user.team_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all CSV data for this file
        csv_data = db.query(CSVData).filter(CSVData.csv_file_id == file_id).order_by(CSVData.row_number).all()
        print(f"DEBUG: Found {len(csv_data)} rows of CSV data for PDF generation")
        
        if not csv_data:
            raise HTTPException(status_code=404, detail="No data found for this game")
        
        # Convert to DataFrame for analysis
        df_data = []
        for row in csv_data:
            try:
                data = json.loads(row.data_json)
                if 'Pitcher' in data and data['Pitcher'] == pitcher_name:
                    df_data.append(data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"DEBUG: Error processing row {row.row_number} for PDF: {str(e)}")
                continue
        
        print(f"DEBUG: Found {len(df_data)} pitches for PDF generation")
        
        if not df_data:
            raise HTTPException(status_code=404, detail=f"No data found for pitcher {pitcher_name} in this game")
        
        # Convert to DataFrame
        df = pd.DataFrame(df_data)
        print(f"DEBUG: DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame columns: {list(df.columns)}")
        
        # Get per-pitch-type metrics
        analyzer = PlayerMetricsAnalyzer(df, pitcher_name)
        per_pitch_df = analyzer.per_pitch_type_metrics_df()
        print(f"DEBUG: Per-pitch metrics shape: {per_pitch_df.shape}")
        
        # Plotting functions
        def plot_breaks(ax):
            pitch_col = analyzer.get_pitch_type_column()
            print(f"DEBUG: Using pitch column: {pitch_col}")
            for pitch_type, group in df.groupby(pitch_col):
                if pd.notna(pitch_type) and pitch_type != '' and pitch_type != 'Unknown':
                    ax.scatter(group["HorzBreak"], group["InducedVertBreak"], label=pitch_type)
            ax.set_xlabel("Horizontal Break (in)")
            ax.set_ylabel("Vertical Break (in)")
            ax.set_title("Pitch Breaks")
            ax.set_xlim(-25, 25)
            ax.set_ylim(-25, 25)
            # Add 0" axis lines
            ax.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.7)
            ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.7)
            ax.legend()
            ax.grid(True)

        def plot_release_points(ax):
            pitch_col = analyzer.get_pitch_type_column()
            df_clean = df.dropna(subset=["RelSide", "RelHeight"])
            print(f"DEBUG: Clean DataFrame shape for release points: {df_clean.shape}")
            for pitch_type, group in df_clean.groupby(pitch_col):
                if pd.notna(pitch_type) and pitch_type != '' and pitch_type != 'Unknown':
                    ax.scatter(group["RelSide"], group["RelHeight"], label=pitch_type)
            ax.set_xlabel("Horizontal Release Side (ft)")
            ax.set_ylabel("Vertical Release Height (ft)")
            ax.set_title("Release Points")
            ax.set_xlim(-3.5, 3.5)
            ax.set_ylim(1, 7)
            # Add 0" axis lines
            ax.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.7)
            ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.7)
            ax.legend()
            ax.grid(True)

        # Generate PDF
        print(f"DEBUG: Generating PDF for {pitcher_name}")
        pdf_path = export_summary_to_pdf(
            player_name=pitcher_name,
            summary_text=f"Game Report - {csv_file.game_date} vs {csv_file.opponent}",
            plot_funcs=[plot_breaks, plot_release_points],
            metrics_df=per_pitch_df
        )
        print(f"DEBUG: PDF generated at: {pdf_path}")

        return FileResponse(pdf_path, media_type='application/pdf', filename=f"{pitcher_name}_{csv_file.game_date}_report.pdf")
        
    except Exception as e:
        print(f"Error in download_pitcher_game_report_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.get(
    "/player-profile",
    summary="Get detailed player profile",
    description="Get comprehensive season statistics and analysis for a specific player."
)
async def get_player_profile(
    player_name: str,
    player_type: str = "all",
    count: str = "all",
    pitch_type: str = "all", 
    result: str = "all",
    min_velocity: Optional[float] = None,
    max_velocity: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed profile for a specific player"""
    try:
        # URL decode the player name to handle special characters
        decoded_player_name = unquote(player_name)
        print(f"DEBUG: Original player_name: '{player_name}'")
        print(f"DEBUG: Decoded player_name: '{decoded_player_name}'")
        
        # Get all CSV files for the user's team
        csv_files = db.query(CSVFile).filter(CSVFile.team_id == current_user.team_id).all()
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No games found for this team")
        
        # Get user's team name and variations for matching
        user_team = db.query(Team).filter(Team.id == current_user.team_id).first()
        team_name = user_team.name if user_team else "Unknown"
        team_variations = get_team_variations(team_name)
        
        print(f"DEBUG: Looking for player '{decoded_player_name}' ({player_type}) in team: {team_name}")
        print(f"DEBUG: Team variations: {team_variations}")
        print(f"DEBUG: Found {len(csv_files)} CSV files to search through")
        
        # Collect all data for this player across all games
        all_player_data = []
        games_played = 0
        
        # Get all possible variations of the player name
        player_name_variations = get_player_name_variations(decoded_player_name)
        print(f"DEBUG: Looking for player variations: {player_name_variations}")
        
        # Debug: Collect all unique batter names to see what's available
        all_batter_names = set()
        all_pitcher_names = set()
        
        for csv_file in csv_files:
            csv_data = db.query(CSVData).filter(CSVData.csv_file_id == csv_file.id).all()
            
            for row in csv_data:
                try:
                    data = json.loads(row.data_json)
                    
                    # Collect all batter and pitcher names for debugging
                    if data.get('Batter'):
                        all_batter_names.add(data.get('Batter'))
                    if data.get('Pitcher'):
                        all_pitcher_names.add(data.get('Pitcher'))
                    
                    # Check if this row contains data for our player (using name variations)
                    if player_type.lower() == 'pitcher':
                        if data.get('Pitcher') in player_name_variations:
                            # Temporarily bypass team matching for debugging
                            all_player_data.append({
                                'game_date': csv_file.game_date,
                                'opponent': csv_file.opponent,
                                'result': csv_file.game_result,
                                'data': data
                            })
                            if csv_file.game_date not in [g['game_date'] for g in all_player_data[:-1]]:
                                games_played += 1
                                
                    elif player_type.lower() == 'batter':
                        if data.get('Batter') in player_name_variations:
                            # Temporarily bypass team matching for debugging
                            all_player_data.append({
                                'game_date': csv_file.game_date,
                                'opponent': csv_file.opponent,
                                'result': csv_file.game_result,
                                'data': data
                            })
                            if csv_file.game_date not in [g['game_date'] for g in all_player_data[:-1]]:
                                games_played += 1
                                
                    elif player_type.lower() == 'all':
                        # Check both pitcher and batter data for this player (using name variations)
                        if data.get('Pitcher') in player_name_variations or data.get('Batter') in player_name_variations:
                            # Temporarily bypass team matching for debugging
                            all_player_data.append({
                                'game_date': csv_file.game_date,
                                'opponent': csv_file.opponent,
                                'result': csv_file.game_result,
                                'data': data
                            })
                            if csv_file.game_date not in [g['game_date'] for g in all_player_data[:-1]]:
                                games_played += 1
                                    
                except (json.JSONDecodeError, KeyError) as e:
                    continue
        
        print(f"DEBUG: All available batter names: {sorted(list(all_batter_names))}")
        print(f"DEBUG: All available pitcher names: {sorted(list(all_pitcher_names))}")
        print(f"DEBUG: Found {len(all_player_data)} data points for player '{decoded_player_name}'")
        print(f"DEBUG: Filter parameters - count: '{count}', pitch_type: '{pitch_type}', result: '{result}'")
        print(f"DEBUG: Sample data point: {all_player_data[0] if all_player_data else 'No data'}")
        
        if not all_player_data:
            raise HTTPException(status_code=404, detail="No data found for this player")
        
        # Apply additional filters
        filtered_player_data = all_player_data.copy()
        
        if count and count != "all":
            # Handle comma-separated count values
            count_list = count.split(',') if count else []
            if count_list:
                filtered_player_data = [p for p in filtered_player_data 
                                      if f"{p['data'].get('Balls', '0')}-{p['data'].get('Strikes', '0')}" in count_list]
        
        if pitch_type and pitch_type != "all":
            # Handle comma-separated pitch type values
            pitch_type_list = pitch_type.split(',') if pitch_type else []
            if pitch_type_list:

                
                # Try multiple field names for pitch type
                filtered_player_data = [p for p in filtered_player_data 
                                      if (p['data'].get('AutoPitchType') in pitch_type_list or
                                          p['data'].get('TaggedPitchType') in pitch_type_list or
                                          p['data'].get('PitchType') in pitch_type_list or
                                          p['data'].get('PitchCall') in pitch_type_list)]
        
        if result != "all":
            filtered_player_data = [p for p in filtered_player_data 
                                  if p['data'].get('PitchCall') == result]
        
        if min_velocity is not None:
            filtered_player_data = [p for p in filtered_player_data 
                                  if p['data'].get('RelSpeed') and 
                                  p['data'].get('RelSpeed') != 'Undefined' and
                                  float(p['data'].get('RelSpeed', 0)) >= min_velocity]
        
        if max_velocity is not None:
            filtered_player_data = [p for p in filtered_player_data 
                                  if p['data'].get('RelSpeed') and 
                                  p['data'].get('RelSpeed') != 'Undefined' and
                                  float(p['data'].get('RelSpeed', 0)) <= max_velocity]
        
        print(f"DEBUG: After filtering, {len(filtered_player_data)} data points remain")
        
        # Calculate season statistics
        season_stats = calculate_season_stats(filtered_player_data, player_type)
        
        # Calculate pitch analysis
        pitch_analysis = calculate_pitch_analysis(filtered_player_data, player_type)
        
        # Get recent games
        recent_games = get_recent_games(filtered_player_data)
        
        # Calculate heat map data
        heat_maps = calculate_heat_map_data(filtered_player_data, player_type)
        
        # Get available pitch types for this pitcher (only include types with actual data)
        available_pitch_types = []
        pitch_types_data = pitch_analysis.get("pitch_types", {})
        
        # Debug: Print the raw pitch types data
        print(f"DEBUG: Raw pitch types data for {player_name}: {pitch_types_data}")
        
        for pitch_type, data in pitch_types_data.items():
            count = data.get("count", 0)
            print(f"DEBUG: Pitch type '{pitch_type}' has count: {count}")
            if count > 0:  # Only include pitch types that have actual pitches
                available_pitch_types.append(pitch_type)
        
        print(f"DEBUG: Final available pitch types for {player_name}: {available_pitch_types}")
        
        return {
            "season_stats": season_stats,
            "pitch_analysis": pitch_analysis,
            "heat_maps": heat_maps,
            "recent_games": recent_games,
            "available_pitch_types": available_pitch_types
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating player profile: {str(e)}")

def calculate_season_stats(player_data, player_type):
    """Calculate season statistics for a player"""
    total_events = len(player_data)
    
    if player_type.lower() == 'pitcher':
        strikes = sum(1 for p in player_data if 'Strike' in p['data'].get('PitchCall', ''))
        strike_rate = (strikes / total_events * 100) if total_events > 0 else 0
        
        speeds = [float(p['data'].get('RelSpeed', 0)) for p in player_data 
                 if p['data'].get('RelSpeed') and p['data'].get('RelSpeed') != 'Undefined']
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        
        # Calculate batting average against
        hits_allowed = sum(1 for p in player_data if p['data'].get('PlayResult') in ['Single', 'Double', 'Triple', 'HomeRun'])
        at_bats_against = sum(1 for p in player_data if p['data'].get('PlayResult') in ['Single', 'Double', 'Triple', 'HomeRun', 'Out'])
        batting_average_against = (hits_allowed / at_bats_against * 1000) if at_bats_against > 0 else 0
        
        return {
            "games_played": len(set(p['game_date'] for p in player_data)),
            "total_events": total_events,
            "strike_rate": strike_rate,
            "avg_speed": avg_speed,
            "batting_average_against": batting_average_against,
            "performance_metrics": {
                "strikes": strikes,
                "balls": total_events - strikes,
                "strikeouts": sum(1 for p in player_data if 'Strikeout' in p['data'].get('KorBB', '')),
                "walks": sum(1 for p in player_data if 'Walk' in p['data'].get('KorBB', '')),
                "hits_allowed": hits_allowed,
                "at_bats_against": at_bats_against
            }
        }
    else:  # batter
        at_bats = sum(1 for p in player_data if p['data'].get('PlayResult') in ['Single', 'Double', 'Triple', 'HomeRun', 'Out'])
        hits = sum(1 for p in player_data if p['data'].get('PlayResult') in ['Single', 'Double', 'Triple', 'HomeRun'])
        batting_average = (hits / at_bats * 1000) if at_bats > 0 else 0
        
        exit_velocities = [float(p['data'].get('ExitSpeed', 0)) for p in player_data 
                          if p['data'].get('ExitSpeed') and p['data'].get('ExitSpeed') != 'Undefined']
        avg_exit_velocity = sum(exit_velocities) / len(exit_velocities) if exit_velocities else 0
        
        return {
            "games_played": len(set(p['game_date'] for p in player_data)),
            "total_events": total_events,
            "batting_average": batting_average,
            "avg_exit_velocity": avg_exit_velocity,
            "performance_metrics": {
                "at_bats": at_bats,
                "hits": hits,
                "walks": sum(1 for p in player_data if 'Walk' in p['data'].get('KorBB', '')),
                "strikeouts": sum(1 for p in player_data if 'Strikeout' in p['data'].get('KorBB', '')),
                "runs": sum(int(p['data'].get('RunsScored', 0)) for p in player_data if p['data'].get('RunsScored'))
            }
        }

def calculate_pitch_analysis(player_data, player_type):
    """Calculate pitch type analysis for a player"""
    if player_type.lower() != 'pitcher':
        return {"pitch_types": {}}
    
    pitch_types = {}
    
    for p in player_data:
        pitch_type = p['data'].get('AutoPitchType', 'Unknown')
        if pitch_type not in pitch_types:
            pitch_types[pitch_type] = {
                'count': 0,
                'successes': 0,
                'speeds': [],
                'spin_rates': []
            }
        
        pitch_types[pitch_type]['count'] += 1
        
        # Track success (strikes)
        if 'Strike' in p['data'].get('PitchCall', ''):
            pitch_types[pitch_type]['successes'] += 1
        
        # Track speed
        speed = p['data'].get('RelSpeed')
        if speed and speed != 'Undefined':
            try:
                pitch_types[pitch_type]['speeds'].append(float(speed))
            except (ValueError, TypeError):
                pass
        
        # Track spin rate
        spin_rate = p['data'].get('SpinRate')
        if spin_rate and spin_rate != 'Undefined':
            try:
                pitch_types[pitch_type]['spin_rates'].append(float(spin_rate))
            except (ValueError, TypeError):
                pass
    
    # Calculate averages and success rates
    for pitch_type, data in pitch_types.items():
        data['success_rate'] = (data['successes'] / data['count'] * 100) if data['count'] > 0 else 0
        data['avg_speed'] = sum(data['speeds']) / len(data['speeds']) if data['speeds'] else 0
        data['spin_rate'] = sum(data['spin_rates']) / len(data['spin_rates']) if data['spin_rates'] else None
    
    return {"pitch_types": pitch_types}

def get_recent_games(player_data):
    """Get recent games for a player"""
    games = {}
    
    for p in player_data:
        game_date = p['game_date']
        if game_date not in games:
            games[game_date] = {
                'date': game_date,
                'opponent': p['opponent'],
                'result': p['result'],
                'performance_summary': f"{len([d for d in player_data if d['game_date'] == game_date])} events"
            }
    
    # Sort by date and return recent games
    sorted_games = sorted(games.values(), key=lambda x: x['date'], reverse=True)
    return sorted_games[:5]  # Return last 5 games

def calculate_heat_map_data(player_data, player_type):
    """Calculate heat map data for pitch locations and velocities"""
    if player_type.lower() not in ['pitcher', 'batter']:
        return {
            "pitch_locations": [],
            "velocities": [],
            "strike_zone": {
                "width": 1.0,
                "height": 1.0,
                "center_x": 0.0,
                "center_y": 0.0
            }
        }
    
    # Define the 3x3 zones that match the frontend
    zones = [
        { 'x': -0.85, 'y': 3.6, 'w': 0.57, 'h': 0.6 },
        { 'x': -0.28, 'y': 3.6, 'w': 0.57, 'h': 0.6 },
        { 'x': 0.28, 'y': 3.6, 'w': 0.57, 'h': 0.6 },
        { 'x': -0.85, 'y': 3.0, 'w': 0.57, 'h': 0.6 },
        { 'x': -0.28, 'y': 3.0, 'w': 0.57, 'h': 0.6 },
        { 'x': 0.28, 'y': 3.0, 'w': 0.57, 'h': 0.6 },
        { 'x': -0.85, 'y': 2.4, 'w': 0.57, 'h': 0.6 },
        { 'x': -0.28, 'y': 2.4, 'w': 0.57, 'h': 0.6 },
        { 'x': 0.28, 'y': 2.4, 'w': 0.57, 'h': 0.6 }
    ]
    
    # Initialize zone data
    zone_data = {i: {
        'strikes': 0, 
        'total': 0, 
        'velocities': [], 
        'hits': 0, 
        'balls_in_play': 0,
        'swinging_strikes': 0,
        'called_strikes': 0,
        'weak_contact': 0  # Exit velocity < 85 mph
    } for i in range(len(zones))}
    
    total_pitches = 0
    
    for p in player_data:
        data = p['data']
        
        # Extract pitch location data
        plate_x = data.get('PlateLocSide')
        plate_z = data.get('PlateLocHeight')
        rel_speed = data.get('RelSpeed')
        pitch_call = data.get('PitchCall', '')
        play_result = data.get('PlayResult', '')
        exit_velocity = data.get('ExitSpeed')
        
        if plate_x is not None and plate_z is not None:
            try:
                x = float(plate_x)
                z = float(plate_z)
                
                # Find which zone this pitch belongs to
                for i, zone in enumerate(zones):
                    if (x >= zone['x'] and x < zone['x'] + zone['w'] and
                        z >= zone['y'] and z < zone['y'] + zone['h']):
                        
                        zone_data[i]['total'] += 1
                        total_pitches += 1
                        
                        # Track different types of strikes
                        if 'Strike' in pitch_call:
                            zone_data[i]['strikes'] += 1
                            if 'Swinging' in pitch_call or 'Foul' in pitch_call:
                                zone_data[i]['swinging_strikes'] += 1
                            else:
                                zone_data[i]['called_strikes'] += 1
                        
                        # Track balls in play and hits
                        if play_result in ['Single', 'Double', 'Triple', 'HomeRun', 'Out']:
                            zone_data[i]['balls_in_play'] += 1
                            if play_result in ['Single', 'Double', 'Triple', 'HomeRun']:
                                zone_data[i]['hits'] += 1
                            
                            # Track weak contact (exit velocity < 85 mph)
                            if exit_velocity and exit_velocity != 'Undefined':
                                try:
                                    ev = float(exit_velocity)
                                    if ev < 85:
                                        zone_data[i]['weak_contact'] += 1
                                except (ValueError, TypeError):
                                    pass
                        
                        # Track velocity
                        if rel_speed and rel_speed != 'Undefined':
                            try:
                                velocity = float(rel_speed)
                                zone_data[i]['velocities'].append(velocity)
                            except (ValueError, TypeError):
                                pass
                        break
                        
            except (ValueError, TypeError):
                continue
    
    # Convert zone data to heat map format
    heat_map_data = []
    velocity_heat_map = []
    
    print(f"DEBUG: Total pitches: {total_pitches}")
    
    for i, zone in enumerate(zones):
        data = zone_data[i]
        
        if data['total'] > 0:
            # Calculate composite success score (0-1, where 0 is best, 1 is worst)
            whiff_rate = (data['swinging_strikes'] / data['total']) if data['total'] > 0 else 0
            called_strike_rate = (data['called_strikes'] / data['total']) if data['total'] > 0 else 0
            weak_contact_rate = (data['weak_contact'] / data['balls_in_play']) if data['balls_in_play'] > 0 else 0
            
            # Weighted success score: 40% whiff rate + 30% called strike rate + 30% weak contact rate
            # Note: We invert the score so 0 = excellent, 1 = poor
            success_score = 1.0 - (0.4 * whiff_rate + 0.3 * called_strike_rate + 0.3 * weak_contact_rate)
            
            # Calculate batting average against (hits / balls in play)
            batting_avg = (data['hits'] / data['balls_in_play']) if data['balls_in_play'] > 0 else 0
            
            # Calculate average velocity
            avg_velocity = sum(data['velocities']) / len(data['velocities']) if data['velocities'] else 0
            
            print(f"DEBUG: Zone {i} ({zone['x']:.2f}, {zone['y']:.2f}): {data['total']} pitches, whiff={whiff_rate:.3f}, called={called_strike_rate:.3f}, weak={weak_contact_rate:.3f}, success={success_score:.3f}")
            
            heat_map_data.append({
                'x': zone['x'],
                'y': zone['y'],
                'count': data['total'],
                'strikes': data['strikes'],
                'total': data['total'],
                'success_score': round(success_score, 3),
                'hits': data['hits']
            })
            
            velocity_heat_map.append({
                'x': zone['x'],
                'y': zone['y'],
                'avg_velocity': round(avg_velocity, 1),
                'count': data['total']
            })
    
    # Handle batter heat maps
    if player_type.lower() == 'batter':
        # Initialize zone data for batters
        zone_data = {i: {
            'total': 0,
            'hits': 0,
            'balls_in_play': 0,
            'exit_velocities': [],
            'batting_avg': 0.0,
            'avg_exit_velocity': 0.0,
            'hard_hits': 0,  # Exit velocity > 95 mph
            'medium_hits': 0,  # Exit velocity 85-95 mph
            'weak_hits': 0,  # Exit velocity < 85 mph
            'strikeouts': 0,
            'walks': 0
        } for i in range(len(zones))}
        
        total_batter_events = 0
        
        for p in player_data:
            data = p['data']
            
            # Extract batter data
            plate_x = data.get('PlateLocSide')
            plate_z = data.get('PlateLocHeight')
            exit_velocity = data.get('ExitSpeed')
            play_result = data.get('PlayResult', '')
            pitch_call = data.get('PitchCall', '')
            
            if plate_x is not None and plate_z is not None:
                try:
                    x = float(plate_x)
                    z = float(plate_z)
                    
                    # Find which zone this event belongs to
                    for i, zone in enumerate(zones):
                        if (x >= zone['x'] and x < zone['x'] + zone['w'] and
                            z >= zone['y'] and z < zone['y'] + zone['h']):
                            
                            zone_data[i]['total'] += 1
                            total_batter_events += 1
                            
                            # Track hits and balls in play
                            if play_result in ['Single', 'Double', 'Triple', 'HomeRun']:
                                zone_data[i]['hits'] += 1
                                zone_data[i]['balls_in_play'] += 1
                            elif play_result == 'Out':
                                zone_data[i]['balls_in_play'] += 1
                            
                            # Track exit velocities
                            if exit_velocity and exit_velocity != 'Undefined':
                                try:
                                    ev = float(exit_velocity)
                                    zone_data[i]['exit_velocities'].append(ev)
                                    
                                    # Categorize hit quality
                                    if ev > 95:
                                        zone_data[i]['hard_hits'] += 1
                                    elif ev > 85:
                                        zone_data[i]['medium_hits'] += 1
                                    else:
                                        zone_data[i]['weak_hits'] += 1
                                except (ValueError, TypeError):
                                    pass
                            
                            # Track strikeouts and walks
                            if 'Strikeout' in pitch_call:
                                zone_data[i]['strikeouts'] += 1
                            elif 'Walk' in pitch_call:
                                zone_data[i]['walks'] += 1
                            
                            break
                            
                except (ValueError, TypeError):
                    continue
        
        # Convert zone data to heat map format for batters
        heat_map_data = []
        velocity_heat_map = []
        
        print(f"DEBUG: Total batter events: {total_batter_events}")
        
        for i, zone in enumerate(zones):
            data = zone_data[i]
            
            if data['total'] > 0:
                # Calculate batting average
                batting_avg = (data['hits'] / data['balls_in_play']) if data['balls_in_play'] > 0 else 0
                
                # Calculate average exit velocity
                avg_exit_velocity = sum(data['exit_velocities']) / len(data['exit_velocities']) if data['exit_velocities'] else 0
                
                # Calculate contact quality score (0-1, where 1 is best)
                total_hits = data['hard_hits'] + data['medium_hits'] + data['weak_hits']
                if total_hits > 0:
                    contact_quality = (data['hard_hits'] * 1.0 + data['medium_hits'] * 0.6 + data['weak_hits'] * 0.2) / total_hits
                else:
                    contact_quality = 0
                
                print(f"DEBUG: Batter Zone {i} ({zone['x']:.2f}, {zone['y']:.2f}): {data['total']} events, BA={batting_avg:.3f}, EV={avg_exit_velocity:.1f}, Quality={contact_quality:.3f}")
                
                heat_map_data.append({
                    'x': zone['x'],
                    'y': zone['y'],
                    'count': data['total'],
                    'hits': data['hits'],
                    'balls_in_play': data['balls_in_play'],
                    'batting_avg': round(batting_avg, 3),
                    'contact_quality': round(contact_quality, 3),
                    'hard_hits': data['hard_hits'],
                    'medium_hits': data['medium_hits'],
                    'weak_hits': data['weak_hits']
                })
                
                velocity_heat_map.append({
                    'x': zone['x'],
                    'y': zone['y'],
                    'avg_exit_velocity': round(avg_exit_velocity, 1),
                    'count': data['total']
                })
    
    return {
        "pitch_locations": heat_map_data,
        "velocities": velocity_heat_map,
        "total_pitches": total_pitches if player_type.lower() == 'pitcher' else total_batter_events,
        "strike_zone": {
            "width": 1.0,
            "height": 1.0,
            "center_x": 0.0,
            "center_y": 0.0
        }
    }


@router.get(
    "/development/analysis",
    summary="Get development analysis",
    description="Get comprehensive development analysis for the team including improvement areas and recommendations."
)
async def get_development_analysis(
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """Get development analysis for the team"""
    print("DEBUG: ===== DEVELOPMENT ENDPOINT CALLED =====")
    print(f"DEBUG: Development analysis requested for user: {user.email}, team_id: {user.team_id}")
    try:
        # Get all CSV files for the user's team
        csv_files = db.query(CSVFile).filter(CSVFile.team_id == user.team_id).all()
        print(f"DEBUG: Found {len(csv_files)} CSV files for team")
        
        if not csv_files:
            print("DEBUG: No CSV files found for team")
            raise HTTPException(status_code=404, detail="No data found for team")
        
        # Get user's team name and variations for filtering
        user_team = db.query(Team).filter(Team.id == user.team_id).first()
        team_name = user_team.name if user_team else "Unknown"
        team_variations = get_team_variations(team_name)
        
        print(f"DEBUG: User team_id: {user.team_id}")
        print(f"DEBUG: User team name: {team_name}")
        print(f"DEBUG: Team variations: {team_variations}")
        
        # Collect all data from all files, filtered by team
        all_data = []
        pitchers = set()
        batters = set()
        
        for csv_file in csv_files:
            csv_data = db.query(CSVData).filter(CSVData.csv_file_id == csv_file.id).all()
            for row in csv_data:
                try:
                    data = json.loads(row.data_json)
                    
                    # Check if this data belongs to the user's team
                    pitcher_team = data.get('PitcherTeam')
                    batter_team = data.get('BatterTeam')
                    
                    # Check if pitcher belongs to user's team
                    pitcher_team_match = pitcher_team and any(variation in str(pitcher_team) for variation in team_variations)
                    
                    # Check if batter belongs to user's team
                    batter_team_match = batter_team and any(variation in str(batter_team) for variation in team_variations)
                    
                    # Only include data if it belongs to the user's team
                    if pitcher_team_match or batter_team_match:
                        all_data.append(data)
                        
                        # Track unique players from user's team only
                        if data.get('Pitcher') and data['Pitcher'].lower() not in ['undefined', 'undefine', 'null', ''] and pitcher_team_match:
                            pitchers.add(data['Pitcher'])
                        if data.get('Batter') and data['Batter'].lower() not in ['undefined', 'undefine', 'null', ''] and batter_team_match:
                            batters.add(data['Batter'])
                        
                except (json.JSONDecodeError, KeyError):
                    continue
        
        if not all_data:
            print("DEBUG: No valid data found in CSV files")
            raise HTTPException(status_code=404, detail="No valid data found")
        
        print(f"DEBUG: Processing {len(all_data)} data rows")
        
        # Debug: Check first few rows for ball/strike counts
        print("DEBUG: Sample data for first pitch calculation:")
        for i, row in enumerate(all_data[:5]):
            balls = row.get('Balls', 'N/A')
            strikes = row.get('Strikes', 'N/A')
            pitch_call = row.get('PitchCall', 'N/A')
            print(f"  Row {i}: Balls={balls} (type: {type(balls)}), Strikes={strikes} (type: {type(strikes)}), PitchCall={pitch_call}")
        
        # Calculate team-wide metrics
        team_metrics = calculate_team_metrics(all_data)
        
        # Identify improvement areas using custom team targets
        improvement_areas = identify_improvement_areas(team_metrics, db, user.team_id)
        
        # Get player insights
        player_insights = get_player_insights(all_data, list(pitchers), list(batters))
        
        # Generate practice recommendations
        practice_recommendations = generate_practice_recommendations(improvement_areas)
        
        result = {
            "team_overview": {
                "total_players": len(pitchers) + len(batters),
                "pitchers": len(pitchers),
                "batters": len(batters),
                "overall_improvement_score": calculate_improvement_score(team_metrics),
                "key_areas": [area['metric'] for area in improvement_areas[:3]]
            },
            "improvement_areas": improvement_areas,
            "player_insights": player_insights,
            "practice_recommendations": practice_recommendations
        }
        
        print(f"DEBUG: Returning development analysis with {len(improvement_areas)} improvement areas")
        return result
        
    except Exception as e:
        print(f"Error in development analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating development analysis")


def calculate_team_metrics(data):
    """Calculate team-wide performance metrics"""
    metrics = {
        'total_pitches': 0,
        'total_batters': 0,
        'avg_velocity': 0,
        'avg_spin_rate': 0,
        'strike_percentage': 0,
        'chase_rate': 0,
        'exit_velocity': 0,
        'first_pitch_strike_percentage': 0,
        'walks_per_9': 0,
        'strikeouts_per_9': 0
    }
    
    pitch_velocities = []
    spin_rates = []
    strikes = 0
    balls = 0
    first_pitch_strikes = 0
    first_pitches = 0
    chases = 0
    total_batter_events = 0
    exit_velocities = []
    walks = 0
    strikeouts = 0
    total_innings = 0
    
    for row in data:
        # Pitching metrics
        if row.get('Pitcher') and row.get('RelSpeed'):
            try:
                velocity = float(row['RelSpeed'])
                pitch_velocities.append(velocity)
                metrics['total_pitches'] += 1
            except (ValueError, TypeError):
                pass
        
        if row.get('SpinRate'):
            try:
                spin_rate = float(row['SpinRate'])
                spin_rates.append(spin_rate)
            except (ValueError, TypeError):
                pass
        
        # Strike/ball tracking
        pitch_call = row.get('PitchCall', '')
        if 'Strike' in pitch_call:
            strikes += 1
        elif 'Ball' in pitch_call:
            balls += 1
        
        # First pitch strikes - handle different data formats
        balls_count = row.get('Balls', '0')
        strikes_count = row.get('Strikes', '0')
        
        # Convert to string and check if it's a first pitch (0 balls, 0 strikes)
        if str(balls_count) == '0' and str(strikes_count) == '0':
            first_pitches += 1
            if 'Strike' in pitch_call:
                first_pitch_strikes += 1
        
        # Batting metrics
        if row.get('Batter'):
            total_batter_events += 1
            
            # Chase rate (swinging at balls)
            if 'SwingingStrike' in pitch_call or 'FoulBall' in pitch_call:
                if row.get('PlateLocSide') and row.get('PlateLocHeight'):
                    try:
                        x = float(row['PlateLocSide'])
                        z = float(row['PlateLocHeight'])
                        # Check if pitch was outside zone
                        if abs(x) > 0.85 or z < 1.5 or z > 3.5:
                            chases += 1
                    except (ValueError, TypeError):
                        pass
            
            # Exit velocity
            if row.get('ExitSpeed'):
                try:
                    ev = float(row['ExitSpeed'])
                    exit_velocities.append(ev)
                except (ValueError, TypeError):
                    pass
        
        # Walks and strikeouts
        kor_bb = row.get('KorBB', '')
        if 'Walk' in kor_bb:
            walks += 1
        elif 'Strikeout' in kor_bb:
            strikeouts += 1
        
        # Track innings
        if row.get('Inning'):
            try:
                inning = int(row['Inning'])
                if inning > total_innings:
                    total_innings = inning
            except (ValueError, TypeError):
                pass
    
    # Calculate averages
    if pitch_velocities:
        metrics['avg_velocity'] = sum(pitch_velocities) / len(pitch_velocities)
    if spin_rates:
        metrics['avg_spin_rate'] = sum(spin_rates) / len(spin_rates)
    if strikes + balls > 0:
        metrics['strike_percentage'] = (strikes / (strikes + balls)) * 100
    if total_batter_events > 0:
        metrics['chase_rate'] = (chases / total_batter_events) * 100
    if exit_velocities:
        metrics['exit_velocity'] = sum(exit_velocities) / len(exit_velocities)
    if first_pitches > 0:
        metrics['first_pitch_strike_percentage'] = (first_pitch_strikes / first_pitches) * 100
        print(f"DEBUG: First pitch calculation - first_pitches: {first_pitches}, first_pitch_strikes: {first_pitch_strikes}, percentage: {metrics['first_pitch_strike_percentage']}")
    else:
        print(f"DEBUG: No first pitches found - first_pitches: {first_pitches}, first_pitch_strikes: {first_pitch_strikes}")
    
    # Per 9 innings calculations
    if total_innings > 0:
        innings_factor = 9 / total_innings
        metrics['walks_per_9'] = walks * innings_factor
        metrics['strikeouts_per_9'] = strikeouts * innings_factor
    
    return metrics


def identify_improvement_areas(metrics, db_session=None, team_id=None):
    """Identify areas that need improvement based on metrics"""
    improvement_areas = []
    
    # Default targets (fallback if no custom targets)
    default_targets = {
        'chase_rate': {'target': 22.0, 'priority': 'High', 'description': 'Reducing chase rate will improve on-base percentage', 'lower_is_better': True},
        'strike_percentage': {'target': 70.0, 'priority': 'Medium', 'description': 'Improving command will reduce walks and increase strike percentage', 'lower_is_better': False},
        'exit_velocity': {'target': 88.0, 'priority': 'High', 'description': 'Higher exit velocity correlates with better hitting outcomes', 'lower_is_better': False},
        'avg_spin_rate': {'target': 2300, 'priority': 'Medium', 'description': 'Higher spin rates create more movement and deception', 'lower_is_better': False},
        'first_pitch_strike_percentage': {'target': 65.0, 'priority': 'High', 'description': 'Getting ahead in counts improves overall pitching success', 'lower_is_better': False}
    }
    
    # Try to get custom team targets
    targets = default_targets.copy()
    if db_session and team_id:
        try:
            from app.models.database import TeamMetricTargets
            custom_targets = db_session.query(TeamMetricTargets).filter(
                TeamMetricTargets.team_id == team_id
            ).all()
            
            for custom_target in custom_targets:
                metric_name = custom_target.metric_name
                if metric_name in targets:
                    targets[metric_name] = {
                        'target': custom_target.target_value / 10.0,  # Convert back to decimal
                        'priority': custom_target.priority,
                        'description': custom_target.description,
                        'lower_is_better': bool(custom_target.lower_is_better)
                    }
        except Exception as e:
            print(f"Error loading custom targets: {e}")
            # Fall back to defaults
    
    # Check each metric against targets with proper logic
    for metric, target_info in targets.items():
        current = metrics.get(metric, 0)
        target = target_info['target']
        lower_is_better = target_info.get('lower_is_better', False)
        
        # Determine if improvement is needed
        needs_improvement = False
        if lower_is_better:
            # For metrics where lower is better (like chase rate), flag if current > target
            needs_improvement = current > target
        else:
            # For metrics where higher is better, flag if current < target
            needs_improvement = current < target
        
        if needs_improvement:
            improvement_areas.append({
                'metric': metric.replace('_', ' ').title(),
                'current': round(current, 1),
                'target': target,
                'priority': target_info['priority'],
                'description': target_info['description'],
                'drills': get_drills_for_metric(metric)
            })
    
    # Sort by priority (High, Medium, Low)
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    improvement_areas.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    return improvement_areas[:5]  # Return top 5 areas


def get_drills_for_metric(metric):
    """Get recommended drills for a specific metric"""
    drill_map = {
        'chase_rate': ['Plate discipline drills', 'Zone recognition', 'Two-strike approach'],
        'strike_percentage': ['Bullpen sessions', 'Target practice', 'Mechanical adjustments'],
        'exit_velocity': ['Strength training', 'Bat speed drills', 'Swing mechanics'],
        'avg_spin_rate': ['Grip adjustments', 'Release point work', 'Pitch-specific training'],
        'first_pitch_strike_percentage': ['First pitch mentality', 'Strike zone work', 'Confidence building']
    }
    return drill_map.get(metric, ['General practice', 'Skill development', 'Game simulation'])


def get_player_insights(data, pitchers, batters):
    """Get insights for individual players"""
    insights = []
    
    # Analyze top performers and areas for improvement
    for pitcher in pitchers[:3]:  # Top 3 pitchers
        pitcher_data = [row for row in data if row.get('Pitcher') == pitcher]
        if pitcher_data:
            insight = analyze_player_performance(pitcher_data, pitcher, 'Pitcher')
            if insight:
                insights.append(insight)
    
    for batter in batters[:3]:  # Top 3 batters
        batter_data = [row for row in data if row.get('Batter') == batter]
        if batter_data:
            insight = analyze_player_performance(batter_data, batter, 'Batter')
            if insight:
                insights.append(insight)
    
    return insights


def analyze_player_performance(player_data, player_name, position):
    """Analyze individual player performance"""
    if position == 'Pitcher':
        velocities = []
        strikes = 0
        total_pitches = 0
        first_pitch_strikes = 0
        first_pitches = 0
        spin_rates = []
        
        for row in player_data:
            if row.get('RelSpeed'):
                try:
                    velocities.append(float(row['RelSpeed']))
                except (ValueError, TypeError):
                    pass
            
            if row.get('SpinRate'):
                try:
                    spin_rates.append(float(row['SpinRate']))
                except (ValueError, TypeError):
                    pass
            
            pitch_call = row.get('PitchCall', '')
            if 'Strike' in pitch_call or 'Ball' in pitch_call:
                total_pitches += 1
                if 'Strike' in pitch_call:
                    strikes += 1
            
            # First pitch strikes
            if row.get('Balls') == '0' and row.get('Strikes') == '0':
                first_pitches += 1
                if 'Strike' in pitch_call:
                    first_pitch_strikes += 1
        
        if velocities and total_pitches > 0:
            avg_velocity = sum(velocities) / len(velocities)
            strike_percentage = (strikes / total_pitches) * 100
            first_pitch_strike_pct = (first_pitch_strikes / first_pitches * 100) if first_pitches > 0 else 0
            avg_spin_rate = sum(spin_rates) / len(spin_rates) if spin_rates else 0
            
            # Determine strengths and weaknesses
            strengths = []
            weaknesses = []
            
            if avg_velocity >= 85:
                strengths.append(f'Velocity ({avg_velocity:.1f} mph)')
            elif avg_velocity >= 80:
                strengths.append(f'Good Velocity ({avg_velocity:.1f} mph)')
            else:
                weaknesses.append(f'Velocity ({avg_velocity:.1f} mph)')
            
            if strike_percentage >= 65:
                strengths.append(f'Command ({strike_percentage:.0f}% strikes)')
            else:
                weaknesses.append(f'Command ({strike_percentage:.0f}% strikes)')
            
            if first_pitch_strike_pct >= 60:
                strengths.append(f'First Pitch ({first_pitch_strike_pct:.0f}%)')
            else:
                weaknesses.append(f'First Pitch ({first_pitch_strike_pct:.0f}%)')
            
            if avg_spin_rate >= 2200:
                strengths.append(f'Spin Rate ({avg_spin_rate:.0f} rpm)')
            elif avg_spin_rate > 0:
                weaknesses.append(f'Spin Rate ({avg_spin_rate:.0f} rpm)')
            
            # Choose top strength and improvement area
            top_strength = strengths[0] if strengths else f'Velocity ({avg_velocity:.1f} mph)'
            improvement_area = weaknesses[0] if weaknesses else f'Command ({strike_percentage:.0f}% strikes)'
            
            # Personalized recommendations
            if 'Command' in improvement_area:
                recommendation = 'Focus on mechanical consistency and strike zone command'
            elif 'First Pitch' in improvement_area:
                recommendation = 'Work on getting ahead in counts with first pitch strikes'
            elif 'Velocity' in improvement_area:
                recommendation = 'Focus on strength training and mechanical efficiency'
            elif 'Spin Rate' in improvement_area:
                recommendation = 'Work on grip adjustments and release point consistency'
            else:
                recommendation = 'Continue developing overall pitching skills'
            
            return {
                'name': player_name,
                'position': position,
                'top_strength': top_strength,
                'improvement_area': improvement_area,
                'recommendation': recommendation
            }
    
    elif position == 'Batter':
        exit_velocities = []
        chases = 0
        total_events = 0
        hits = 0
        total_at_bats = 0
        
        for row in player_data:
            if row.get('ExitSpeed'):
                try:
                    exit_velocities.append(float(row['ExitSpeed']))
                except (ValueError, TypeError):
                    pass
            
            # Track hits
            play_result = row.get('PlayResult', '')
            if play_result in ['Single', 'Double', 'Triple', 'HomeRun']:
                hits += 1
            if play_result and play_result != 'Walk':
                total_at_bats += 1
            
            if row.get('PitchCall'):
                total_events += 1
                if 'SwingingStrike' in row['PitchCall'] or 'FoulBall' in row['PitchCall']:
                    if row.get('PlateLocSide') and row.get('PlateLocHeight'):
                        try:
                            x = float(row['PlateLocSide'])
                            z = float(row['PlateLocHeight'])
                            if abs(x) > 0.85 or z < 1.5 or z > 3.5:
                                chases += 1
                        except (ValueError, TypeError):
                            pass
        
        if exit_velocities and total_events > 0:
            avg_exit_velocity = sum(exit_velocities) / len(exit_velocities)
            chase_rate = (chases / total_events) * 100
            
            return {
                'name': player_name,
                'position': position,
                'top_strength': f'Exit Velocity ({avg_exit_velocity:.1f} mph)',
                'improvement_area': f'Chase Rate ({chase_rate:.0f}%)',
                'recommendation': 'Work on plate discipline and zone recognition'
            }
    
    return None


def generate_practice_recommendations(improvement_areas):
    """Generate structured practice recommendations"""
    recommendations = []
    
    # Group by category
    pitching_areas = [area for area in improvement_areas if 'strike' in area['metric'].lower() or 'spin' in area['metric'].lower()]
    hitting_areas = [area for area in improvement_areas if 'chase' in area['metric'].lower() or 'exit' in area['metric'].lower()]
    
    if pitching_areas:
        recommendations.append({
            'category': 'Pitching',
            'focus': 'Command & Control',
            'drills': ['Bullpen sessions with target practice', 'Mechanical video analysis', 'Strike zone visualization drills'],
            'frequency': '3x per week',
            'duration': '45 minutes'
        })
    
    if hitting_areas:
        recommendations.append({
            'category': 'Hitting',
            'focus': 'Plate Discipline',
            'drills': ['Zone recognition drills', 'Two-strike approach practice', 'Pitch recognition training'],
            'frequency': '4x per week',
            'duration': '30 minutes'
        })
    
    return recommendations


def calculate_improvement_score(metrics):
    """Calculate overall improvement score (0-100)"""
    score = 0
    max_score = 0
    
    # Weight different metrics
    weights = {
        'strike_percentage': 20,
        'chase_rate': 25,
        'exit_velocity': 20,
        'avg_spin_rate': 15,
        'first_pitch_strike_percentage': 20
    }
    
    targets = {
        'strike_percentage': 70.0,
        'chase_rate': 22.0,
        'exit_velocity': 88.0,
        'avg_spin_rate': 2300,
        'first_pitch_strike_percentage': 65.0
    }
    
    for metric, weight in weights.items():
        current = metrics.get(metric, 0)
        target = targets.get(metric, 0)
        
        if target > 0:
            # Calculate percentage of target achieved
            if metric == 'chase_rate':  # Lower is better for chase rate
                percentage = max(0, min(100, (target - current) / target * 100))
            else:
                percentage = max(0, min(100, current / target * 100))
            
            score += percentage * weight
            max_score += weight
    
    return round(score / max_score) if max_score > 0 else 0

@router.get(
    "/metric-targets",
    summary="Get team metric targets",
    description="Get all metric targets for the current user's team."
)
async def get_metric_targets(
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """Get all metric targets for the team"""
    try:
        targets = db.query(TeamMetricTargets).filter(
            TeamMetricTargets.team_id == user.team_id
        ).all()
        
        # Convert target values back to decimal (divide by 10)
        result = []
        for target in targets:
            result.append({
                'id': target.id,
                'metric_name': target.metric_name,
                'target_value': target.target_value / 10.0,  # Convert back to decimal
                'priority': target.priority,
                'description': target.description,
                'lower_is_better': bool(target.lower_is_better)
            })
        
        return {"targets": result}
    except Exception as e:
        print(f"Error getting metric targets: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metric targets")

@router.post(
    "/metric-targets",
    summary="Create or update metric target",
    description="Create or update a metric target for the team."
)
async def create_metric_target(
    metric_name: str = Form(...),
    target_value: float = Form(...),
    priority: str = Form("Medium"),
    description: str = Form(""),
    lower_is_better: bool = Form(False),
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """Create or update a metric target"""
    try:
        # Convert target value to integer (multiply by 10 for decimals)
        target_value_int = int(target_value * 10)
        
        # Check if target already exists
        existing_target = db.query(TeamMetricTargets).filter(
            TeamMetricTargets.team_id == user.team_id,
            TeamMetricTargets.metric_name == metric_name
        ).first()
        
        if existing_target:
            # Update existing target
            existing_target.target_value = target_value_int
            existing_target.priority = priority
            existing_target.description = description
            existing_target.lower_is_better = 1 if lower_is_better else 0
            existing_target.updated_at = datetime.utcnow()
        else:
            # Create new target
            new_target = TeamMetricTargets(
                team_id=user.team_id,
                metric_name=metric_name,
                target_value=target_value_int,
                priority=priority,
                description=description,
                lower_is_better=1 if lower_is_better else 0
            )
            db.add(new_target)
        
        db.commit()
        return {"message": "Metric target saved successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error saving metric target: {e}")
        raise HTTPException(status_code=500, detail="Failed to save metric target")

@router.delete(
    "/metric-targets/{target_id}",
    summary="Delete metric target",
    description="Delete a specific metric target."
)
async def delete_metric_target(
    target_id: int,
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """Delete a metric target"""
    try:
        target = db.query(TeamMetricTargets).filter(
            TeamMetricTargets.id == target_id,
            TeamMetricTargets.team_id == user.team_id
        ).first()
        
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        db.delete(target)
        db.commit()
        return {"message": "Target deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting metric target: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete target")

@router.post(
    "/metric-targets/reset-defaults",
    summary="Reset to default targets",
    description="Reset all metric targets to default values for the team."
)
async def reset_default_targets(
    user: User = Depends(require_coach_or_admin),
    db: Session = Depends(get_db)
):
    """Reset all metric targets to defaults"""
    try:
        # Delete existing targets
        db.query(TeamMetricTargets).filter(
            TeamMetricTargets.team_id == user.team_id
        ).delete()
        
        # Default targets (same as in identify_improvement_areas)
        default_targets = [
            {
                'metric_name': 'chase_rate',
                'target_value': 220,  # 22.0 * 10
                'priority': 'High',
                'description': 'Reducing chase rate will improve on-base percentage',
                'lower_is_better': True
            },
            {
                'metric_name': 'strike_percentage',
                'target_value': 700,  # 70.0 * 10
                'priority': 'Medium',
                'description': 'Improving command will reduce walks and increase strike percentage',
                'lower_is_better': False
            },
            {
                'metric_name': 'exit_velocity',
                'target_value': 880,  # 88.0 * 10
                'priority': 'High',
                'description': 'Higher exit velocity correlates with better hitting outcomes',
                'lower_is_better': False
            },
            {
                'metric_name': 'avg_spin_rate',
                'target_value': 2300,
                'priority': 'Medium',
                'description': 'Higher spin rates create more movement and deception',
                'lower_is_better': False
            },
            {
                'metric_name': 'first_pitch_strike_percentage',
                'target_value': 650,  # 65.0 * 10
                'priority': 'High',
                'description': 'Getting ahead in counts improves overall pitching success',
                'lower_is_better': False
            }
        ]
        
        # Create default targets
        for target_data in default_targets:
            new_target = TeamMetricTargets(
                team_id=user.team_id,
                metric_name=target_data['metric_name'],
                target_value=target_data['target_value'],
                priority=target_data['priority'],
                description=target_data['description'],
                lower_is_better=1 if target_data['lower_is_better'] else 0
            )
            db.add(new_target)
        
        db.commit()
        return {"message": "Default targets reset successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error resetting default targets: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset targets")

