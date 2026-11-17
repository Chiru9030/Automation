"""
Continuous 5-Hour Story-to-Shorts Automation Daemon.
Protected with Circuit Breakers & Non-Blocking Error Handling.
Every 5 hours, it:
1. Synthesizes a new viral story chapter.
2. Generates 3D Pixar visuals and neural voiceovers.
3. Renders a 60-second vertical MP4.
4. Generates a high-CTR thumbnail.
5. Publishes to YouTube Shorts and Instagram Reels.
6. Updates episode history.
7. Sleeps for 5 hours and repeats!
"""

import argparse
import datetime
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from story_runner import process_next_story

DEFAULT_INTERVAL_HOURS = 5.0
MAX_CONSECUTIVE_FAILURES = 3
COOLDOWN_ON_ERROR_SECONDS = 600  # 10 minutes


def run_continuous_daemon(interval_hours: float = DEFAULT_INTERVAL_HOURS):
    interval_seconds = int(interval_hours * 3600)

    print("=============================================================")
    print(f" ⏳ Continuous Story-to-Shorts Daemon Initialized ")
    print(f" Cadence: Every {interval_hours} hours ({interval_seconds} seconds)")
    print(" Watching folder: books/")
    print(" Safety: Circuit breaker active (Max retries: 2, Timeout: 360s)")
    print("=============================================================")

    iteration = 0
    consecutive_failures = 0

    while True:
        iteration += 1
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[Cycle #{iteration} - {now_str}] Executing story video pipeline...")

        try:
            result = process_next_story()
            status = result.get("status")
            print(f"[Cycle #{iteration} Status]: {status}")

            if status == "SUCCESS":
                consecutive_failures = 0
            elif status == "NO_NEW_STORIES":
                print("ℹ️ Waiting for new book upload in 'books/'.")
            else:
                consecutive_failures += 1
                print(f"⚠️ Cycle encountered non-fatal failure ({status}). Failure count: {consecutive_failures}")

        except Exception as e:
            consecutive_failures += 1
            print(f"❌ [Cycle #{iteration} Exception]: {e}")

        # Check circuit breaker
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            print(f"\n🛑 CIRCUIT BREAKER TRIGGERED: {MAX_CONSECUTIVE_FAILURES} consecutive failures.")
            print(f"Pausing for {COOLDOWN_ON_ERROR_SECONDS // 60} minutes cooldown before resetting...")
            time.sleep(COOLDOWN_ON_ERROR_SECONDS)
            consecutive_failures = 0
            continue

        next_run_dt = datetime.datetime.now() + datetime.timedelta(seconds=interval_seconds)
        print(f"\n💤 Sleeping for {interval_hours} hours...")
        print(f"📅 Next scheduled story production: {next_run_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Tip: Drop new PDF or TXT story books into 'books/' anytime!\n")

        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n🛑 Continuous scheduler stopped by user.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Continuous 8-Hour Story-to-Shorts Publisher")
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL_HOURS,
        help="Cadence in hours (default: 8.0)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run once immediately without entering the 8-hour sleep loop",
    )
    args = parser.parse_args()

    if args.test:
        print("Running single test cycle...")
        process_next_story()
    else:
        run_continuous_daemon(interval_hours=args.interval)
