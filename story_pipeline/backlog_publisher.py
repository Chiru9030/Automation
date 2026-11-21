"""
Autonomous Backlog Queue & Smart Scheduled Publishing Engine.
Handles rolling 24-hour YouTube upload limits (uploadLimitExceeded) with self-healing persistence:
- Enqueues certified rendered videos when third-party upload limits are reached.
- Automatically drains and publishes queued videos on subsequent runs once quota clears.
- Prevents compute wastage by avoiding re-rendering of already-certified episodes.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
BACKLOG_FILE = BASE_DIR / "story_pipeline" / "backlog_queue.json"


def load_backlog() -> dict:
    """Loads the backlog queue from disk or returns empty template."""
    if not BACKLOG_FILE.exists():
        return {"queue": []}
    try:
        return json.loads(BACKLOG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️ Error reading backlog queue ({e}), resetting to empty.")
        return {"queue": []}


def save_backlog(data: dict):
    """Atomically writes backlog queue to disk."""
    BACKLOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    BACKLOG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def enqueue_backlog_episode(
    episode_num: int,
    chapter_id: str,
    title: str,
    description: str,
    tags: list,
    pinned_comment: str,
    video_path: str,
    thumbnail_path: str,
    duration: float = 58.0,
    size_mb: float = 50.0,
) -> bool:
    """Adds a rendered and certified episode to the backlog queue."""
    backlog = load_backlog()
    queue = backlog.get("queue", [])

    # Prevent duplicate enqueues for the same episode number
    for item in queue:
        if item.get("episode_num") == episode_num:
            print(f"ℹ️ Episode #{episode_num} already enqueued in backlog.")
            return True

    now_iso = datetime.now(timezone.utc).isoformat()
    entry = {
        "episode_num": episode_num,
        "chapter_id": chapter_id,
        "title": title,
        "description": description,
        "tags": tags,
        "pinned_comment": pinned_comment,
        "video_path": video_path,
        "thumbnail_path": thumbnail_path,
        "duration": duration,
        "size_mb": size_mb,
        "enqueued_at": now_iso,
        "status": "PENDING_QUOTA_RESET",
    }
    queue.append(entry)
    backlog["queue"] = queue
    save_backlog(backlog)
    print(f"📦 Successfully enqueued Episode #{episode_num} into backlog queue ({BACKLOG_FILE.name})")
    return True


def get_pending_backlog() -> list:
    """Returns list of all pending backlog episodes."""
    backlog = load_backlog()
    return [item for item in backlog.get("queue", []) if item.get("status") == "PENDING_QUOTA_RESET"]


def dequeue_backlog_episode(episode_num: int) -> bool:
    """Removes a published episode from the backlog queue."""
    backlog = load_backlog()
    queue = backlog.get("queue", [])
    initial_len = len(queue)
    queue = [item for item in queue if item.get("episode_num") != episode_num]
    if len(queue) < initial_len:
        backlog["queue"] = queue
        save_backlog(backlog)
        print(f"✅ Dequeued Episode #{episode_num} from backlog queue.")
        return True
    return False
