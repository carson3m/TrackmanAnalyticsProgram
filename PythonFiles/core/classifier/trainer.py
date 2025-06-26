# pitch_classifier_trainer.py
import pandas as pd
import joblib
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Fields available in live JSON that we can use
LIVE_FEATURES = [
    "RelSpeed",           # Release speed
    "SpinRate",           # Spin rate
    "SpinAxis",           # Spin axis
    "RelHeight",          # Release height
    "RelSide",            # Release side
    "Extension",          # Extension
    "VertBreak",          # Vertical break
    "InducedVertBreak",   # Induced vertical break
    "HorzBreak",          # Horizontal break
    "PlateLocHeight",     # Plate height location
    "PlateLocSide",       # Plate side location
    "ZoneSpeed",          # Speed at zone
    "VertApprAngle",      # Vertical approach angle
    "HorzApprAngle",      # Horizontal approach angle
    "ZoneTime"            # Time to zone
]
LABEL_COLUMN = "AutoPitchType"

def load_and_prepare_data(files):
    dfs = []
    for file in files:
        df = pd.read_csv(file)

        # Rename deeply nested JSON-like columns to match flat field names
        df = df.rename(columns={
            "Pitch.Release.Extension": "ReleaseExtension",
            "Pitch.Release.Height": "ReleaseHeight",
            "Pitch.Release.Side": "ReleaseSide",
            "Pitch.Release.VerticalAngle": "ReleaseVertAngle",
            "Pitch.Release.HorizontalAngle": "ReleaseHorizAngle",
            "Pitch.Movement.Horizontal": "MovementHorizontal",
            "Pitch.Movement.Vertical": "MovementVertical",
            "Pitch.Movement.InducedVertical": "InducedVertical",
            "Pitch.Speed": "Speed",
            "Pitch.SpinRate": "SpinRate",
            "Pitch.SpinAxis": "SpinAxis",
            "Pitch.ZoneSpeed": "ZoneSpeed",
            "Pitch.VertApprAngle": "VertApprAngle",
            "Pitch.HorzApprAngle": "HorzApprAngle",
            "AutoPitchType": "AutoPitchType"
        })

        df = df[LIVE_FEATURES + [LABEL_COLUMN]]
        df = df.dropna()
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    return combined


def train_model(data):
    X = data[LIVE_FEATURES]
    y = data[LABEL_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", DecisionTreeClassifier(max_depth=8))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    joblib.dump(pipeline, Path(__file__).parent / "pitch_classifier_rf_live_trimmed.joblib")
    print("✅ Model saved as pitch_classifier_rf_live_trimmed.joblib")


if __name__ == "__main__":
    csv_files = [
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20240709-McBean-1_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20240727-McBean-1_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250610-McBean-Private-2_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250608-McBean-Private-2_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250607-McBean-Private-2_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250606-McBean-Private-1_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250607-McBean-Private-2_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250608-McBean-Private-2_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250601-McBean-Private-1_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250531-McBean-Private-2_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250530-McBean-Private-1_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250528-McBean-Private-1_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250526-McBean-Private-1_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250525-McBean-Private-1_unverified.csv",
        "/Users/carsonmorton/TrackmanDataProgram/TrackmanAnalyticsProgram/data/Potters/20250524-McBean-Private-3_unverified.csv"
    ]
    data = load_and_prepare_data(csv_files)
    train_model(data)
