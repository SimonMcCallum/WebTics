# WebTics Discord Support Bot

An AI helper for your course Discord that answers students' questions about using
**WebTics / Ludogogy Logging** — powered by the server's **local Ollama** instance plus a
bundled knowledge base (`knowledge/*.md`). Nothing leaves the server: the model runs
locally and the knowledge is just the markdown in this folder.

- **`/webtics <question>`** — slash command (works with no special permissions).
- **@mention the bot** — optional; needs the privileged *Message Content* intent.

## 1. Create the bot in Discord (one-time)

1. Go to <https://discord.com/developers/applications> → **New Application** (e.g. "WebTics Helper").
2. **Bot** tab → **Add Bot** → **Reset Token** → copy the token.
3. (Optional, for @mention replies) under **Privileged Gateway Intents**, enable
   **Message Content Intent**.
4. **OAuth2 → URL Generator**: scopes `bot` + `applications.commands`; bot permissions
   *Send Messages*, *Read Message History* (+ *Use Slash Commands*). Open the generated
   URL and invite the bot to your course server.
5. Copy your server's **Guild ID** (enable Developer Mode in Discord → right-click the
   server → *Copy Server ID*) — used for instant slash-command sync.

## 2. Configure

In `/home/simon/docker/.env`:

```
WEBTICS_DISCORD_BOT_TOKEN=<the token from step 2>
WEBTICS_OLLAMA_MODEL=gemma3:4b          # or any model from `ollama list`
WEBTICS_DISCORD_GUILD_IDS=<your guild id>   # optional; instant command sync + scoping
WEBTICS_BOT_MENTION_REPLIES=false       # true to also answer @mentions (needs intent above)
WEBTICS_PUBLIC_BASE_URL=http://192.168.1.64:8013   # used to fill in links in answers
```

## 3. Build & run (on the home server)

```bash
CD=/home/simon/docker
sudo docker compose -f $CD/docker-compose.yml build webtics-discord-bot
sudo docker compose -f $CD/docker-compose.yml up -d webtics-discord-bot
sudo docker compose -f $CD/docker-compose.yml logs -f webtics-discord-bot
# look for: "Synced /webtics to guilds: [...]" and "Logged in as ..."
```

In Discord, type `/webtics how do I register my game?` — the bot defers, asks Ollama, and
replies. If you set a Guild ID the command appears instantly; otherwise global sync can
take up to ~1 hour.

## How it works

- `bot.py` loads every `knowledge/*.md` file, substitutes the portal URL, and puts it in
  the system prompt. Student questions go to Ollama's `/api/chat` (`OLLAMA_URL`,
  `OLLAMA_MODEL`); the reply is chunked to fit Discord's 2000-char limit.
- It's grounded: the prompt tells the model to answer **only** from the knowledge base and
  to defer to the portal docs / instructor when unsure — so it won't invent endpoints or
  quota numbers.

## Updating the bot's knowledge

Edit / add markdown files in `knowledge/`, then rebuild:

```bash
sudo docker compose -f /home/simon/docker/docker-compose.yml build webtics-discord-bot
sudo docker compose -f /home/simon/docker/docker-compose.yml up -d webtics-discord-bot
```

Use the literal token `PORTAL` in knowledge files where you want the student portal URL —
the bot substitutes it at load time.

## Notes

- The bot reaches Ollama at `http://ollama:11434` over `proxy-net` (same Docker network).
  If Ollama is slow to answer, raise `REQUEST_TIMEOUT`.
- This bot is **help/Q&A only**. Automated account *signup* (guild-locked `/claim`) is a
  separate, larger feature — design in [`../docs/Discord_Signup_Future.md`](../docs/Discord_Signup_Future.md).
