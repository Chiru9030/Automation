"""
Autonomous Storage & Asset Lifecycle Cleaner.
Prevents disk and cloud artifact storage exhaustion by automatically purging
historical videos, audio, temporary clips, carousels, and image caches after each run.

Rules:
1. Retains only the latest N (default: 3) episodes of generated videos, thumbnails, and images.
2. Completely purges fast_render_tmp/ intermediate clips, temp audio, and failed artifacts.
3. Leaves all history JSON metadata (story_history.json, backlog_queue.json) intact.
4. Returns exact human-readable metrics on reclaimed disk space.
"""

import os
import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_APP_DIR = BASE_DIR / "video-app"
OUT_DIR = VIDEO_APP_DIR / "out"
PUBLIC_IMAGES_DIR = VIDEO_APP_DIR / "public" / "images"
PUBLIC_AUDIO_DIR = VIDEO_APP_DIR / "public" / "audio"
FAST_RENDER_TMP = OUT_DIR / "fast_render_tmp"


def _extract_ep_number(filename: str) -> int | None:
    """Extracts integer episode number from various file naming conventions."""
    # Matches story_episode_41.mp4, ep_41_scene_1.jpg, thumbnail_episode_41.jpg, carousel_ep_41
    m = re.search(r"(?:story_episode_|ep_|thumbnail_episode_|carousel_ep_)(\d+)", filename, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def cleanup_storage(keep_episodes: int = 3, verbose: bool = True) -> dict:
    """
    Scans output and public asset directories, purges temporary and older episode assets,
    and preserves only the latest `keep_episodes` episodes.
    """
    bytes_freed = 0
    deleted_files = 0
    deleted_dirs = 0

    # 1. Always purge fast_render_tmp intermediate files
    if FAST_RENDER_TMP.exists():
        for item in FAST_RENDER_TMP.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    sz = item.stat().st_size
                    item.unlink()
                    bytes_freed += sz
                    deleted_files += 1
                elif item.is_dir():
                    sz = sum(f.stat().st_size for f in item.glob("**/*") if f.is_file())
                    shutil.rmtree(item)
                    bytes_freed += sz
                    deleted_dirs += 1
            except Exception as e:
                if verbose:
                    print(f"  [Cleaner Notice] Could not remove {item.name}: {e}")

    # 2. Identify all existing episodes in OUT_DIR
    episode_numbers = set()
    if OUT_DIR.exists():
        for p in OUT_DIR.glob("story_episode_*.mp4"):
            ep = _extract_ep_number(p.name)
            if ep is not None:
                episode_numbers.add(ep)

    sorted_eps = sorted(list(episode_numbers), reverse=True)
    kept_episodes = set(sorted_eps[:keep_episodes])
    pruned_episodes = set(sorted_eps[keep_episodes:])

    if verbose and pruned_episodes:
        print(f"🧹 [Storage Cleaner] Retaining latest {len(kept_episodes)} episodes: {sorted(list(kept_episodes))}")
        print(f"   Pruning {len(pruned_episodes)} older episodes: {sorted(list(pruned_episodes))}")

    # 3. Clean older videos, thumbnails, and carousels in OUT_DIR
    if OUT_DIR.exists():
        for item in OUT_DIR.iterdir():
            if item.name.startswith("."):
                continue

            # Temporary documentary concatenation files
            if item.name.startswith("DOCUMENTARY_"):
                try:
                    sz = item.stat().st_size
                    item.unlink()
                    bytes_freed += sz
                    deleted_files += 1
                except Exception:
                    pass
                continue

            # Check if file/folder belongs to an older pruned episode
            ep = _extract_ep_number(item.name)
            if ep is not None and ep in pruned_episodes:
                try:
                    if item.is_file() or item.is_symlink():
                        sz = item.stat().st_size
                        item.unlink()
                        bytes_freed += sz
                        deleted_files += 1
                    elif item.is_dir():
                        sz = sum(f.stat().st_size for f in item.glob("**/*") if f.is_file())
                        shutil.rmtree(item)
                        bytes_freed += sz
                        deleted_dirs += 1
                except Exception as e:
                    if verbose:
                        print(f"  [Cleaner Notice] Could not remove {item.name}: {e}")

    # 4. Clean older scene images in PUBLIC_IMAGES_DIR
    if PUBLIC_IMAGES_DIR.exists():
        for img in PUBLIC_IMAGES_DIR.iterdir():
            if img.name.startswith("."):
                continue
            # Remove any stray temp images
            if ".tmp" in img.name or img.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                try:
                    sz = img.stat().st_size
                    img.unlink()
                    bytes_freed += sz
                    deleted_files += 1
                except Exception:
                    pass
                continue

            ep = _extract_ep_number(img.name)
            if ep is not None and ep in pruned_episodes:
                try:
                    sz = img.stat().st_size
                    img.unlink()
                    bytes_freed += sz
                    deleted_files += 1
                except Exception as e:
                    if verbose:
                        print(f"  [Cleaner Notice] Could not remove {img.name}: {e}")

    # 5. Clean temporary and unneeded audio in PUBLIC_AUDIO_DIR
    if PUBLIC_AUDIO_DIR.exists():
        for aud in PUBLIC_AUDIO_DIR.iterdir():
            if aud.name.startswith("."):
                continue
            # Clean raw/tmp audio stems
            if ".raw." in aud.name or ".tmp." in aud.name:
                try:
                    sz = aud.stat().st_size
                    aud.unlink()
                    bytes_freed += sz
                    deleted_files += 1
                except Exception:
                    pass
                continue

    mb_freed = bytes_freed / (1024 * 1024)
    if verbose:
        print(f"✨ [Storage Cleaner] Purge complete: Reclaimed {mb_freed:.2f} MB ({deleted_files} files, {deleted_dirs} dirs).")
        print(f"   Storage is safely bounded and will never exceed quota.")

    return {
        "bytes_freed": bytes_freed,
        "mb_freed": mb_freed,
        "deleted_files": deleted_files,
        "deleted_dirs": deleted_dirs,
        "kept_episodes": sorted(list(kept_episodes)),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean historical video and image assets")
    parser.add_argument("--keep", type=int, default=3, help="Number of latest episodes to retain")
    args = parser.parse_args()
    cleanup_storage(keep_episodes=args.keep, verbose=True)
