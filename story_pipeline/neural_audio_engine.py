"""
Stage 4 & 5: Neural Audio & Exact Frame Synchronization Engine.
Synthesizes cinema-grade multi-character voiceovers with boundary="WordBoundary".
Extracts exact millisecond neural word timings and locks total duration strictly to 58.0s (1740 frames @ 30fps).
"""

import asyncio
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_AUDIO_DIR = BASE_DIR / "video-app" / "public" / "audio"

VOICE_MAP = {
    "narrator": {"voice": "en-US-ChristopherNeural", "rate": "+4%", "pitch": "+0Hz"},
    "character_hero": {"voice": "en-US-GuyNeural", "rate": "+5%", "pitch": "+0Hz"},
    "character_guide": {"voice": "en-US-EricNeural", "rate": "+0%", "pitch": "+0Hz"},
}


def get_audio_duration(file_path: Path) -> float:
    """Gets audio duration in seconds using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        return 4.0


async def synthesize_beat_audios(beats: list[dict]) -> list[dict]:
    """Generates voiceover for each beat with exact neural word timestamps."""
    import edge_tts

    PUBLIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    fps = 30
    total_frames = 0

    for i, beat in enumerate(beats):
        b_num = beat["beat_number"]
        narration = beat["narration"]
        speaker = beat.get("speaker", "narrator")
        cfg = VOICE_MAP.get(speaker, VOICE_MAP["narrator"])

        audio_filename = f"beat_{b_num}.mp3"
        audio_path = PUBLIC_AUDIO_DIR / audio_filename

        audio_bytes = bytearray()
        raw_words = []

        try:
            comm = edge_tts.Communicate(
                narration,
                voice=cfg["voice"],
                rate=cfg["rate"],
                pitch=cfg["pitch"],
                boundary="WordBoundary",
            )
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start_sec = chunk["offset"] / 10_000_000
                    duration_sec = chunk["duration"] / 10_000_000
                    end_sec = start_sec + duration_sec
                    raw_words.append({
                        "word": chunk["text"],
                        "start_sec": start_sec,
                        "end_sec": end_sec,
                        "start_frame": max(0, int(round(start_sec * fps))),
                        "end_frame": max(1, int(round(end_sec * fps))),
                    })
        except Exception as e_tts:
            print(f"⚠️ TTS notice on {cfg['voice']} ({e_tts}), retrying with default neural voice...")
            comm = edge_tts.Communicate(
                narration,
                voice="en-US-GuyNeural",
                boundary="WordBoundary",
            )
            audio_bytes = bytearray()
            raw_words = []
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start_sec = chunk["offset"] / 10_000_000
                    duration_sec = chunk["duration"] / 10_000_000
                    end_sec = start_sec + duration_sec
                    raw_words.append({
                        "word": chunk["text"],
                        "start_sec": start_sec,
                        "end_sec": end_sec,
                        "start_frame": max(0, int(round(start_sec * fps))),
                        "end_frame": max(1, int(round(end_sec * fps))),
                    })

        audio_path.write_bytes(audio_bytes)
        dur_sec = get_audio_duration(audio_path)

        # Fallback word timestamps if boundaries missing
        if not raw_words:
            words_list = narration.split()
            step = dur_sec / max(1, len(words_list))
            for idx, w in enumerate(words_list):
                s_s = idx * step
                e_s = (idx + 1) * step
                raw_words.append({
                    "word": w,
                    "start_sec": s_s,
                    "end_sec": e_s,
                    "start_frame": max(0, int(round(s_s * fps))),
                    "end_frame": max(1, int(round(e_s * fps))),
                })

        # Padding between beats: 0.4s
        dur_frames = max(60, int(round((dur_sec + 0.40) * fps)))

        beat["audio_url"] = f"audio/{audio_filename}"
        beat["audio_duration_sec"] = round(dur_sec, 2)
        beat["duration_in_frames"] = dur_frames
        beat["words"] = raw_words

        total_frames += dur_frames
        print(f"🎙️ [Stage 4/5: Audio Engine] Beat #{b_num} [{beat.get('speaker_name', speaker)}]: {dur_sec:.2f}s ({dur_frames}f, {len(raw_words)} words) -> {audio_filename}")

    # Lock composition to strictly 1740 frames (58.0 seconds @ 30fps)
    target_frames = 1740  # 58.0s (strictly < 59s limit)
    if total_frames < target_frames:
        diff = target_frames - total_frames
        beats[-1]["duration_in_frames"] += diff
        print(f"⏱️ Adjusted final beat by +{diff} frames to lock total duration to strictly 58.0s (1740 frames).")
    elif total_frames > target_frames:
        scale = target_frames / total_frames
        for b in beats:
            b["duration_in_frames"] = max(60, int(round(b["duration_in_frames"] * scale)))
        now_total = sum(b["duration_in_frames"] for b in beats)
        beats[-1]["duration_in_frames"] += (target_frames - now_total)

    return beats


def build_audio_and_timings_sync(beats: list[dict]) -> list[dict]:
    return asyncio.run(synthesize_beat_audios(beats))
