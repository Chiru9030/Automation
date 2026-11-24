"""
Stage 6: Kinetic Subtitle & Frame-Accurate Typography Engine.
Compiles broadcast-grade Submagic / Alex Hormozi style subtitles with dynamic style rotation:
- 3 Rotating Typography Presets: Hormozi Punch (Impact/Gold), MrBeast Lime (Arial Black/Lime), Cyber Cyan (Trebuchet/Cyan)
- Grouped into punchy 2-3 word chunks (optimal mobile reading pace)
- Millisecond-accurate discrete word highlighting with contextual emotion color tags
- Dynamic scale bounce pop (115% - 118%)
- Strictly anchored in the safe lower-third zone (MarginV=420) above all YouTube Shorts UI overlays.
"""

from pathlib import Path

TYPOGRAPHY_PRESETS = [
    {
        "id": "hormozi_punch",
        "name": "Hormozi Punch",
        "font": "Impact",
        "size": 58,
        "primary": "&H00FFFFFF&",     # Pure White
        "secondary": "&H0000E6FF&",   # Neon Gold Yellow
        "default_highlight": r"{\c&H0000E6FF&}",
        "outline": 5,
        "shadow": 3,
        "scale_pop": 116,
    },
    {
        "id": "mrbeast_lime",
        "name": "MrBeast Lime",
        "font": "Arial Black",
        "size": 56,
        "primary": "&H00FFFFFF&",     # Pure White
        "secondary": "&H0033FF33&",   # Neon Electric Lime Green
        "default_highlight": r"{\c&H0033FF33&}",
        "outline": 6,
        "shadow": 4,
        "scale_pop": 118,
    },
    {
        "id": "cyber_cyan",
        "name": "Cyber Cyan",
        "font": "Trebuchet MS",
        "size": 55,
        "primary": "&H00FFFFFF&",     # Ice White
        "secondary": "&H00FFFF00&",   # High-Voltage Cyan
        "default_highlight": r"{\c&H00FFFF00&}",
        "outline": 5,
        "shadow": 3,
        "scale_pop": 115,
    },
]


def get_typography_preset(episode_num: int = 1, preset_id: str | None = None) -> dict:
    """Selects the typography preset, rotating across episodes to eliminate viewer visual fatigue."""
    if preset_id:
        for p in TYPOGRAPHY_PRESETS:
            if p["id"] == preset_id:
                return p
    idx = episode_num % len(TYPOGRAPHY_PRESETS)
    return TYPOGRAPHY_PRESETS[idx]


def format_ass_time(seconds: float) -> str:
    """Formats seconds to ASS subtitle timestamp: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"


def build_subtitle_chunks(words: list[dict], max_words_per_chunk: int = 3) -> list[dict]:
    """Groups individual words into punchy 2-3 word display chunks."""
    if not words:
        return []

    chunks = []
    for i in range(0, len(words), max_words_per_chunk):
        group = words[i:i + max_words_per_chunk]
        chunks.append({
            "chunk_id": len(chunks),
            "text": " ".join(w["word"] for w in group).upper(),
            "start_frame": group[0]["start_frame"],
            "end_frame": group[-1]["end_frame"],
            "words": [
                {
                    "word": w["word"].upper().replace("{", "").replace("}", ""),
                    "start_frame": w["start_frame"],
                    "end_frame": w["end_frame"],
                }
                for w in group
            ]
        })

    # Extend chunk display until next chunk starts to prevent jarring blank flickers
    for i in range(len(chunks) - 1):
        if chunks[i]["end_frame"] < chunks[i + 1]["start_frame"]:
            chunks[i]["end_frame"] = chunks[i + 1]["start_frame"]

    return chunks


def get_word_highlight_tags(
    word: str,
    default_highlight: str = r"{\c&H0000E6FF&}",
    scale_pop: int = 116,
) -> tuple[str, str, str]:
    """
    Returns dynamic kinetic active word formatting:
    - (prefix_tags, emoji, reset_suffix)
    - Active word pops in scale (115-118%) with dynamic emotion colors:
      * Neon Green (&H0066FF00&) for numbers & metrics
      * Neon Crimson Red (&H003333FF&) for danger & destruction
      * Neon Cyan (&H00FFFF00&) for mystery & questions
      * Active preset highlight color for default punch
    """
    w_clean = word.lower().strip(".,!?;:\"'")
    emoji = ""

    # Contextual Emoji Injection
    if any(k in w_clean for k in ["ocean", "sea", "trench", "water", "dive", "submarine"]):
        emoji = " 🌊"
    elif any(k in w_clean for k in ["crush", "crushed", "shatter", "explode", "implode", "blast"]):
        emoji = " 💥"
    elif any(k in w_clean for k in ["nuclear", "reactor", "radiation", "radioactive", "atomic"]):
        emoji = " ☢️"
    elif any(k in w_clean for k in ["second", "seconds", "minute", "time", "clock"]):
        emoji = " ⏱️"
    elif any(k in w_clean for k in ["space", "saturn", "moon", "planet", "galaxy", "asteroid"]):
        emoji = " 🪐"
    elif any(k in w_clean for k in ["dinosaur", "monster", "shark", "megalodon", "predator"]):
        emoji = " 🦈"
    elif any(k in w_clean for k in ["brain", "mind", "sleep", "dream"]):
        emoji = " 🧠"
    elif any(k in w_clean for k in ["fire", "lava", "volcano", "heat", "burn"]):
        emoji = " 🔥"

    # Color & Glow Determination (Kinetic 2.0 Contextual Neon Aura)
    # 1. Numbers / Statistics / Quantities -> Neon Emerald Green
    if any(c.isdigit() for c in w_clean) or w_clean in [
        "hundred", "thousand", "million", "billion", "trillion", "zero",
        "percent", "years", "hours", "seconds", "liters", "miles", "gravity", "double"
    ]:
        glow_color = "&H0066FF00&"
    # 2. Danger / Shock / Catastrophe -> Neon Crimson Red
    elif w_clean in [
        "die", "death", "kill", "destroyed", "terror", "crushed", "shattered",
        "exploded", "fatal", "suffocate", "warning", "catastrophe", "violently",
        "radiation", "lethal", "toxic", "fall", "collapse", "danger"
    ]:
        glow_color = "&H003333FF&"
    # 3. Curiosity / Questions / Mystery -> Neon Cyan
    elif w_clean in [
        "what", "why", "how", "secret", "never", "mystery", "shocking",
        "hidden", "truth", "discovered", "impossible", "imagine", "if"
    ]:
        glow_color = "&H00FFFF00&"
    else:
        # Default active highlight from active typography preset
        glow_color = default_highlight.replace(r"{\c", "").replace("}", "") if r"{\c" in default_highlight else "&H0000E6FF&"

    # Elastic Spring Physics Bounce + Neon Aura Glow:
    # Scale peaks at (scale_pop + 12)% in 80ms, easing smoothly to scale_pop% over the next 100ms
    peak_pop = scale_pop + 12
    bounce_tags = rf"\t(0,80,\fscx{peak_pop}\fscy{peak_pop})\t(80,180,\fscx{scale_pop}\fscy{scale_pop})"
    pop_prefix = rf"{{\c{glow_color}\3c{glow_color}\blur3{bounce_tags}}}"
    reset_suffix = r"{\r\fscx100\fscy100\c&H00FFFFFF&}"
    return pop_prefix, emoji, reset_suffix


def get_word_highlight_color(word: str) -> str:
    """Backward compatibility shim."""
    prefix, _, _ = get_word_highlight_tags(word)
    return prefix


def compile_kinetic_subtitles(
    beats: list[dict],
    output_ass_path: Path,
    episode_num: int = 1,
    preset_id: str | None = None,
    top_hook_banner: str | None = None,
) -> Path:
    """Compiles exact frame-accurate ASS subtitles with persistent top banner and lower-third kinetic karaoke."""
    preset = get_typography_preset(episode_num=episode_num, preset_id=preset_id)
    print(f"  ✨ [Typography Engine] Active Subtitle Style: '{preset['name']}' (Font: {preset['font']}, Size: {preset['size']}px, Pop: {preset['scale_pop']}%)")

    # Resolve persistent Top Hook Banner text if provided
    if not top_hook_banner and beats:
        top_hook_banner = beats[0].get("top_hook_banner") or beats[0].get("banner") or ""

    banner_style = "Style: TopHookBanner,Arial,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&HE6121215,-1,0,0,0,100,100,1,0,3,18,0,8,45,45,90,1\n"

    header = f"""[Script Info]
Title: Kinetic Viral Story Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{banner_style}Style: KineticSub,{preset['font']},{preset['size']},{preset['primary']},{preset['secondary']},{preset['outline_color'] if 'outline_color' in preset else '&H00000000&'},&H90000000,-1,0,0,0,100,100,2,0,1,{preset['outline']},{preset['shadow']},2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    fps = 30
    total_frames = sum(beat.get("duration_in_frames", 348) for beat in beats)
    total_dur_sec = total_frames / fps

    # Persistent Top Hook Banner (Anchored at top of the frame for the entire duration)
    if top_hook_banner:
        clean_banner = top_hook_banner.strip()
        events.append(f"Dialogue: 1,0:00:00.00,{format_ass_time(total_dur_sec)},TopHookBanner,,0,0,0,,{clean_banner}")
        print(f"  📌 [Top Hook Banner] Injected persistent header: '{clean_banner}' (0.0s -> {total_dur_sec:.1f}s)")

    running_time = 0.0

    for beat in beats:
        beat_dur = beat.get("duration_in_frames", 348) / fps
        words = beat.get("words", [])
        chunks = build_subtitle_chunks(words, max_words_per_chunk=3)
        beat["subtitle_chunks"] = chunks

        # Active Word Karaoke Events with Emotion Color Highlighting & Active Preset Theme
        for chunk in chunks:
            chunk_words = chunk["words"]
            for i, target_word in enumerate(chunk_words):
                w_start = running_time + (target_word["start_frame"] / fps)
                w_end = running_time + (target_word["end_frame"] / fps)

                parts = []
                for j, w in enumerate(chunk_words):
                    if j == i:
                        pop_pfx, emo, rst_sfx = get_word_highlight_tags(
                            w["word"],
                            default_highlight=preset["default_highlight"],
                            scale_pop=preset["scale_pop"],
                        )
                        parts.append(pop_pfx + w["word"] + emo + rst_sfx)
                    else:
                        parts.append(w["word"])
                line_text = " ".join(parts)
                events.append(f"Dialogue: 2,{format_ass_time(w_start)},{format_ass_time(w_end)},KineticSub,,0,0,0,,{line_text}")

            last_w_end = running_time + (chunk_words[-1]["end_frame"] / fps)
            chunk_end = running_time + (chunk["end_frame"] / fps)
            if chunk_end > last_w_end + 0.04:
                plain_text = " ".join(w["word"] for w in chunk_words)
                events.append(f"Dialogue: 2,{format_ass_time(last_w_end)},{format_ass_time(chunk_end)},KineticSub,,0,0,0,,{plain_text}")

        running_time += beat_dur

    output_ass_path.parent.mkdir(parents=True, exist_ok=True)
    output_ass_path.write_text(header + "\n".join(events), encoding="utf-8")
    return output_ass_path
