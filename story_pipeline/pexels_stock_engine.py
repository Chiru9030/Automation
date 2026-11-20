"""
Pexels Free Stock Video & B-Roll Integration Engine.
Fetches high-definition vertical (9:16) stock video clips via the free Pexels API (200 req/hr, 20,000 req/mo).
Provides real cinematic motion for opening hooks and rapid cuts (2-4 seconds).
"""

import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STOCK_CACHE_DIR = BASE_DIR / "video-app" / "public" / "stock_videos"


def fetch_pexels_vertical_video(query: str, min_duration: int = 3, target_path: Path = None) -> Path | None:
    """
    Searches Pexels for a vertical 1080x1920 video clip matching the query.
    Downloads the optimal 1080p MP4 file.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        return None

    STOCK_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if target_path and target_path.exists() and target_path.stat().st_size > 50_000:
        return target_path

    try:
        clean_query = urllib.parse.quote(query[:40])
        url = f"https://api.pexels.com/videos/search?query={clean_query}&orientation=portrait&size=medium&per_page=3"
        req = urllib.request.Request(url, headers={"Authorization": api_key, "User-Agent": "AutonomousStoryPipeline/2.1"})

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        videos = data.get("videos", [])
        if not videos:
            return None

        # Find best 1080x1920 or portrait file
        best_file_url = None
        for vid in videos:
            files = vid.get("video_files", [])
            for f in files:
                w, h = f.get("width", 0), f.get("height", 0)
                if h > w and f.get("link"):  # Vertical portrait
                    best_file_url = f.get("link")
                    break
            if best_file_url:
                break

        if not best_file_url:
            return None

        out_path = target_path or (STOCK_CACHE_DIR / f"pexels_{abs(hash(query)) % 100000}.mp4")
        urllib.request.urlretrieve(best_file_url, str(out_path))
        if out_path.exists() and out_path.stat().st_size > 50_000:
            print(f"🎬 [Pexels Engine] Downloaded vertical B-roll: {out_path.name} for '{query}'")
            return out_path
    except Exception as e:
        print(f"Notice: Pexels stock video lookup skipped ({e})")

    return None
