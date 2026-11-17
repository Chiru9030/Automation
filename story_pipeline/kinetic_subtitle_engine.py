"""
Stage 6: Kinetic Subtitle & Frame-Accurate Typography Engine.
Compiles broadcast-grade Submagic / Alex Hormozi style subtitles:
- Grouped into punchy 2-3 word chunks (optimal mobile reading pace)
- Millisecond-accurate discrete word highlighting in glowing neon yellow (&H0000E6FF&)
- Sized at 58px with 5px black stroke (perfect visual balance: visible, readable, non-obtrusive)
- Positioned in the lower-third safe zone (MarginV=240) above YouTube Shorts UI.
"""

from pathlib import Path


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


def compile_kinetic_subtitles(beats: list[dict], output_ass_path: Path) -> Path:
    """Compiles exact frame-accurate ASS subtitles for the entire video."""
    header = """[Script Info]
Title: Kinetic Viral Story Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticSub,Impact,58,&H00FFFFFF,&H0000E6FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,5,3,2,60,60,240,1
Style: BeatBadge,Impact,30,&H0000E6FF,&H00FFFFFF,&H00000000,&HB005050F,-1,0,0,0,100,100,2,0,1,4,2,8,40,40,75,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    fps = 30
    running_time = 0.0

    for beat in beats:
        beat_dur = beat.get("duration_in_frames", 348) / fps
        words = beat.get("words", [])
        chunks = build_subtitle_chunks(words, max_words_per_chunk=3)
        beat["subtitle_chunks"] = chunks

        # Top Badge (Avatar + Speaker + Beat)
        b_start = format_ass_time(running_time)
        b_end = format_ass_time(running_time + beat_dur)
        avatar = beat.get("speaker_avatar", "🎙️")
        speaker = beat.get("speaker_name", "NARRATOR").upper()
        title = beat.get("title", f"BEAT #{beat['beat_number']}").upper()
        events.append(f"Dialogue: 1,{b_start},{b_end},BeatBadge,,0,0,0,,{avatar} {speaker} • {title}")

        # Active Word Karaoke Events (Zero drift, 100% discrete synchronization)
        for chunk in chunks:
            chunk_words = chunk["words"]
            for i, target_word in enumerate(chunk_words):
                w_start = running_time + (target_word["start_frame"] / fps)
                w_end = running_time + (target_word["end_frame"] / fps)

                parts = []
                for j, w in enumerate(chunk_words):
                    if j == i:
                        parts.append(r"{\c&H0000E6FF&}" + w["word"] + r"{\c&H00FFFFFF&}")
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
