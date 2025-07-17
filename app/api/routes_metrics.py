from fastapi import APIRouter, Security, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.core.security import get_current_user, require_coach_or_admin
import pandas as pd
import os
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

router = APIRouter()

TEMP_CSV_PATH = "temp_uploaded.csv"

class MetricsRequest(BaseModel):
    team: str
    pitcher: str

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

    return {
        "whiff_rate": whiff,
        "strike_rate": strike,
        "zone_rate": zone,
        "per_pitch_metrics": per_pitch_df.to_dict(orient="records")
    }

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
        ax.legend()
        ax.grid(True)

    def plot_release_points(ax):
        for pitch_type, group in filtered_df.groupby(analyzer.get_pitch_type_column()):
            ax.scatter(group["RelSide"], group["RelHeight"], label=pitch_type)
        ax.set_xlabel("Horizontal Release Side (ft)")
        ax.set_ylabel("Vertical Release Height (ft)")
        ax.set_title("Release Points")
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

    # Select columns needed for plots (add more as needed)
    columns = [
        'Pitcher', 'PitcherTeam', 'PitchType', 'TaggedPitchType', 'AutoPitchType',
        'HorzBreak', 'InducedVertBreak', 'RelSide', 'RelHeight',
        'PitchCall', 'PitchNo', 'Inning', 'VertBreak', 'SpinRate', 'RelSpeed',
    ]
    # Only keep columns that exist in the DataFrame
    columns = [col for col in columns if col in filtered_df.columns]
    pitch_data = filtered_df[columns].to_dict(orient="records")
    return JSONResponse(content={"pitches": pitch_data})
