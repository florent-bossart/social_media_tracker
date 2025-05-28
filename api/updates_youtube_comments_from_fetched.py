import sys
import json
from pathlib import Path
from datetime import datetime, timezone


from .youtube import fetch_video_comments
from .youtube_quota import quota

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
YOUTUBE_ROOT = DATA_ROOT / "youtube"
COMMENT_UPDATES_ROOT = YOUTUBE_ROOT / "comment_updates"

# Ensure all necessary directories exist
DATA_ROOT.mkdir(parents=True, exist_ok=True)
YOUTUBE_ROOT.mkdir(parents=True, exist_ok=True)
COMMENT_UPDATES_ROOT.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_ROOT / "fetched_data.json"
ROTATION_STATE_FILE = YOUTUBE_ROOT / "comments_rotation_position.json"
OUTPUT_DIR = COMMENT_UPDATES_ROOT

QUOTA_BUFFER = 10  # stop with 10 quota left as a safety buffer

def load_video_ids(data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "videos" in data and isinstance(data["videos"], list):
        return data["videos"]
    else:
        raise ValueError("fetched_data.json must contain a 'videos' key with a list of video IDs")

def load_rotation_state(state_file):
    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("position", 0)
    return 0

def save_rotation_state(state_file, position):
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump({"position": position}, f)

def update_comments_from_fetched_rotating():
    video_ids = load_video_ids(DATA_FILE)
    n_videos = len(video_ids)
    if n_videos == 0:
        return {"error": "No video IDs found"}

    current_position = load_rotation_state(ROTATION_STATE_FILE)
    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    updates = []
    results = []

    start_position = current_position
    processed = 0

    while quota.remaining() > QUOTA_BUFFER and processed < n_videos:
        video_id = video_ids[current_position]
        try:
            new_comments = fetch_video_comments(video_id)
            n = len(new_comments) if new_comments else 0
            results.append({"video_id": video_id, "new_comments": n})
            if new_comments:
                for comment in new_comments:
                    updates.append({"video_id": video_id, **comment})
        except RuntimeError as e:
            # Now these can be 'videoNotFound', 'commentsDisabled', etc
            results.append({"video_id": video_id, "error": str(e)})
        except Exception as e:
            results.append({"video_id": video_id, "error": f"unknown: {str(e)}"})

        current_position = (current_position + 1) % n_videos
        processed += 1

        if not quota.can_use(1):  # 1 is the minimal cost for a comment request
            break

    save_rotation_state(ROTATION_STATE_FILE, current_position)

    if updates:
        output_path = OUTPUT_DIR / f"new_comments_{fetch_date}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(updates, f, ensure_ascii=False, indent=2)
        output_file = str(output_path)
    else:
        output_file = None

    return {
        "summary": results,
        "output_file": output_file,
        "total_new_comments": len(updates),
        "next_position": current_position,
        "quota_remaining": quota.remaining()
    }

if __name__ == "__main__":
    result = update_comments_from_fetched_rotating()
    print(json.dumps(result, indent=2, ensure_ascii=False))
