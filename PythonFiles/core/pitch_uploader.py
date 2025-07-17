# pitch_uploader.py
import requests

def upload_pitch(pitch):
    try:
        res = requests.post("http://127.0.0.1:5050/api/pitches", json=pitch)
        if res.status_code != 200:
            print(f"[Uploader] ❌ Failed to upload pitch: {res.text}")
    except Exception as e:
        print(f"[Uploader] 🚨 Error sending pitch: {e}")
