"""
AI Voice Narration Generator using edge-tts.
Produces studio-grade storytelling voiceover for 60-second video shorts.
"""

import asyncio
from pathlib import Path

# Dramatic storytelling voice options:
# "en-US-ChristopherNeural" (Deep, authoritative, cinematic)
# "en-US-AriaNeural" (Expressive, engaging)
# "en-GB-RyanNeural" (British dramatic narrator)
DEFAULT_VOICE = "en-US-ChristopherNeural"


async def generate_voiceover(
    narration_text: str,
    output_mp3: Path,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
) -> Path:
    """Generates an MP3 voiceover using edge-tts."""
    import edge_tts

    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(narration_text, voice=voice, rate=rate)
    await communicate.save(str(output_mp3))
    print(f" Generated voiceover audio: {output_mp3}")
    return output_mp3


def generate_voiceover_sync(narration_text: str, output_mp3: Path, voice: str = DEFAULT_VOICE) -> Path:
    """Synchronous wrapper for voiceover generation."""
    return asyncio.run(generate_voiceover(narration_text, output_mp3, voice=voice))


if __name__ == "__main__":
    sample = "Deep within the forgotten archives of Valen, a young scholar uncovered an ancient whispering compass."
    out = Path(__file__).parent / "test_voice.mp3"
    generate_voiceover_sync(sample, out)

