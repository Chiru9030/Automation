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

# 8 Rotating Multi-Accent Character Suites (Defeats YouTube Inauthentic/Repetitive Audio Profile Detection)
VOICE_SUITES = [
    {
        "anchor": {"voice": "en-US-ChristopherNeural", "rate": "+2%", "pitch": "-3Hz", "name": "Deep Anchor (US)"},
        "analyst": {"voice": "en-US-EricNeural", "rate": "+3%", "pitch": "+0Hz", "name": "Science Specialist (US)"}
    },
    {
        "anchor": {"voice": "en-US-JennyNeural", "rate": "+3%", "pitch": "+0Hz", "name": "Investigative Host (US)"},
        "analyst": {"voice": "en-GB-RyanNeural", "rate": "+2%", "pitch": "-2Hz", "name": "British Academic (GB)"}
    },
    {
        "anchor": {"voice": "en-US-GuyNeural", "rate": "+4%", "pitch": "+0Hz", "name": "Curiosity Narrator (US)"},
        "analyst": {"voice": "en-US-AriaNeural", "rate": "+2%", "pitch": "+1Hz", "name": "Analyst (US)"}
    },
    {
        "anchor": {"voice": "en-US-AndrewNeural", "rate": "+3%", "pitch": "-1Hz", "name": "Dynamic Explainer (US)"},
        "analyst": {"voice": "en-US-AvaNeural", "rate": "+3%", "pitch": "+1Hz", "name": "Science Journalist (US)"}
    },
    {
        "anchor": {"voice": "en-GB-ThomasNeural", "rate": "+2%", "pitch": "-2Hz", "name": "Documentarian (GB)"},
        "analyst": {"voice": "en-GB-SoniaNeural", "rate": "+3%", "pitch": "+0Hz", "name": "UK Researcher (GB)"}
    },
    {
        "anchor": {"voice": "en-AU-WilliamNeural", "rate": "+2%", "pitch": "-1Hz", "name": "Explorer (AU)"},
        "analyst": {"voice": "en-AU-NatashaNeural", "rate": "+3%", "pitch": "+1Hz", "name": "Outback Analyst (AU)"}
    },
    {
        "anchor": {"voice": "en-US-BrianNeural", "rate": "+3%", "pitch": "-2Hz", "name": "Resonant Investigator (US)"},
        "analyst": {"voice": "en-US-EmmaNeural", "rate": "+2%", "pitch": "+0Hz", "name": "Tech Analyst (US)"}
    },
    {
        "anchor": {"voice": "en-IE-ConnorNeural", "rate": "+2%", "pitch": "-1Hz", "name": "Storyteller (IE)"},
        "analyst": {"voice": "en-IE-EmilyNeural", "rate": "+3%", "pitch": "+0Hz", "name": "Historian (IE)"}
    },
    {
        "anchor": {"voice": "hi-IN-MadhurNeural", "rate": "+4%", "pitch": "+0Hz", "name": "Energetic Paheli Host (IN)"},
        "analyst": {"voice": "hi-IN-SwaraNeural", "rate": "+3%", "pitch": "+1Hz", "name": "Curious Specialist (IN)"}
    },
    {
        "anchor": {"voice": "en-IN-PrabhatNeural", "rate": "+3%", "pitch": "-1Hz", "name": "Indian Storyteller (IN)"},
        "analyst": {"voice": "en-IN-NeerjaNeural", "rate": "+3%", "pitch": "+0Hz", "name": "Indian Analyst (IN)"}
    }
]


def get_voice_for_beat(beat_number: int, episode_num: int = 1, text: str = "", category: str = "") -> dict:
    """Alternates between Lead Anchor and Specialist with suite rotation, language detection, and micro-jitter."""
    is_hindi = any(w in (text + " " + category).lower() for w in ["paheli", "nakli", "golu", "samosa", "chacha", "rupaye", "hindi", "nuksaan"])
    if is_hindi:
        # Use energetic Indian Hindi voice suite
        suite = VOICE_SUITES[-2]
    else:
        suite = VOICE_SUITES[episode_num % (len(VOICE_SUITES) - 2)]

    base = suite["anchor"] if beat_number % 2 == 1 else suite["analyst"]

    # Subtle deterministic acoustic jitter (+/- 1Hz pitch, +/- 1% rate) to prevent audio fingerprinting
    rate_val = int(base["rate"].replace("%", "").replace("+", ""))
    pitch_val = int(base["pitch"].replace("Hz", "").replace("+", ""))

    rate_jitter = ((episode_num * 3 + beat_number * 7) % 3) - 1  # -1, 0, or +1 %
    pitch_jitter = ((episode_num * 5 + beat_number * 11) % 3) - 1  # -1, 0, or +1 Hz

    final_rate = f"{rate_val + rate_jitter:+d}%"
    final_pitch = f"{pitch_val + pitch_jitter:+d}Hz"

    return {
        "voice": base["voice"],
        "rate": final_rate,
        "pitch": final_pitch,
        "name": base["name"],
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


async def synthesize_beat_audios(beats: list[dict], episode_num: int = 1) -> list[dict]:
    """Generates voiceover for each beat with exact neural word timestamps."""
    import edge_tts

    PUBLIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    fps = 30
    total_frames = 0

    for i, beat in enumerate(beats):
        b_num = beat.get("scene_number") or beat.get("beat_number", i + 1)
        narration = beat["narration"]
        cfg = get_voice_for_beat(b_num, episode_num, text=narration, category=beat.get("category", ""))
        speaker_name = cfg.get("name", "Narrator")

        audio_filename = f"beat_{b_num}.mp3"
        audio_path = PUBLIC_AUDIO_DIR / audio_filename

        audio_bytes = bytearray()
        raw_words = []

        # Sanitize narration to prevent artificial 1-second TTS pauses
        import re
        clean_narration = re.sub(r'\.{2,}', '.', narration)
        clean_narration = re.sub(r'—|–', ', ', clean_narration)
        clean_narration = re.sub(r'\s+', ' ', clean_narration).strip()

        try:
            comm = edge_tts.Communicate(
                clean_narration,
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

        # Apply Crazy Bass DSP Audio Mastering & Silence Trimming (Zero dead air)
        temp_raw = audio_path.with_suffix(".raw.mp3")
        try:
            audio_path.rename(temp_raw)
            cmd_bass = [
                "ffmpeg", "-y", "-i", str(temp_raw),
                "-af", "bass=g=16:f=95:w=0.6,equalizer=f=60:t=q:w=1.5:g=12,volume=1.2,loudnorm=I=-14:TP=-1.5:LRA=7",
                str(audio_path),
            ]
            subprocess.run(cmd_bass, check=True, capture_output=True)
            temp_raw.unlink(missing_ok=True)
        except Exception:
            if temp_raw.exists() and not audio_path.exists():
                temp_raw.rename(audio_path)

        dur_sec = get_audio_duration(audio_path)

        # Fallback word timestamps if boundaries missing
        if not raw_words:
            words_list = clean_narration.split()
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

        # Padding between beats: 0.05s ultra-tight viral pacing (eliminates dead air)
        dur_frames = max(30, int(round((dur_sec + 0.05) * fps)))

        beat["audio_url"] = f"audio/{audio_filename}"
        beat["audio_duration_sec"] = round(dur_sec, 2)
        beat["duration_in_frames"] = dur_frames
        beat["words"] = raw_words

        total_frames += dur_frames
        print(f"🎙️ [Stage 4/5: Audio Engine] Beat #{b_num} [{speaker_name}]: {dur_sec:.2f}s ({dur_frames}f, {len(raw_words)} words) -> {audio_filename}")

    # High-retention natural timeline: No artificial padding to 58s!
    # Max hard ceiling is 58.0s (1740 frames). Optimal viral window is 28-40s.
    max_hard_ceiling = 1740  # 58.0s
    if total_frames > max_hard_ceiling:
        scale = max_hard_ceiling / total_frames
        for b in beats:
            b["duration_in_frames"] = max(45, int(round(b["duration_in_frames"] * scale)))
        now_total = sum(b["duration_in_frames"] for b in beats)
        beats[-1]["duration_in_frames"] += (max_hard_ceiling - now_total)
        print(f"⏱️ Clamped total duration to 58.0s hard ceiling ({sum(b['duration_in_frames'] for b in beats)} frames).")
    else:
        actual_sec = total_frames / fps
        print(f"⚡ [Pacing Engine] Optimized high-retention video duration: {actual_sec:.2f}s ({total_frames} frames).")

    return beats


def build_audio_and_timings_sync(beats: list[dict], episode_num: int = 1) -> list[dict]:
    return asyncio.run(synthesize_beat_audios(beats, episode_num))
