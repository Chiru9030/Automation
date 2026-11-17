"""
Genre-Aware Audio Synthesizer for Automated Video Production.
Generates ambient/cinematic royalty-free background soundtracks
using Python's standard 'wave' and 'struct' libraries (zero external dependencies).
Supports 15s, 60s, or custom durations.
"""

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100


def clamp(val, min_val=-1.0, max_val=1.0):
    return max(min_val, min(max_val, val))


def generate_music_for_genre(genre: str, output_path: Path, duration: float = 60.0) -> Path:
    """Generates an ambient soundtrack tailored to the story's genre and duration."""
    genre_lower = genre.lower()
    num_samples = int(SAMPLE_RATE * duration)

    # Determine musical parameters based on genre
    if any(k in genre_lower for k in ["children", "warm", "playful", "kids", "lion", "animal"]):
        # Warm, cheerful, playful acoustic marimba & pad
        base_freq = 130.81  # C3
        chord_freqs = [130.81, 164.81, 196.00, 261.63, 329.63]  # C Major 9th
        pulse_bpm = 76
        shimmer = True
    elif any(k in genre_lower for k in ["fantasy", "fairy", "lore", "ancient", "magic"]):
        # Mystical Celtic / Ambient Fantasy Pad
        base_freq = 73.42  # D2
        chord_freqs = [73.42, 110.00, 164.81, 220.00, 293.66]  # D Sus2
        pulse_bpm = 54
        shimmer = True
    elif any(k in genre_lower for k in ["mystery", "horror", "dark", "crime", "suspense", "thriller"]):
        # Tense Suspense Drone & Heartbeat
        base_freq = 55.00  # A1
        chord_freqs = [55.00, 77.78, 110.00, 164.81]  # Tritone tension
        pulse_bpm = 68
        shimmer = False
    elif any(k in genre_lower for k in ["sci-fi", "space", "cosmic", "universe"]):
        # Ambient Cosmic Drone & Shimmer
        base_freq = 65.41  # C2
        chord_freqs = [65.41, 98.00, 155.56, 196.00]
        pulse_bpm = 60
        shimmer = True
    elif any(k in genre_lower for k in ["action", "energy", "adventure"]):
        # Driving Adventure Synth Pulse
        base_freq = 73.42  # D2
        chord_freqs = [73.42, 110.00, 146.83, 220.00]
        pulse_bpm = 95
        shimmer = True
    else:
        # Default: Cinematic Ambient
        base_freq = 65.41
        chord_freqs = [65.41, 98.00, 130.81, 196.00]
        pulse_bpm = 70
        shimmer = True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = bytearray()
    beat_interval = 60.0 / pulse_bpm

    for i in range(num_samples):
        t = i / SAMPLE_RATE

        # Volume Envelope (Fade-in first 1.0s, Fade-out last 2.0s)
        if t < 1.0:
            env = t / 1.0
        elif t > (duration - 2.0):
            env = max(0.0, (duration - t) / 2.0)
        else:
            env = 1.0

        # Sub-bass Warm Drone
        drone = 0.25 * math.sin(2.0 * math.pi * base_freq * t)
        drone += 0.10 * math.sin(2.0 * math.pi * (base_freq * 0.5) * t)

        # Chord Pad Layer with subtle chorus
        pad = 0.0
        for idx, freq in enumerate(chord_freqs):
            detune = 1.0 + 0.002 * math.sin(t * 0.3 + idx)
            pad += 0.05 * math.sin(2.0 * math.pi * freq * detune * t)

        # Rhythmic Pulse / Heartbeat
        beat_phase = (t % beat_interval) / beat_interval
        pulse = math.exp(-beat_phase * 10.0) * math.sin(2.0 * math.pi * 50.0 * t) * 0.16

        # High shimmer / bell tones
        bell = 0.0
        if shimmer:
            bell_time = t % 1.8
            bell_note = [523.25, 659.25, 783.99, 1046.50][int(t / 1.8) % 4]
            bell = math.exp(-bell_time * 3.5) * math.sin(2.0 * math.pi * bell_note * t) * 0.07

        # Mix and Apply Envelope
        left_signal = (drone + pad + pulse * 0.8 + bell * 0.9) * env * 0.65
        right_signal = (drone + pad + pulse * 0.8 + bell * 0.7) * env * 0.65

        left_sample = int(clamp(left_signal) * 32767.0)
        right_sample = int(clamp(right_signal) * 32767.0)

        frames.extend(struct.pack("<hh", left_sample, right_sample))

    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(frames)

    print(f" Generated {duration}s soundtrack for genre '{genre}' -> {output_path}")
    return output_path


if __name__ == "__main__":
    out = Path(__file__).parent / "video-app" / "public" / "audio" / "story_bg.wav"
    generate_music_for_genre("Children Adventure / Warm", out, duration=60.0)
