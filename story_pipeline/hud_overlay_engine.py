"""
Dynamic HUD Telemetry, Progress Bar & Brand Watermark Engine (Tier 2).
Generates high-retention technical telemetry overlays:
1. Top-Right Telemetry HUD Pill (Depth / Pressure / Velocity / Chrono) with pulsing status indicator.
2. Bottom-Edge Animated Retention Progress Bar (Subtle neon line advancing 0% -> 100%).
3. Top-Left Channel Signature Watermark badge ('CURIOSITY UNIVERSE').
Integrated cleanly into the ASS subtitle compositor so it renders with ZERO additional rendering passes or CPU strain.
"""

from pathlib import Path


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


def append_hud_and_progress_to_ass(ass_path: Path, category: str = "Science", total_duration: float = 58.0):
    """
    Appends the HUD telemetry pill, channel brand badge, and bottom retention progress line
    directly into the ASS subtitle file.
    """
    if not ass_path.exists():
        return

    text = ass_path.read_text(encoding="utf-8")

    # Inject HUD and Watermark Styles if not present
    hud_styles = (
        "Style: HUDTopRight,Arial,28,&H00FFFFFF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,3,2,9,40,40,65,1\n"
        "Style: BrandBadge,Impact,32,&H0000E6FF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,4,2,7,45,40,60,1\n"
        "Style: ProgressBar,Arial,10,&H0000E6FF,&H0000E6FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,1,0,0,12,1\n"
    )

    if "[V4+ Styles]" in text and "HUDTopRight" not in text:
        text = text.replace("[Events]", hud_styles + "\n[Events]")

    hud_text = get_thematic_hud_text(category)

    # Calculate timestamps for entire video
    start_time = "0:00:00.00"
    hrs = int(total_duration // 3600)
    mins = int((total_duration % 3600) // 60)
    secs = int(total_duration % 60)
    cs = int(round((total_duration - int(total_duration)) * 100))
    end_time = f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"

    hud_events = [
        # 1. Top-Left Channel Brand Badge
        f"Dialogue: 1,{start_time},{end_time},BrandBadge,,0,0,0,,CURIOSITY UNIVERSE",
        # 2. Top-Right Dynamic Telemetry HUD
        f"Dialogue: 1,{start_time},{end_time},HUDTopRight,,0,0,0,,{hud_text}",
    ]

    # 3. Bottom Neon Retention Progress Bar (Advancing line using ASS drawing vector)
    # Divided into 10 smooth advancing keyframes
    step_sec = total_duration / 20.0
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

        # Vector line drawing in ASS: m 0 0 l {line_w} 0 {line_w} 6 0 6
        draw_tag = r"{\p1\c&H0000E6FF&\bord0\shad0}" + f"m 0 0 l {line_w} 0 {line_w} 6 0 6" + r"{\p0}"
        hud_events.append(f"Dialogue: 0,{ts_start},{ts_end},ProgressBar,,0,0,0,,{draw_tag}")

    updated_text = text.strip() + "\n" + "\n".join(hud_events) + "\n"
    ass_path.write_text(updated_text, encoding="utf-8")
    print(f"✨ [HUD Engine] Injected telemetry HUD, brand badge, and retention progress line into {ass_path.name}")
