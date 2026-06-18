"""WebTics / Ludogogy Logging — Discord support bot.

An AI helper that answers students' questions about using the WebTics analytics service,
powered by the course's **local Ollama** instance plus a curated knowledge base. No data
leaves the server: the model runs locally and the knowledge is the bundled markdown.

Surfaces:
  * Slash command  /webtics <question>   (works with no privileged intents)
  * @mention the bot with a question      (needs the Message Content intent enabled)

Configuration (environment variables):
  DISCORD_BOT_TOKEN        (required) the bot token from the Discord developer portal
  OLLAMA_URL               default http://ollama:11434
  OLLAMA_MODEL             default gemma3:4b  (must be pulled in Ollama)
  WEBTICS_PUBLIC_BASE_URL  default http://192.168.1.64:8013 (used to fill PORTAL in answers)
  DISCORD_GUILD_IDS        optional comma-separated guild ids to scope/sync commands to
  ENABLE_MENTION_REPLIES   "true" to also answer @mentions (needs Message Content intent)
  KB_DIR                   default /app/knowledge
  REQUEST_TIMEOUT          default 120 (seconds to wait on Ollama)
"""
import asyncio
import glob
import logging
import os

import httpx
import discord
from discord import app_commands

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("webtics-bot")

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
PUBLIC_BASE_URL = os.getenv("WEBTICS_PUBLIC_BASE_URL", "http://192.168.1.64:8013").rstrip("/")
GUILD_IDS = [int(x) for x in os.getenv("DISCORD_GUILD_IDS", "").replace(" ", "").split(",") if x]
ENABLE_MENTION_REPLIES = os.getenv("ENABLE_MENTION_REPLIES", "false").lower() in ("1", "true", "yes")
KB_DIR = os.getenv("KB_DIR", "/app/knowledge")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "120"))

DISCORD_LIMIT = 2000


def load_knowledge() -> str:
    """Concatenate the bundled markdown KB, with PORTAL placeholders filled in."""
    parts = []
    for path in sorted(glob.glob(os.path.join(KB_DIR, "*.md"))):
        try:
            with open(path, encoding="utf-8") as f:
                parts.append(f.read())
        except OSError as e:
            log.warning("Could not read KB file %s: %s", path, e)
    text = "\n\n".join(parts) if parts else "(knowledge base missing)"
    return text.replace("PORTAL/../", PUBLIC_BASE_URL + "/").replace("PORTAL", PUBLIC_BASE_URL + "/app")


KNOWLEDGE = load_knowledge()

SYSTEM_PROMPT = (
    "You are the WebTics / Ludogogy Logging support assistant for a university game-dev "
    "course. You help students add analytics to their games and troubleshoot problems. "
    "Answer ONLY using the knowledge below. Be concise and practical, use Discord markdown, "
    "and include a short code snippet when it helps. If the answer isn't in the knowledge, "
    "say so briefly and point them to the portal docs or their instructor — do not invent "
    "endpoints, parameters, or numbers. Never reveal secrets or other students' data.\n\n"
    f"The student portal base URL is {PUBLIC_BASE_URL}/app .\n\n"
    "=== KNOWLEDGE BASE ===\n" + KNOWLEDGE
)


async def ask_ollama(question: str) -> str:
    """Query the local Ollama chat API. Returns the assistant's reply text."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
    return (data.get("message") or {}).get("content", "").strip() or "(no answer)"


def chunk(text: str, size: int = DISCORD_LIMIT - 100):
    """Split a reply into Discord-sized chunks, preferring line boundaries.

    Lines longer than `size` (e.g. a giant code line) are hard-sliced so no chunk ever
    exceeds Discord's 2000-char message limit.
    """
    out, cur = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > size:  # hard-split a single over-long line
            if cur:
                out.append(cur)
                cur = ""
            out.append(line[:size])
            line = line[size:]
        if len(cur) + len(line) > size:
            if cur:
                out.append(cur)
            cur = line
        else:
            cur += line
    if cur:
        out.append(cur)
    return out or ["(empty)"]


intents = discord.Intents.default()
if ENABLE_MENTION_REPLIES:
    intents.message_content = True  # privileged — must be enabled in the dev portal too

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="webtics", description="Ask the WebTics helper how to add analytics to your game")
@app_commands.describe(question="Your question about WebTics / Ludogogy Logging")
async def webtics(interaction: discord.Interaction, question: str):
    # Ollama can take >3s, so defer immediately to avoid the interaction timing out.
    await interaction.response.defer(thinking=True)
    try:
        answer = await ask_ollama(question)
    except Exception as e:  # network/model errors shouldn't crash the command
        log.exception("Ollama request failed")
        answer = (
            "Sorry — I couldn't reach the local AI right now. Try again shortly, or check "
            f"the docs at {PUBLIC_BASE_URL}/app/docs. (debug: {type(e).__name__})"
        )
    pieces = chunk(answer)
    await interaction.followup.send(pieces[0])
    for extra in pieces[1:]:
        await interaction.followup.send(extra)


@client.event
async def on_ready():
    try:
        if GUILD_IDS:
            for gid in GUILD_IDS:
                guild = discord.Object(id=gid)
                tree.copy_global_to(guild=guild)
                await tree.sync(guild=guild)
            log.info("Synced /webtics to guilds: %s", GUILD_IDS)
        else:
            await tree.sync()
            log.info("Synced /webtics globally (can take up to ~1h to appear)")
    except Exception:
        log.exception("Command sync failed")
    log.info("Logged in as %s — model=%s ollama=%s", client.user, OLLAMA_MODEL, OLLAMA_URL)


@client.event
async def on_message(message: discord.Message):
    if not ENABLE_MENTION_REPLIES or message.author.bot or client.user is None:
        return
    if client.user not in message.mentions:
        return
    question = message.content.replace(f"<@{client.user.id}>", "").replace(f"<@!{client.user.id}>", "").strip()
    if not question:
        await message.reply("Ask me anything about WebTics! e.g. `@me how do I register my game?`")
        return
    async with message.channel.typing():
        try:
            answer = await ask_ollama(question)
        except Exception as e:
            log.exception("Ollama request failed")
            answer = f"Sorry — local AI is unavailable right now. See {PUBLIC_BASE_URL}/app/docs ({type(e).__name__})."
    pieces = chunk(answer)
    await message.reply(pieces[0])
    for extra in pieces[1:]:
        await message.channel.send(extra)


def main():
    if not TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is not set")
    client.run(TOKEN)


if __name__ == "__main__":
    main()
