import json
from pathlib import Path

DATA_DIR = Path("/app/data")  # Adjust this to your base directory
TRACK_FILE = DATA_DIR / "fetched_data.json"

# Ensure the directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def initialize_tracking():
    """Ensure the tracking file exists and is properly initialized."""
    if not TRACK_FILE.exists():
        with open(TRACK_FILE, "w", encoding="utf-8") as f:
            json.dump({"videos": [], "comments": []}, f)

def add_fetched_video(video_id: str):
    """Add a video ID to the tracking file."""
    initialize_tracking()
    with open(TRACK_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        if video_id not in data["videos"]:
            data["videos"].append(video_id)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

def add_fetched_comments(video_id: str, comments: list):
    """Add comments for a video ID to the tracking file."""
    initialize_tracking()
    with open(TRACK_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        if video_id not in [entry["video_id"] for entry in data["comments"]]:
            data["comments"].append({"video_id": video_id, "comments": comments})
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

def get_fetched_videos():
    """Retrieve the list of already fetched video IDs."""
    initialize_tracking()
    with open(TRACK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["videos"]

def get_fetched_comments(video_id: str):
    """Retrieve comments for a specific video ID."""
    initialize_tracking()
    with open(TRACK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for entry in data["comments"]:
            if entry["video_id"] == video_id:
                return entry["comments"]
        return []
