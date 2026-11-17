"""
Production Audio & Millisecond-Accurate Word Boundary Sync Engine.
Streams voiceover directly from Microsoft Neural TTS with boundary="WordBoundary",
extracting millisecond-accurate start/end timestamps for every word and assembling
high-retention Submagic-style 2-3 word dynamic subtitle chunks.
"""

import asyncio
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_AUDIO_DIR = BASE_DIR / "video-app" / "public" / "audio"

# Multi-Character Voice Profiles
VOICE_PROFILES = {
    "narrator": {
        "voice": "en-US-AndrewMultilingualNeural",
        "rate": "+4%",
        "pitch": "+1Hz",
    },
    "toffee": {
        "voice": "en-US-AnaNeural",
        "rate": "+6%",
        "pitch": "+4Hz",
    },
    "father": {
        "voice": "en-US-ChristopherNeural",
        "rate": "-3%",
        "pitch": "-3Hz",
    },
    "character_hero": {
        "voice": "en-US-AnaNeural",
        "rate": "+5%",
        "pitch": "+3Hz",
    },
    "character_guide": {
        "voice": "en-US-ChristopherNeural",
        "rate": "-2%",
        "pitch": "-2Hz",
    },
}

DEFAULT_PROFILE = VOICE_PROFILES["narrator"]


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
        print(f"Notice: ffprobe duration fallback ({e})")
        return 4.0


def build_subtitle_chunks(words: list[dict], max_words_per_chunk: int = 3) -> list[dict]:
    """
    Groups individual words into punchy 2-3 word display chunks (Submagic/Opus Clip style).
    Each chunk displays only 2-3 words at a time with frame-accurate highlight bounds.
    """
    if not words:
        return []

    chunks = []
    for i in range(0, len(words), max_words_per_chunk):
        group = words[i:i + max_words_per_chunk]
        start_f = group[0]["start_frame"]
        end_f = group[-1]["end_frame"]

        chunk_words = []
        for w in group:
            chunk_words.append({
                "word": w["word"].upper(),
                "start_frame": w["start_frame"],
                "end_frame": w["end_frame"],
            })

        chunks.append({
            "chunk_id": len(chunks),
            "text": " ".join(w["word"] for w in group).upper(),
            "start_frame": start_f,
            "end_frame": end_f,
            "words": chunk_words,
        })

    # Extend chunk display until next chunk starts so text doesn't flicker away during micro-pauses
    for i in range(len(chunks) - 1):
        if chunks[i]["end_frame"] < chunks[i + 1]["start_frame"]:
            chunks[i]["end_frame"] = chunks[i + 1]["start_frame"]

    return chunks


async def build_scene_audios(scenes: list[dict]) -> list[dict]:
    """Synthesizes voiceover with exact neural word timestamps and builds punchy subtitle chunks."""
    import edge_tts

    PUBLIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    fps = 30
    total_frames = 0

    for i, scene in enumerate(scenes):
        scene_num = i + 1
        narration = scene["narration"]
        speaker = scene.get("speaker", "narrator")
        profile = VOICE_PROFILES.get(speaker, DEFAULT_PROFILE)

        audio_filename = f"scene_{scene_num}.mp3"
        audio_path = PUBLIC_AUDIO_DIR / audio_filename

        # Stream voiceover with boundary="WordBoundary" for exact neural timestamps
        comm = edge_tts.Communicate(
            narration,
            voice=profile["voice"],
            rate=profile["rate"],
            pitch=profile["pitch"],
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

        # Save audio file
        audio_path.write_bytes(audio_bytes)

        # Measure exact duration
        duration_sec = get_audio_duration(audio_path)
        # 0.5s breathing room between cinematic scenes
        padded_duration = duration_sec + 0.5
        duration_frames = max(90, int(round(padded_duration * fps)))

        # Build viral 2-3 word Submagic subtitle chunks
        subtitle_chunks = build_subtitle_chunks(raw_words, max_words_per_chunk=3)

        scene["audio_url"] = f"audio/{audio_filename}"
        scene["audio_duration_sec"] = round(duration_sec, 2)
        scene["duration_in_frames"] = duration_frames
        scene["words"] = raw_words
        scene["subtitle_chunks"] = subtitle_chunks

        total_frames += duration_frames
        print(f"🎙️ Scene #{scene_num} [{scene.get('speaker_name', speaker)}]: {duration_sec:.2f}s ({duration_frames}f, {len(raw_words)} words, {len(subtitle_chunks)} chunks) -> {audio_filename}")

    # Lock total video length to exactly 1800 frames (60.0s @ 30fps)
    target_total = 1800
    if total_frames < target_total:
        diff = target_total - total_frames
        scenes[-1]["duration_in_frames"] += diff
        # Also extend last chunk's end frame
        if scenes[-1].get("subtitle_chunks"):
            scenes[-1]["subtitle_chunks"][-1]["end_frame"] += diff
        print(f"⏱️ Adjusted final scene by +{diff} frames to lock composition to exactly 60.0s (1800 frames).")
    elif total_frames > target_total:
        scale = target_total / total_frames
        for sc in scenes:
            old_dur = sc["duration_in_frames"]
            sc["duration_in_frames"] = max(90, int(round(old_dur * scale)))
        total_now = sum(s["duration_in_frames"] for s in scenes)
        scenes[-1]["duration_in_frames"] += (target_total - total_now)

    return scenes


def build_scene_audios_sync(scenes: list[dict]) -> list[dict]:
    return asyncio.run(build_scene_audios(scenes))
