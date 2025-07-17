from fastapi import APIRouter, UploadFile, File, HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.core.security import get_current_user, require_coach_or_admin, require_admin
import pandas as pd
import os

router = APIRouter()

# OAuth2 scheme for explicit Swagger token inclusion
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Temp file storage
TEMP_CSV_PATH = "temp_uploaded.csv"
uploaded_df = None  # In-memory store for CSV data


@router.post(
    "/upload",
    summary="Upload CSV (Coach/Admin only)",
    description="Upload a CSV file to process Trackman data. Coach or Admin role required."
)
async def upload_csv(
    file: UploadFile = File(...),
    user: User = Depends(require_coach_or_admin)
):
    """
    Upload a CSV file and save it to TEMP_CSV_PATH.
    Coaches and admins can upload CSVs.
    """
    print(f"DEBUG: Token received in upload_csv: {user}")  # Debug token

    # Check if filename exists and ends with .csv
    if not (hasattr(file, "filename") and str(file.filename).lower().endswith(".csv")):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    # Save file to disk
    contents = await file.read()
    with open(TEMP_CSV_PATH, "wb") as f:
        f.write(contents)

    # Load into pandas DataFrame
    global uploaded_df
    uploaded_df = pd.read_csv(TEMP_CSV_PATH)

    # Extract unique teams for response
    if 'PitcherTeam' in uploaded_df.columns:
        teams = uploaded_df['PitcherTeam'].dropna().unique().tolist()
    else:
        teams = []
    return {"message": "✅ CSV uploaded successfully", "teams": teams}


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