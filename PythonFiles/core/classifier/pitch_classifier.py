from pathlib import Path
import joblib

_model = joblib.load(Path(__file__).parent / "pitch_classifier_rf_live_trimmed.joblib")

FEATURE_NAMES = [
    "pitch_speed", "zone_speed", "spin_rate", "spin_axis", "tilt",
    "release_extension", "release_height", "release_side",
    "release_vert_angle", "release_horiz_angle",
    "movement_horizontal", "movement_vertical", "induced_vertical",
    "plate_loc_height", "plate_loc_side"
]

def classify_pitch(pitch_dict):
    try:
        pitch_dict["tilt"] = tilt_to_degrees(pitch_dict.get("tilt"))
        row = [pitch_dict.get(feature, None) for feature in FEATURE_NAMES]
        return _model.predict([row])[0]
    except Exception as e:
        print(f"[Trackman] Classification error: {e}")
        return "Unknown"
    
def tilt_to_degrees(tilt_str):
    if isinstance(tilt_str, str) and ":" in tilt_str:
        hour, minute = map(int, tilt_str.split(":"))
        return (hour % 12 + minute / 60.0) * 30  # 360° clock
    return None

