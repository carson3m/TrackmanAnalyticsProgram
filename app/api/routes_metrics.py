from fastapi import APIRouter, Security, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.core.security import get_current_user, require_coach_or_admin
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
    time_period: str = "all"  # "all", "week", "month", etc.

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

@router.post("/best-of")
async def get_best_of_stats(
    files: list[UploadFile] = File(...),
    team: str = Form(...),
    time_period: str = Form("all"),
    user: User = Depends(require_coach_or_admin)
):
    """
    Get "Best of" statistics for a team across different metrics.
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No CSV files uploaded.")

    # Read and concatenate all CSVs
    import io
    import pandas as pd
    dfs = []
    for file in files:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        dfs.append(df)
    if not dfs:
        raise HTTPException(status_code=400, detail="No valid CSV data found.")
    df = pd.concat(dfs, ignore_index=True)

    # Filter by team
    team_pitching = df[df["PitcherTeam"] == team]
    team_hitting = df[df["BatterTeam"] == team]

    if team_pitching.empty and team_hitting.empty:
        raise HTTPException(status_code=404, detail=f"No data found for team {team}")

    def top_unique_by(df, group_col, stat_col, label, top_n=5):
        if group_col not in df.columns or stat_col not in df.columns:
            return {"label": label, "error": "Column missing", "data": []}

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
                if isinstance(hr_df, pd.DataFrame) and len(hr_df) > 0:
                    # Sort by distance and get top 5
                    hr_df_sorted = hr_df.sort_values(by="Distance", ascending=False).head(5)
                    for _, row in hr_df_sorted.iterrows():
                        home_runs.append({
                            "player": str(row.get('Batter', 'Unknown')),
                            "value": float(row['Distance']),
                            "unit": "ft"
                        })
        except Exception as e:
            # If there's an error processing home runs, continue without them
            pass
    
    home_runs_data = {"label": "🎯 Top 5 Longest Home Runs", "data": home_runs}

    return {
        "team": team,
        "time_period": time_period,
        "pitching_stats": [top_spin_rates, top_pitch_speeds],
        "hitting_stats": [top_exit_velocities, home_runs_data]
    }

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
