import socket
import json
from datetime import datetime, timezone
import uuid

def send_simulated_trackman_broadcast(host="192.168.68.103", port=20998):
    now_utc = datetime.now(timezone.utc).isoformat()

    packet = {
        "Time": now_utc,
        "SessionId": str(uuid.uuid4()),
        "PlayId": str(uuid.uuid4()),
        "Version": "1.1.0",
        "TrackId": str(uuid.uuid4()),
        "TrackStartTime": now_utc,
        "Kind": "Pitch",
        "Pitch": {
            "TrackStartTime": now_utc,
            "Speed": 87.15,
            "SpinRate": 2577.89,
            "Tilt": "1:30",
            "ZoneSpeed": 79.94,
            "SpinAxis": 227.67,
            "VertApprAngle": -6.09,
            "HorzApprAngle": -0.06,
            "Location": {
                "X": 1.416667,
                "Y": 2.151739,
                "Z": -0.56939,
                "Time": 0.437969,
                "Height": 2.15174,
                "Side": 0.56939,
                "Speed": 79.93653
            },
            "Release": {
                "Extension": 5.689,
                "VerticalAngle": -1.826,
                "HorizontalAngle": -2.610,
                "Height": 5.763,
                "Side": 1.815
            },
            "Movement": {
                "Horizontal": 14.264,
                "Vertical": -22.880,
                "InducedVertical": 14.149
            },
            "NineP": {
                "Pfxx": -8.015,
                "Pfxz": 8.046,
                "X0": {"X": -1.605, "Y": 50.0, "Z": 5.595},
                "V0": {"X": 5.176, "Y": -126.466, "Z": -4.781},
                "A0": {"X": -13.009, "Y": 25.244, "Z": -19.114}
            }
        },
        "Hit": None,
        "CatcherThrow": None
    }

    message = json.dumps(packet).encode('utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(message, ("192.168.1.102", 20998))

    print("✅ Simulated TrackMan packet sent to port 20998.")

if __name__ == "__main__":
    send_simulated_trackman_broadcast()
