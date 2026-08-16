"""
Auren Voice Platform — Chunk 2: Database-Driven Client Config
---------------------------------------------------------------
Yeh file ek voice pipeline chalati hai:
Caller bolta hai -> Deepgram (STT) text banata hai -> Groq (LLM) reply sochta hai
-> Deepgram (TTS) reply bolta hai -> caller sunta hai.

Chunk 2: CLIENT_CONFIG ab hardcoded nahi hai — har call pe Supabase database
se client ka config (business_name, prompt, voice, llm_model) fetch hota hai.
Isse multiple clients ek hi agent.py se handle ho sakte hain.
"""

import logging
import os

from dotenv import load_dotenv
from supabase import create_client, Client

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, groq, silero

load_dotenv()

logger = logging.getLogger("auren-voice-agent")

# ---------------------------------------------------------------------------
# Supabase connection setup — Railway ke environment variables se aayega
# ---------------------------------------------------------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def get_client_config():
    """
    Supabase se client ka config fetch karta hai.
    Abhi ke liye pehla active client uthayega (single-client testing ke liye).
    Chunk 3 mein isse incoming phone number ke basis pe specific client
    match karne ke liye update karenge.
    """
    try:
        response = (
            supabase.table("clients")
            .select("*")
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        if response.data and len(response.data) > 0:
            client = response.data[0]
            return {
                "business_name": client["business_name"],
                "instructions": client["system_prompt"],
                "voice_model": client["voice"],
                "llm_model": client["llm_model"],
            }
        else:
            raise Exception("No active client found in database")
    except Exception as e:
        logger.error(f"Error fetching client config from Supabase: {e}")
        # Fallback config agar database fail ho jaye ya khali ho
        return {
            "business_name": "Default Assistant",
            "instructions": (
                "You are a helpful AI assistant. Be friendly and concise."
            ),
            "voice_model": "aura-2-thalia-en",
            "llm_model": "llama-3.3-70b-versatile",
        }


async def entrypoint(ctx: JobContext):
    """LiveKit har naye call/room ke liye is function ko call karta hai."""
    await ctx.connect()

    client_config = get_client_config()

    logger.info(f"Agent joined room for: {client_config['business_name']}")

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=groq.LLM(model=client_config["llm_model"]),
        tts=deepgram.TTS(model=client_config["voice_model"]),
        vad=silero.VAD.load(),
    )

    agent = Agent(instructions=client_config["instructions"])

    await session.start(agent=agent, room=ctx.room)

    # Pehla greeting khud bot bole, caller ko wait na karna pade
    await session.generate_reply(
        instructions=f"Greet the caller on behalf of {client_config['business_name']} and ask how you can help."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
