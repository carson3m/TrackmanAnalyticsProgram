def parse_pitch_message(msg, context_manager):
    try:
        pitch = msg.get("Pitch", {})
        release = pitch.get("Release") or {}
        movement = pitch.get("Movement") or {}
        location = pitch.get("Location") or {}

        return {
            "play_id": msg.get("PlayId"),  # ✅ Include this
            "timestamp": msg.get("Time"),  # ✅ Optional but recommended
            "pitch_speed": pitch.get("Speed"),
            "zone_speed": pitch.get("ZoneSpeed"),
            "spin_rate": pitch.get("SpinRate"),
            "spin_axis": pitch.get("SpinAxis"),
            "tilt": pitch.get("Tilt"),
            "release_extension": release.get("Extension"),
            "release_height": release.get("Height"),
            "release_side": release.get("Side"),
            "release_vert_angle": release.get("VerticalAngle"),
            "release_horiz_angle": release.get("HorizontalAngle"),
            "movement_horizontal": movement.get("Horizontal"),
            "movement_vertical": movement.get("Vertical"),
            "induced_vertical": movement.get("InducedVertical"),
            "plate_loc_height": location.get("Height"),
            "plate_loc_side": location.get("Side"),
            "pitcher": context_manager.pitcher_name
        }
    except Exception as e:
        print(f"[LiveParser] ⚠️ Error parsing pitch: {e}")
        return None
