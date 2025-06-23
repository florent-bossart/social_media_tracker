import sys
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone


from .youtube import fetch_video_comments
from .youtube_quota import quota

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

QUOTA_BUFFER = 5  # Reduced buffer from 10 to 5 for maximum quota usage
MAX_VIDEOS_PER_BATCH = 10  # Limit videos per batch to prevent long execution
INDIVIDUAL_VIDEO_TIMEOUT = 30  # Timeout per video in seconds

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

def safe_fetch_video_comments(video_id, timeout=INDIVIDUAL_VIDEO_TIMEOUT):
    """Safely fetch video comments with timeout and error handling."""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Video {video_id} timed out after {timeout} seconds")

    # Set timeout alarm (Unix only)
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        start_time = time.time()
        logger.info(f"Fetching comments for video: {video_id}")

        result = fetch_video_comments(video_id)

        elapsed = time.time() - start_time
        logger.info(f"Video {video_id} completed in {elapsed:.2f}s - {len(result) if result else 0} new comments")

        signal.alarm(0)  # Cancel alarm
        return result

    except TimeoutError as e:
        logger.warning(f"Timeout for video {video_id}: {e}")
        raise RuntimeError(f"timeout: {e}")
    except Exception as e:
        logger.warning(f"Error for video {video_id}: {e}")
        raise
    finally:
        signal.alarm(0)  # Ensure alarm is cancelled

def update_comments_from_fetched_rotating():
    logger.info("Starting YouTube comments rotation update")

    video_ids = load_video_ids(DATA_FILE)
    n_videos = len(video_ids)
    if n_videos == 0:
        logger.error("No video IDs found in data file")
        return {"error": "No video IDs found"}

    current_position = load_rotation_state(ROTATION_STATE_FILE)
    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    updates = []
    results = []

    start_position = current_position
    processed = 0
    max_process = min(MAX_VIDEOS_PER_BATCH, n_videos)

    logger.info(f"Processing up to {max_process} videos starting from position {current_position}")
    logger.info(f"Available quota: {quota.remaining()}")

    start_time = time.time()

    while quota.remaining() > QUOTA_BUFFER and processed < max_process:
        video_id = video_ids[current_position]
        video_start_time = time.time()

        try:
            new_comments = safe_fetch_video_comments(video_id)
            n = len(new_comments) if new_comments else 0
            results.append({"video_id": video_id, "new_comments": n, "status": "success"})
            if new_comments:
                for comment in new_comments:
                    updates.append({"video_id": video_id, **comment})

        except RuntimeError as e:
            # Now these can be 'videoNotFound', 'commentsDisabled', 'timeout', etc
            error_msg = str(e)
            logger.warning(f"RuntimeError for video {video_id}: {error_msg}")
            results.append({"video_id": video_id, "error": error_msg, "status": "failed"})

        except Exception as e:
            error_msg = f"unknown: {str(e)}"
            logger.error(f"Unexpected error for video {video_id}: {error_msg}")
            results.append({"video_id": video_id, "error": error_msg, "status": "failed"})

        current_position = (current_position + 1) % n_videos
        processed += 1

        video_elapsed = time.time() - video_start_time
        logger.info(f"Processed video {processed}/{max_process} (ID: {video_id}) in {video_elapsed:.2f}s")

        if not quota.can_use(1):  # 1 is the minimal cost for a comment request
            logger.warning("Quota exhausted, stopping processing")
            break

    total_elapsed = time.time() - start_time
    save_rotation_state(ROTATION_STATE_FILE, current_position)

    logger.info(f"Batch completed in {total_elapsed:.2f}s. Processed {processed} videos, found {len(updates)} new comments")
    logger.info(f"Next batch will start from position {current_position}")

    if updates:
        output_path = OUTPUT_DIR / f"new_comments_{fetch_date}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(updates, f, ensure_ascii=False, indent=2)
        output_file = str(output_path)
        logger.info(f"Saved {len(updates)} new comments to {output_file}")
    else:
        output_file = None
        logger.info("No new comments found")

    return {
        "summary": results,
        "output_file": output_file,
        "total_new_comments": len(updates),
        "videos_processed": processed,
        "next_position": current_position,
        "quota_remaining": quota.remaining(),
        "execution_time_seconds": round(total_elapsed, 2),
        "batch_size": max_process
    }

if __name__ == "__main__":
    result = update_comments_from_fetched_rotating()
    print(json.dumps(result, indent=2, ensure_ascii=False))
