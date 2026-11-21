"""
Dynamic Visual Theme & HUD Overlay Engine (Anti-Repetition Shield).
Rotates across 4 distinct visual presentation themes across episodes:
- Theme 0: TECHNICAL_TELEMETRY (Live data telemetry pill + channel brand badge + bottom progress line)
- Theme 1: MODERN_MINIMALIST (Clean full-bleed visuals with subtitles only; zero HUD/badge pixel repetition)
- Theme 2: CURIOSITY_BANNER (Top bold question hook pill e.g., 'CAN YOU SURVIVE?' + bottom progress line)
- Theme 3: CINEMATIC_ARCHIVE (Clean top-left episode archive mark + subtle timecode + lower progress line)

Integrated cleanly into the ASS subtitle compositor so it renders with ZERO additional rendering passes or CPU strain.
"""

from pathlib import Path


OVERLAY_THEMES = [
    "technical_telemetry",
    "modern_minimalist",
    "curiosity_banner",
    "cinematic_archive",
]


def get_thematic_hud_text(category: str) -> str:
    """Generates thematic technical telemetry based on the story category."""
    c = category.lower()
    if any(k in c for k in ["sea", "ocean", "trench", "abyss", "submarine", "water"]):
        return r"DEPTH: 10,994m  |  PRESSURE: 1,086 ATM  |  \c&H0033FF33&● LIVE\c&H00FFFFFF&"
    elif any(k in c for k in ["space", "cosmic", "saturn", "moon", "jupiter", "planet", "alien"]):
        return r"ORBIT: 1.2B KM  |  VELOCITY: 28,400 KM/H  |  \c&H0033FF33&● LIVE\c&H00FFFFFF&"
    elif any(k in c for k in ["prehistoric", "dinosaur", "megalodon", "ancient"]):
        return r"CHRONO: -66M YRS  |  O2 LEVEL: 32%  |  \c&H0033FF33&● SIM\c&H00FFFFFF&"
    elif any(k in c for k in ["body", "brain", "immune", "cell", "medical", "sleep"]):
        return r"NEURAL FREQ: 40 Hz  |  CELL ACTIVITY: CRITICAL  |  \c&H003333FF&● ALERT\c&H00FFFFFF&"
    else:
        return r"ANOMALY INDEX: 9.8  |  SIMULATION ACTIVE  |  \c&H0033FF33&● LIVE\c&H00FFFFFF&"


def append_hud_and_progress_to_ass(
    ass_path: Path, category: str = "Science", total_duration: float = 58.0, episode_num: int = 1
):
    """
    Appends one of 4 rotating visual themes directly into the ASS subtitle file.
    Defeats YouTube's automated template detection by varying the visual composition per episode.
    """
    if not ass_path.exists():
        return

    text = ass_path.read_text(encoding="utf-8")
    theme_idx = episode_num % len(OVERLAY_THEMES)
    chosen_theme = OVERLAY_THEMES[theme_idx]

    # Inject HUD and Theme Styles into ASS header
    hud_styles = (
        "Style: HUDTopRight,Arial,28,&H00FFFFFF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,3,2,9,40,40,65,1\n"
        "Style: BrandBadge,Impact,32,&H0000E6FF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,4,2,7,45,40,60,1\n"
        "Style: HookBanner,Impact,34,&H00FFFFFF,&H00000000,&H00000000,&HE0000000,-1,0,0,0,100,100,2,0,1,5,2,8,30,30,65,1\n"
        "Style: ArchiveMark,Arial,24,&H00D0D0D0,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,3,2,7,45,40,65,1\n"
        "Style: ProgressBar,Arial,10,&H0000E6FF,&H0000E6FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,1,0,0,12,1\n"
    )

    if "[V4+ Styles]" in text and "HUDTopRight" not in text:
        text = text.replace("[Events]", hud_styles + "\n[Events]")

    start_time = "0:00:00.00"
    hrs = int(total_duration // 3600)
    mins = int((total_duration % 3600) // 60)
    secs = int(total_duration % 60)
    cs = int(round((total_duration - int(total_duration)) * 100))
    end_time = f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"

    hud_events = []

    # 1. Theme-Specific Visual Headers
    if chosen_theme == "technical_telemetry":
        hud_text = get_thematic_hud_text(category)
        hud_events.extend([
            f"Dialogue: 1,{start_time},{end_time},BrandBadge,,0,0,0,,CURIOSITY UNIVERSE",
            f"Dialogue: 1,{start_time},{end_time},HUDTopRight,,0,0,0,,{hud_text}",
        ])
    elif chosen_theme == "curiosity_banner":
        hook_titles = [
            "● CAN YOU SURVIVE THIS? ●",
            "● 99% OF PEOPLE GET THIS WRONG ●",
            "● THE SHOCKING TRUTH ●",
            "● SCIENTIFIC ANOMALY DETECTED ●",
        ]
        chosen_hook = hook_titles[episode_num % len(hook_titles)]
        hud_events.append(
            f"Dialogue: 1,{start_time},{end_time},HookBanner,,0,0,0,,{{\\c&H0000E6FF&}}{chosen_hook}"
        )
    elif chosen_theme == "cinematic_archive":
        hud_events.append(
            f"Dialogue: 1,{start_time},{end_time},ArchiveMark,,0,0,0,,PARADOX ARCHIVE // EPISODE #{episode_num:02d}"
        )
    # Note: "modern_minimalist" intentionally adds ZERO top overlay elements! Pure cinematic full bleed.

    # 2. Subtle Bottom Retention Progress Bar (Divided into 20 advancing keyframes)
    step_sec = total_duration / 20.0
    bar_color = "&H0000E6FF&" if chosen_theme != "curiosity_banner" else "&H00E6FF00&"
    for step in range(20):
        t_start = step * step_sec
        t_end = (step + 1) * step_sec
        s_h, s_m, s_s = int(t_start // 3600), int((t_start % 3600) // 60), int(t_start % 60)
        s_cs = int(round((t_start - int(t_start)) * 100))
        e_h, e_m, e_s = int(t_end // 3600), int((t_end % 3600) // 60), int(t_end % 60)
        e_cs = int(round((t_end - int(t_end)) * 100))

        ts_start = f"{s_h}:{s_m:02d}:{s_s:02d}.{s_cs:02d}"
        ts_end = f"{e_h}:{e_m:02d}:{e_s:02d}.{e_cs:02d}"
        line_w = int(1080 * ((step + 1) / 20.0))

        draw_tag = r"{\p1\c" + bar_color + r"\bord0\shad0}" + f"m 0 0 l {line_w} 0 {line_w} 6 0 6" + r"{\p0}"
        hud_events.append(f"Dialogue: 0,{ts_start},{ts_end},ProgressBar,,0,0,0,,{draw_tag}")

    updated_text = text.strip() + "\n" + "\n".join(hud_events) + "\n"
    ass_path.write_text(updated_text, encoding="utf-8")
    print(f"✨ [HUD Engine] Applied visual theme '{chosen_theme}' (Episode #{episode_num}) into {ass_path.name}")

