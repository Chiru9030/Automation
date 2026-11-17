"""
Procedural Cinematic Sound Effects (SFX) Synthesizer.
Generates broadcast-grade whooshes, cinematic impact booms, pop hits, and chimes
using Python's standard 'wave' and 'struct' libraries (zero external dependencies).
"""

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100
PUBLIC_SFX_DIR = Path(__file__).resolve().parent.parent / "video-app" / "public" / "sfx"


def clamp(val, min_val=-1.0, max_val=1.0):
    return max(min_val, min(max_val, val))


def write_wav(path: Path, frames: bytearray):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)  # Stereo
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(frames)
    print(f"🔊 Generated SFX: {path.name}")


def generate_whoosh(output_path: Path, duration: float = 0.5):
    """Generates a dynamic camera transition whoosh / swish."""
    num_samples = int(SAMPLE_RATE * duration)
    frames = bytearray()
    import random

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        progress = t / duration

        # Frequency sweeps up then down
        freq = 180 + 700 * math.sin(progress * math.pi)
        # Fast noise-modulated air whoosh
        noise = (random.random() * 2.0 - 1.0) * 0.3
        sine = math.sin(2.0 * math.pi * freq * t) * 0.7

        # Volume envelope: peaks at 50%
        env = math.sin(progress * math.pi) ** 1.8

        sig = clamp((sine + noise) * env * 0.75)
        sample = int(sig * 32767.0)
        frames.extend(struct.pack("<hh", sample, sample))

    write_wav(output_path, frames)


def generate_impact_boom(output_path: Path, duration: float = 1.2):
    """Generates a deep cinematic sub-bass impact boom for dramatic moments."""
    num_samples = int(SAMPLE_RATE * duration)
    frames = bytearray()

    for i in range(num_samples):
        t = i / SAMPLE_RATE

        # Pitch drops rapidly from 120Hz to 38Hz (sub-bass drop)
        pitch = 38.0 + 82.0 * math.exp(-t * 9.0)
        sine = math.sin(2.0 * math.pi * pitch * t)
        sine2 = math.sin(2.0 * math.pi * (pitch * 0.5) * t) * 0.5

        # Exponential decay envelope
        env = math.exp(-t * 3.5)

        sig = clamp((sine + sine2) * env * 0.9)
        sample = int(sig * 32767.0)
        frames.extend(struct.pack("<hh", sample, sample))

    write_wav(output_path, frames)


def generate_pop(output_path: Path, duration: float = 0.12):
    """Generates a snappy, satisfying UI / subtitle pop sound."""
    num_samples = int(SAMPLE_RATE * duration)
    frames = bytearray()

    for i in range(num_samples):
        t = i / SAMPLE_RATE

        # Rapid pitch rise and drop (350Hz -> 850Hz -> 200Hz)
        pitch = 350.0 + 500.0 * math.sin((t / duration) * math.pi)
        sine = math.sin(2.0 * math.pi * pitch * t)
        env = math.exp(-t * 38.0)

        sig = clamp(sine * env * 0.8)
        sample = int(sig * 32767.0)
        frames.extend(struct.pack("<hh", sample, sample))

    write_wav(output_path, frames)


def generate_all_sfx():
    """Generates the full core sound effects suite for the video engine."""
    PUBLIC_SFX_DIR.mkdir(parents=True, exist_ok=True)
    generate_whoosh(PUBLIC_SFX_DIR / "whoosh.wav")
    generate_impact_boom(PUBLIC_SFX_DIR / "impact_boom.wav")
    generate_pop(PUBLIC_SFX_DIR / "pop.wav")


if __name__ == "__main__":
    generate_all_sfx()
