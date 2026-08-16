"""
Auren Voice Platform — Chunk 1: Core Agent Engine
---------------------------------------------------
Yeh file ek single test client ke liye poora voice pipeline chalati hai:
Caller bolta hai -> Deepgram (STT) text banata hai -> OpenAI (LLM) reply sochta hai
-> ElevenLabs (TTS) reply bolta hai -> caller sunta hai.

Chunk 2 mein hum CLIENT_CONFIG ko hardcoded se database-driven banayenge
(taaki har client ka apna prompt/voice/LLM ho, admin panel se set kiya hua).
Abhi ke liye ek client pe pipeline ko end-to-end proof karna hai.
"""

import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, groq, silero

load_dotenv()

logger = logging.getLogger("auren-voice-agent")

# ---------------------------------------------------------------------------
# CLIENT_CONFIG: Chunk 2 mein yeh database se aayega (ek row per client).
# Abhi test ke liye ek dummy client hardcoded hai — tum apna real client
# business daal sakte ho test karne ke liye.
# ---------------------------------------------------------------------------
CLIENT_CONFIG = {
    "business_name": "Test Business",
    "instructions": (
        "You are a friendly AI receptionist for Test Business. "
        "Greet the caller warmly, understand what they need, "
        "answer basic questions about services and pricing, "
        "and try to collect their name and phone number if they want a callback. "
        "Keep responses short and natural, like a real phone conversation."
    ),
    "voice_model": "aura-2-thalia-en",  # Deepgram ki reliable voice — badal sakte ho
    "llm_model": "llama-3.3-70b-versatile",  # Groq ka fast + free-tier model
}


async def entrypoint(ctx: JobContext):
    """LiveKit har naye call/room ke liye is function ko call karta hai."""
    await ctx.connect()

    logger.info(f"Agent joined room for: {CLIENT_CONFIG['business_name']}")

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=groq.LLM(model=CLIENT_CONFIG["llm_model"]),
        tts=deepgram.TTS(model=CLIENT_CONFIG["voice_model"]),
        vad=silero.VAD.load(),
    )

    agent = Agent(instructions=CLIENT_CONFIG["instructions"])

    await session.start(agent=agent, room=ctx.room)

    # Pehla greeting khud bot bole, caller ko wait na karna pade
    await session.generate_reply(
        instructions=f"Greet the caller on behalf of {CLIENT_CONFIG['business_name']} and ask how you can help."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
