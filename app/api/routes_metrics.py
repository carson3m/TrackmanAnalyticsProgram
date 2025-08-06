from fastapi import APIRouter, Security, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.core.security import get_current_user, require_coach_or_admin
from app.models.database import get_db, CSVFile, CSVData
from sqlalchemy.orm import Session
import pandas as pd
import os
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

router = APIRouter()

TEMP_CSV_PATH = "temp_uploaded.csv"

class MetricsRequest(BaseModel):
    team: str
    pitcher: str

class BestOfRequest(BaseModel):
    team: str
    season: str = "all"  # "all" or specific year
    file_ids: list[int] | None = None  # Optional list of file IDs to filter by

class UmpireRequest(BaseModel):
    team: str | None = None
    pitcher: str | None = None

@router.post("/summary")
async def get_metrics(request: MetricsRequest, user: User = Depends(require_coach_or_admin)):
    """
    Calculate metrics for a given team and pitcher.
    """
    from PythonFiles.core.statistics import calculate_whiff_rate, calculate_strike_rate, calculate_zone_rate
    from PythonFiles.core.player_metrics import PlayerMetricsAnalyzer

    if not os.path.exists(TEMP_CSV_PATH):
        raise HTTPException(status_code=404, detail="No CSV uploaded.")

    df = pd.read_csv(TEMP_CSV_PATH)
    filtered_df = df[(df['PitcherTeam'] == request.team) & (df['Pitcher'] == request.pitcher)]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No data for specified team and pitcher.")

    # Ensure filtered_df is a DataFrame, not a Series
    if isinstance(filtered_df, pd.Series):
        filtered_df = filtered_df.to_frame().T

    whiff = calculate_whiff_rate(filtered_df)
    strike = calculate_strike_rate(filtered_df)
    zone = calculate_zone_rate(filtered_df)

    analyzer = PlayerMetricsAnalyzer(filtered_df, request.pitcher)
    per_pitch_df = analyzer.per_pitch_type_metrics_df()

    # Replace NaN values with None for JSON serialization
    per_pitch_df = per_pitch_df.where(pd.notnull(per_pitch_df), None)

    return {
        "whiff_rate": whiff,
        "strike_rate": strike,
        "zone_rate": zone,
        "per_pitch_metrics": per_pitch_df.to_dict(orient="records")
    }

@router.get("/available-teams")
async def get_available_teams(
    user: User = Depends(require_coach_or_admin)
):
    """
    Get all available teams from the CSV data in the database.
    """
    db: Session = next(get_db())
    
    # Handle users without a team_id (admin users)
    if not user.team_id:
        # For admin users, show all CSV files
        query = db.query(CSVFile)
    else:
        # Get CSV files for the user's team
        query = db.query(CSVFile).filter(CSVFile.team_id == user.team_id)
    
    csv_files = query.all()
    if not csv_files:
        return {"teams": []}
    
    file_ids = [file.id for file in csv_files]
    csv_data = db.query(CSVData).filter(CSVData.csv_file_id.in_(file_ids)).all()
    
    if not csv_data:
        return {"teams": []}
    
    # Extract all unique teams from the CSV data
    all_teams = set()
    for record in csv_data:
        import json
        data_dict = json.loads(record.data_json)
        
        # Check for team fields in the data
        if "PitcherTeam" in data_dict and data_dict["PitcherTeam"]:
            all_teams.add(data_dict["PitcherTeam"])
        if "BatterTeam" in data_dict and data_dict["BatterTeam"]:
            all_teams.add(data_dict["BatterTeam"])
        if "Team" in data_dict and data_dict["Team"]:
            all_teams.add(data_dict["Team"])
    
    return {"teams": sorted(list(all_teams))}

@router.post("/best-of")
async def get_best_of_stats(
    request: BestOfRequest,
    user: User = Depends(require_coach_or_admin)
):
    """
    Get "Best of" statistics for a team across different metrics using stored CSV files.
    """
    from datetime import datetime, timedelta
    import pandas as pd
    
    try:
        db: Session = next(get_db())
        
        # Handle users without a team_id (admin users)
        if not user.team_id:
            # For admin users, show all CSV files
            query = db.query(CSVFile)
        else:
            # Get CSV files for the user's team
            query = db.query(CSVFile).filter(CSVFile.team_id == user.team_id)
        
        # Filter by specific file IDs if provided
        if request.file_ids:
            query = query.filter(CSVFile.id.in_(request.file_ids))
        
        # Filter by season if specified
        if request.season != "all":
            query = query.filter(CSVFile.game_date.like(f"{request.season}%"))
        
        csv_files = query.all()
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No CSV files found for the specified criteria.")
        
        # Get CSV data for these files
        file_ids = [file.id for file in csv_files]
        csv_data = db.query(CSVData).filter(CSVData.csv_file_id.in_(file_ids)).all()
        
        if not csv_data:
            raise HTTPException(status_code=404, detail="No CSV data found for the specified files.")
        
        # Convert to DataFrame
        data_list = []
        for record in csv_data:
            import json
            data_dict = json.loads(record.data_json)
            # Add file metadata
            data_dict['csv_file_id'] = record.csv_file_id
            data_dict['uploaded_at'] = record.csv_file.uploaded_at.isoformat() if record.csv_file.uploaded_at else None
            data_dict['game_date'] = record.csv_file.game_date if record.csv_file.game_date else None
            data_list.append(data_dict)
        
        df = pd.DataFrame(data_list)
        
        # Filter by team
        team_pitching = df[df["PitcherTeam"] == request.team]
        team_hitting = df[df["BatterTeam"] == request.team]

        if team_pitching.empty and team_hitting.empty:
            raise HTTPException(status_code=404, detail=f"No data found for team {request.team}")

        def top_unique_by(df, group_col, stat_col, label, top_n=5, include_pitch_details=False):
            if group_col not in df.columns or stat_col not in df.columns:
                return {"label": label, "error": "Column missing", "data": []}

            if include_pitch_details:
                # For break metrics, we want to find the top pitch for each unique player
                # and include pitch details
                df_filtered = df.dropna(subset=[stat_col, group_col])
                if df_filtered.empty:
                    return {"label": label, "data": []}
                
                # Group by player and find the best pitch for each player
                player_best_pitches = df_filtered.groupby(group_col)[stat_col].idxmax()
                
                # Get the top 5 players based on their best pitch
                top_player_indices = []
                for player in player_best_pitches.index:
                    best_pitch_idx = player_best_pitches[player]
                    top_player_indices.append(best_pitch_idx)
                
                # Sort by the stat value and take top 5
                top_pitches = df_filtered.loc[top_player_indices].nlargest(top_n, stat_col)
                
                data = []
                for _, row in top_pitches.iterrows():
                    pitch_details = {
                        "player": row[group_col],
                        "value": round(row[stat_col], 1)
                    }
                    
                    # Add pitch details if available
                    if "AutoPitchType" in row:
                        pitch_details["pitch_type"] = str(row["AutoPitchType"])
                    if "Date" in row:
                        pitch_details["date"] = str(row["Date"])
                    
                    # Calculate pitch count for this pitcher in this game
                    if "Date" in row and "Pitcher" in row:
                        # Filter to same pitcher and same date
                        same_game_pitches = df_filtered[
                            (df_filtered["Pitcher"] == row["Pitcher"]) & 
                            (df_filtered["Date"] == row["Date"])
                        ]
                        # Find the position of this pitch in the sequence
                        pitch_count = len(same_game_pitches[same_game_pitches.index <= row.name]) + 1
                        pitch_details["pitch_no"] = pitch_count
                    
                    # Debug: Print what pitch details were found
                    print(f"DEBUG: Pitch details for {row[group_col]}: pitch_type={pitch_details.get('pitch_type', 'N/A')}, date={pitch_details.get('date', 'N/A')}, pitch_no={pitch_details.get('pitch_no', 'N/A')}")
                    
                    data.append(pitch_details)
            else:
                # Original logic for other metrics
                grouped = (
                    df.dropna(subset=[stat_col, group_col])
                    .groupby(group_col)[stat_col]
                    .max()
                    .reset_index()
                    .sort_values(by=stat_col, ascending=False)
                    .head(top_n)
                )

                data = []
                for _, row in grouped.iterrows():
                    data.append({
                        "player": row[group_col],
                        "value": round(row[stat_col], 1)
                    })
            
            return {"label": label, "data": data}

        # Pitching metrics
        top_spin_rates = top_unique_by(team_pitching, "Pitcher", "SpinRate", "🔥 Top 5 Spin Rates (rpm)")
        top_pitch_speeds = top_unique_by(team_pitching, "Pitcher", "RelSpeed", "⚾ Top 5 Pitch Speeds (mph)")
        
        # Break metrics with pitch details
        top_induced_vertical_break = top_unique_by(team_pitching, "Pitcher", "InducedVertBreak", "📈 Top 5 Induced Vertical Break (in)", include_pitch_details=True)
        
        # Horizontal break - use absolute values
        if "HorzBreak" in team_pitching.columns:
            team_pitching_copy = team_pitching.copy()
            team_pitching_copy["AbsHorzBreak"] = team_pitching_copy["HorzBreak"].abs()
            top_horizontal_break = top_unique_by(team_pitching_copy, "Pitcher", "AbsHorzBreak", "🔄 Top 5 Horizontal Break (in)", include_pitch_details=True)
        else:
            top_horizontal_break = {"label": "🔄 Top 5 Horizontal Break (in)", "error": "Column missing", "data": []}
        
        # Total break - calculate using Pythagorean theorem
        if "InducedVertBreak" in team_pitching.columns and "HorzBreak" in team_pitching.columns:
            team_pitching_copy = team_pitching.copy()
            # Calculate total break using Pythagorean theorem: sqrt(vertical² + horizontal²)
            team_pitching_copy["CalculatedTotalBreak"] = (
                (team_pitching_copy["InducedVertBreak"] ** 2 + team_pitching_copy["HorzBreak"] ** 2) ** 0.5
            )
            top_total_break = top_unique_by(team_pitching_copy, "Pitcher", "CalculatedTotalBreak", "🎯 Top 5 Total Break (in)", include_pitch_details=True)
            
            # Debug: Print available columns and sample data
            print(f"DEBUG: Available columns in team_pitching: {list(team_pitching.columns)}")
            if top_total_break["data"]:
                print(f"DEBUG: Sample total break data: {top_total_break['data'][0]}")
        else:
            print(f"DEBUG: Missing columns. Available: {list(team_pitching.columns)}")
            top_total_break = {"label": "🎯 Top 5 Total Break (in)", "error": "Required columns missing", "data": []}
        
        # Debug: Check what columns are available in hitting data
        print(f"DEBUG: Hitting data columns: {list(team_hitting.columns)}")
        
        # Hitting metrics
        top_exit_velocities = top_unique_by(team_hitting, "Batter", "ExitSpeed", "💥 Top 5 Exit Velocities (mph)")
        
        # Home runs
        home_runs = []
        if "PlayResult" in team_hitting.columns and "Distance" in team_hitting.columns:
            try:
                # Filter for home runs more safely
                play_result = team_hitting['PlayResult']
                distance = team_hitting['Distance']
                import pandas as pd
                if isinstance(play_result, pd.Series) and isinstance(distance, pd.Series):
                    hr_mask = play_result.fillna('').astype(str).str.contains("HomeRun", case=False)
                    distance_mask = distance.notna()
                    hr_df = team_hitting[hr_mask & distance_mask]
                    print(f"DEBUG: Found {len(hr_df)} home runs in data")
                    if isinstance(hr_df, pd.DataFrame) and len(hr_df) > 0:
                        # Sort by distance and get top 5
                        hr_df_sorted = hr_df.sort_values(by="Distance", ascending=False).head(5)
                        for _, row in hr_df_sorted.iterrows():
                            home_runs.append({
                                "player": str(row.get('Batter', 'Unknown')),
                                "value": float(row['Distance']),
                                "unit": "ft"
                            })
                        print(f"DEBUG: Processed {len(home_runs)} home runs")
                    else:
                        print("DEBUG: No home runs found in filtered data")
                else:
                    print("DEBUG: PlayResult or Distance columns are not Series")
            except Exception as e:
                print(f"DEBUG: Error processing home runs: {str(e)}")
                # If there's an error processing home runs, continue without them
                pass
        else:
            print("DEBUG: PlayResult or Distance columns not found in team_hitting data")
    
        home_runs_data = {"label": "🎯 Top 5 Longest Home Runs", "data": home_runs}

        result = {
            "team": request.team,
            "season": request.season,
            "pitching": {
                "top_spin_rate": top_spin_rates,
                "top_velocity": top_pitch_speeds,
                "top_induced_vertical_break": top_induced_vertical_break,
                "top_horizontal_break": top_horizontal_break,
                "top_total_break": top_total_break
            },
            "batting": {
                "top_exit_velocity": top_exit_velocities,
                "top_home_runs": home_runs_data
            }
        }
        print(f"DEBUG: Returning result: {result}")
        return result
    except Exception as e:
        print(f"Error in get_best_of_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/umpire-accuracy")
async def get_umpire_accuracy(
    file: UploadFile = File(...),
    user: User = Depends(require_coach_or_admin)
):
    """
    Get umpire accuracy analysis for all data or filtered by team/pitcher.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No CSV file uploaded.")

    content = await file.read()
    import io
    df = pd.read_csv(io.StringIO(content.decode('utf-8')))
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found in uploaded file.")

    from PythonFiles.core.player_metrics import PlayerMetricsAnalyzer
    
    analyzer = PlayerMetricsAnalyzer(df, name="All Pitches")
    umpire_accuracy = analyzer.umpire_accuracy_string()
    
    # Extract numeric values for frontend display
    lines = umpire_accuracy.split('\n')
    metrics = {}
    for line in lines:
        if ':' in line and not line.startswith('\n'):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            metrics[key] = value
    
    return {
        "accuracy_text": umpire_accuracy,
        "metrics": metrics,
        "filters": {}
    }

@router.post("/umpire-accuracy-plot")
async def umpire_accuracy_plot(
    file: UploadFile = File(...),
    user: User = Depends(require_coach_or_admin)
):
    """
    Generate and return the umpire call accuracy plot as a PNG image.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No CSV file uploaded.")
    import io
    import pandas as pd
    import matplotlib.pyplot as plt
    from PythonFiles.ui.strike_zone_plotter import plot_umpire_calls
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode('utf-8')))
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found in uploaded file.")
    fig, ax = plt.subplots(figsize=(6, 6))
    plot_umpire_calls(df, ax)
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")

@router.get("/download_pdf")
async def download_pdf(team: str, pitcher: str, user: User = Depends(require_coach_or_admin)):
    """
    Generate and download PDF summary for pitcher.
    """
    from PythonFiles.summary.export import export_summary_to_pdf
    from PythonFiles.core.player_metrics import PlayerMetricsAnalyzer

    if not os.path.exists(TEMP_CSV_PATH):
        raise HTTPException(status_code=404, detail="No CSV uploaded.")

    df = pd.read_csv(TEMP_CSV_PATH)
    filtered_df = df[(df['PitcherTeam'] == team) & (df['Pitcher'] == pitcher)]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No data for specified team and pitcher.")

    analyzer = PlayerMetricsAnalyzer(filtered_df, pitcher)
    per_pitch_df = analyzer.per_pitch_type_metrics_df()

    # --- Include the plot functions ---
    def plot_breaks(ax):
        for pitch_type, group in filtered_df.groupby(analyzer.get_pitch_type_column()):
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
        import numpy as np
        group = filtered_df
        if not isinstance(group, pd.DataFrame):
            group = pd.DataFrame(group)
        group = group.dropna(subset=["RelSide", "RelHeight"])
        for pitch_type, group_type in group.groupby(analyzer.get_pitch_type_column()):
            ax.scatter(group_type["RelSide"], group_type["RelHeight"], label=pitch_type)
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

    # --- Pass the plot functions to the exporter ---
    pdf_path = export_summary_to_pdf(
        player_name=pitcher,
        summary_text="Pitcher report",
        plot_funcs=[plot_breaks, plot_release_points],
        metrics_df=per_pitch_df
    )

    return FileResponse(pdf_path, media_type='application/pdf', filename=f"{pitcher}_summary.pdf")

@router.get("/pitches")
async def get_pitch_data(team: str, pitcher: str, user: User = Depends(require_coach_or_admin)):
    """
    Return all pitch-level data for a given team and pitcher for plotting.
    """
    if not os.path.exists(TEMP_CSV_PATH):
        raise HTTPException(status_code=404, detail="No CSV uploaded.")

    df = pd.read_csv(TEMP_CSV_PATH)
    filtered_df = df[(df['PitcherTeam'] == team) & (df['Pitcher'] == pitcher)]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No data for specified team and pitcher.")

    # Ensure filtered_df is a DataFrame
    if not isinstance(filtered_df, pd.DataFrame):
        filtered_df = pd.DataFrame(filtered_df)

    # Select columns needed for plots (add more as needed)
    columns = [
        'Pitcher', 'PitcherTeam', 'PitchType', 'TaggedPitchType', 'AutoPitchType',
        'HorzBreak', 'InducedVertBreak', 'RelSide', 'RelHeight',
        'PitchCall', 'PitchNo', 'Inning', 'VertBreak', 'SpinRate', 'RelSpeed',
    ]
    # Only keep columns that exist in the DataFrame
    columns = [col for col in columns if col in filtered_df.columns]
    
    # Get the data and replace NaN values with None for JSON serialization
    data_for_dict = filtered_df[columns].copy()
    data_for_dict = data_for_dict.where(pd.notnull(data_for_dict), None)
    
    # Convert to list of dictionaries, ensuring no NaN values remain
    pitch_data = []
    for _, row in data_for_dict.iterrows():
        row_dict = {}
        for col in columns:
            value = row[col]
            # Convert NaN, inf, and other problematic values to None
            try:
                if value is None or str(value).lower() in ['nan', 'inf', '-inf']:
                    row_dict[col] = None
                else:
                    row_dict[col] = value
            except:
                row_dict[col] = None
        pitch_data.append(row_dict)
    
    return JSONResponse(content={"pitches": pitch_data})
