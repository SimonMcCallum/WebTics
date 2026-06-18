# Deployment Guide — Home Server (Docker + Nginx Proxy Manager)

This deploys WebTics / Ludogogy Logging on Simon's home server alongside the other sites,
behind Nginx Proxy Manager (NPM), on the `proxy-net` network. The service was added to
`/home/simon/docker/docker-compose.yml` as **`webtics`** (FastAPI, internal port 8013) +
**`webtics-db`** (its own PostgreSQL, volume `webtics-pgdata`). No host port is published —
NPM routes a domain to it.

> Per CLAUDE.md, all `sudo docker` commands below are for **you to run manually**.

---

## 1. Pick a domain

Choose the public hostname, e.g. `analytics.ludogogy.co.nz` or `analytics.<your-domain>`.
Point its DNS **A record** at the server's public IP (`103.224.130.189`) first.

This guide uses `analytics.example.nz` as a placeholder — substitute your choice in the
`.env` (`WEBTICS_PUBLIC_BASE_URL`) and the NPM proxy host.

## 2. Add secrets to `/home/simon/docker/.env`

Generate strong values and append:

```bash
cat >> /home/simon/docker/.env <<EOF

# --- WebTics / Ludogogy Logging ---
WEBTICS_POSTGRES_PASSWORD=$(python3 -c "import secrets;print(secrets.token_urlsafe(24))")
WEBTICS_SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_urlsafe(48))")
WEBTICS_JWT_SECRET=$(python3 -c "import secrets;print(secrets.token_urlsafe(48))")
WEBTICS_PUBLIC_BASE_URL=https://analytics.example.nz
WEBTICS_ALLOWED_ORIGINS=*
WEBTICS_BOOTSTRAP_ADMIN_EMAIL=simon.mccallum@gmail.com
WEBTICS_BOOTSTRAP_ADMIN_PASSWORD=$(python3 -c "import secrets;print(secrets.token_urlsafe(12))")
EOF
# Show the admin password you just generated so you can save it:
grep WEBTICS_BOOTSTRAP_ADMIN_PASSWORD /home/simon/docker/.env
```

(The compose file uses `${VAR:?...}` for the three required secrets, so it will refuse to
start if any are missing — a safety net.)

## 3. Build & start

```bash
CD=/home/simon/docker
sudo docker compose -f $CD/docker-compose.yml build webtics
sudo docker compose -f $CD/docker-compose.yml up -d webtics-db webtics

# Watch it come up
sudo docker compose -f $CD/docker-compose.yml logs -f webtics
```

The app auto-creates its database tables on first start.

## 4. Your admin account (automatic)

Because you set `WEBTICS_BOOTSTRAP_ADMIN_EMAIL` + `WEBTICS_BOOTSTRAP_ADMIN_PASSWORD` in
step 2, the backend **creates/updates that admin account on startup** — nothing to run.
Log in at `/app/login` with those credentials. (The CLI `scripts/create_admin.py` and
`scripts/import_roster.py` remain available for host/dev use.)

## 5. Add the NPM proxy host

In the NPM admin UI (`http://<server-ip>:81`):

1. **Proxy Hosts → Add Proxy Host**
2. **Domain Names:** `analytics.example.nz`
3. **Scheme:** `http` · **Forward Hostname:** `webtics` · **Forward Port:** `8013`
4. **Block Common Exploits:** on · **Websockets Support:** on
5. **Custom Nginx Configuration** (so batch uploads aren't truncated):
   ```
   client_max_body_size 10m;
   ```
6. **SSL tab:** request a new Let's Encrypt cert, **Force SSL** on, HTTP/2 on.

> Remember the NPM gotcha: NPM crashes (`host not found in upstream`) if `webtics` isn't
> running when NPM (re)starts. Bring `webtics` up before restarting NPM. The boot service
> (`start-all-services.sh`) already does a two-pass `up -d` + NPM restart.

## 6. Verify

```bash
curl -s https://analytics.example.nz/            # {"status":"online",...}
curl -s https://analytics.example.nz/mp/event-registry | head
```

Then open `https://analytics.example.nz/app` → log in as admin → `/app/admin` to create a
course and import a roster (see [Admin_Guide.md](Admin_Guide.md)).

---

## Onboarding students

1. `/app/admin` → **Create a course** (set the access-ends date = account expiry).
2. **Import roster** (CSV with `email[,name]`) → download the temp-password CSV.
3. Email each student their email + temp password + the portal URL.
4. Students go to `/app/claim`, set their password, register a game, and copy the snippet.

---

## Importing rosters in production

Use the **admin UI** at `/app/admin` (Import roster) — it accepts a CSV upload and returns
the temp passwords to email out. No shell access needed. The CLI `import_roster.py` is for
local/dev use against a reachable database.

## Updating after code changes

```bash
cd /home/simon/git/WebTics && git pull
CD=/home/simon/docker
sudo docker compose -f $CD/docker-compose.yml build webtics
sudo docker compose -f $CD/docker-compose.yml up -d webtics
```

## Backups

The data lives in the `webtics-pgdata` Docker volume. To dump:

```bash
sudo docker compose -f /home/simon/docker/docker-compose.yml exec webtics-db \
    pg_dump -U webtics webtics > webtics-$(date +%F).sql
```
