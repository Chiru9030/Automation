"""
Antigravity Agent with 8-Hour Periodic Trigger for Story Automation.
Uses google.antigravity.triggers.every to fire autonomous video production cycles.
"""

import asyncio
from pathlib import Path
from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.triggers import every, TriggerContext
from google.antigravity.hooks import policy

BASE_DIR = Path(__file__).resolve().parent
from story_runner import process_next_story


async def eight_hour_story_cycle(ctx: TriggerContext):
    """Trigger handler executed every 8 hours."""
    print("\n⏰ [TRIGGER FIRED] Starting scheduled story video production...")
    result = process_next_story()
    await ctx.send(f"Automated story pipeline cycle finished. Result: {result}")


async def main():
    print("==========================================================")
    print(" Antigravity Autonomous Story Daemon (8-Hour Triggers)    ")
    print("==========================================================")

    # Trigger fires every 8 hours (28,800 seconds)
    timer_trigger = every(8 * 3600, eight_hour_story_cycle)

    config = LocalAgentConfig(
        system_instructions=(
            "You are an autonomous story video production and publishing supervisor. "
            "Every 8 hours, you monitor the rendering and social media uploads."
        ),
        workspaces=[str(BASE_DIR)],
        triggers=[timer_trigger],
        policies=[policy.allow_all()],
    )

    async with Agent(config) as agent:
        print("Agent is active and monitoring the 8-hour schedule. Running first cycle now...")
        process_next_story()
        print("Waiting for future periodic triggers (press Ctrl+C to stop)...")
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())

