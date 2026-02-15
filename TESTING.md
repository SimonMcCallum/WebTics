# WebTics Testing Guide

Complete guide for testing the WebTics telemetry system locally and deploying to production.

## Prerequisites

- Docker and Docker Compose installed
- Godot Engine 4.3+ (for testing the minigame)
- (Optional) Nginx Proxy Manager for production deployment

## Local Testing

### 1. Start the Backend

```bash
# From the WebTics root directory
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Verify services are running
docker-compose ps
```

The backend will be available at `http://localhost:8013`

### 2. Test the API

```bash
# Health check
curl http://localhost:8013/

# Create a test session
curl -X POST http://localhost:8013/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"unique_id": "test_player_1", "build_number": "0.1.0"}'

# Response will include session_id, use it for play session
curl -X POST http://localhost:8013/api/v1/play-sessions \
  -H "Content-Type: application/json" \
  -d '{"metric_session_id": 1}'

# Log a test event (use play_session_id from above)
curl -X POST "http://localhost:8013/api/v1/events?play_session_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": 100,
    "event_subtype": 0,
    "x": 0,
    "y": 0,
    "magnitude": 1.5,
    "data": {"test": true}
  }'

# Retrieve events for session
curl http://localhost:8013/api/v1/sessions/1/events
```

### 3. Test with the Godot Minigame

1. Open Godot Engine
2. Import the project from `minigame/reaction_test/`
3. Copy the WebTics addon:
   ```bash
   cp -r sdk/godot/addons minigame/reaction_test/
   ```
4. Enable the WebTics plugin:
   - Project → Project Settings → Plugins
   - Enable "WebTics"
5. Run the game (F5)
6. Click "Start Test" and complete the trials
7. Check the Godot console for WebTics logs

### 4. Verify Data in Database

```bash
# Access PostgreSQL
docker-compose exec db psql -U webtics -d webtics

# Query sessions
SELECT * FROM metric_sessions;

# Query play sessions
SELECT * FROM play_sessions;

# Query events
SELECT * FROM events ORDER BY timestamp DESC LIMIT 10;

# Count events by type
SELECT event_type, COUNT(*) FROM events GROUP BY event_type;

# Exit psql
\q
```

## Viewing Events

### API Query

```bash
# Get all events for a session
curl http://localhost:8013/api/v1/sessions/1/events

# Pretty print with jq
curl http://localhost:8013/api/v1/sessions/1/events | jq '.'
```

### Database Query

```sql
-- Get recent events with details
SELECT
    e.id,
    e.event_type,
    e.event_subtype,
    e.x, e.y, e.z,
    e.magnitude,
    e.data,
    e.timestamp,
    ps.id as play_session_id,
    ms.unique_id as player_id
FROM events e
JOIN play_sessions ps ON e.play_session_id = ps.id
JOIN metric_sessions ms ON ps.metric_session_id = ms.id
ORDER BY e.timestamp DESC
LIMIT 20;

-- Calculate average reaction time
SELECT
    AVG(magnitude) as avg_reaction_time_sec,
    COUNT(*) as total_responses
FROM events
WHERE event_type = 102  -- CORRECT_RESPONSE
AND magnitude > 0;
```

## Production Deployment

### 1. Prepare Your Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Create webtics user (optional)
sudo useradd -m -s /bin/bash webtics
sudo usermod -aG docker webtics
```

### 2. Deploy WebTics

```bash
# Clone or copy WebTics to server
git clone https://github.com/YourUsername/WebTics.git
cd WebTics

# Create production environment file
cat > backend/.env <<EOF
DATABASE_URL=postgresql://webtics:CHANGE_THIS_PASSWORD@db:5432/webtics
EOF

# Update docker-compose.yml for production
# - Change PostgreSQL password
# - Remove volume mounts for code (use COPY in Dockerfile)
# - Add restart: unless-stopped

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 3. Configure Nginx Proxy Manager

See [nginx/README.md](nginx/README.md) for NPM configuration.

Or use standard nginx configuration:

```bash
# Copy nginx config
sudo cp nginx/webtics.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/webtics.conf /etc/nginx/sites-enabled/

# Update server_name in config
sudo nano /etc/nginx/sites-available/webtics.conf

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Set Up SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d webtics.yourdomain.com

# Auto-renewal is configured automatically
```

### 5. Update Godot Game Configuration

In your game's code, update the WebTics URL:

```gdscript
func _ready():
    # Production URL
    WebTics.configure("https://webtics.yourdomain.com")
```

## Testing Checklist

### Backend Tests
- [ ] Backend starts successfully
- [ ] Database migrations applied
- [ ] Health check returns 200
- [ ] Can create metric session
- [ ] Can create play session
- [ ] Can log single event
- [ ] Can log batch events
- [ ] Can retrieve events
- [ ] Can close sessions

### Godot Integration Tests
- [ ] Plugin loads without errors
- [ ] WebTics singleton available
- [ ] Can connect to backend
- [ ] Session created successfully
- [ ] Events logged during gameplay
- [ ] Play session closed properly
- [ ] Metric session closed on exit
- [ ] Error handling works

### Performance Tests
- [ ] Single event latency < 100ms
- [ ] Batch 100 events < 500ms
- [ ] Backend handles 100 req/sec
- [ ] Database query response < 200ms
- [ ] No memory leaks during long sessions

### Security Tests
- [ ] HTTPS enforced in production
- [ ] CORS configured correctly
- [ ] SQL injection prevented
- [ ] Rate limiting active
- [ ] Logs don't contain sensitive data

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Check database connection
docker-compose exec backend python -c "from app.database import engine; print(engine)"

# Recreate containers
docker-compose down
docker-compose up -d --force-recreate
```

### Godot can't connect

1. Check backend URL in game code
2. Verify backend is accessible: `curl http://localhost:8013/`
3. Check Godot console for error messages
4. Verify CORS headers are set
5. Test with browser dev tools network tab

### Events not appearing in database

```bash
# Check if play session exists
docker-compose exec db psql -U webtics -d webtics -c "SELECT * FROM play_sessions;"

# Check backend logs for errors
docker-compose logs backend | grep ERROR

# Verify event API call succeeded in Godot console
```

### Performance issues

```bash
# Check database connections
docker-compose exec db psql -U webtics -d webtics -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor backend resources
docker stats webtics_backend

# Add database indexes if needed
docker-compose exec db psql -U webtics -d webtics -c "CREATE INDEX idx_events_timestamp ON events(timestamp);"
```

## Next Steps

1. **Analytics Dashboard**: Create a web dashboard to visualize events (Grafana, custom React app)
2. **Export Tools**: Add CSV/JSON export for researcher analysis
3. **Real-time Monitoring**: Set up Prometheus + Grafana for backend metrics
4. **Automated Tests**: Add pytest tests for backend, GDScript tests for SDK
5. **CI/CD**: Set up GitHub Actions for automated testing and deployment

## Support

For issues or questions:
- Check documentation in `docs/`
- Review API documentation: `http://localhost:8013/docs`
- Open an issue on GitHub
