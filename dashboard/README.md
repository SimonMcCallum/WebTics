# WebTics Dashboard

Simple web dashboard for viewing telemetry events in real-time.

## Features

- 📊 Real-time event viewing with auto-refresh
- 📈 Statistics cards (total events, event types, average magnitude, time range)
- 🎨 Color-coded event types for easy identification
- 🔍 Configurable session ID and event limit
- 📱 Responsive design for mobile and desktop
- 🚀 No build step required - pure HTML/CSS/JavaScript

## Usage

### Option 1: Open Directly (Simple)

```bash
# Start the backend first
docker-compose up -d

# Open the dashboard in your browser
open dashboard/index.html
# Or on Windows:
start dashboard/index.html
```

### Option 2: Serve with Python

```bash
cd dashboard
python -m http.server 8080

# Open http://localhost:8080 in your browser
```

### Option 3: Serve with Node.js

```bash
cd dashboard
npx http-server -p 8080

# Open http://localhost:8080 in your browser
```

### Option 4: Add to Docker Compose

Add nginx service to `docker-compose.yml`:

```yaml
  dashboard:
    image: nginx:alpine
    container_name: webtics_dashboard
    ports:
      - "8080:80"
    volumes:
      - ./dashboard:/usr/share/nginx/html:ro
    depends_on:
      - backend
```

Then access at `http://localhost:8080`

## Configuration

The dashboard has these controls:

1. **Backend URL**: WebTics backend API URL (default: `http://localhost:8000`)
2. **Session ID**: Which metric session to view events from
3. **Limit**: Maximum number of events to retrieve (50-1000)
4. **Refresh**: Manual refresh button
5. **Auto-Refresh**: Toggle automatic refresh every 3 seconds

## Event Types

Events are color-coded by type:

- 🔴 **Red**: Deaths, incorrect responses
- 🟢 **Green**: Respawns, correct responses, task completion
- 🔵 **Blue**: Task starts
- 🟠 **Orange**: Timeouts
- 🟣 **Purple**: Attention/ADHD assessment events

## Statistics

The dashboard shows:

- **Total Events**: Count of events in the session
- **Event Types**: Number of unique event types logged
- **Avg Magnitude**: Average magnitude value across events (useful for reaction times)
- **Time Range**: Duration from first to last event

## API Endpoint

The dashboard queries:

```
GET /api/v1/sessions/{session_id}/events?limit={limit}
```

Example response:

```json
[
  {
    "id": 1,
    "event_type": 100,
    "event_subtype": 0,
    "x": 0,
    "y": 0,
    "z": 0,
    "magnitude": 0.0,
    "data": {"test_type": "reaction_time"},
    "timestamp": "2026-02-15T12:00:00"
  }
]
```

## CORS Configuration

If you get CORS errors, ensure your backend allows the dashboard's origin:

```python
# In backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    # allow_origins=["http://localhost:8080"],  # For production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Customization

### Add Custom Event Types

Edit the `EVENT_TYPE_NAMES` object in `index.html`:

```javascript
const EVENT_TYPE_NAMES = {
    // ... existing types
    1000: 'MY_CUSTOM_EVENT',
};
```

And add custom colors:

```css
.event-type-1000 { background: #e0f2f1; color: #00695c; }
```

### Change Auto-Refresh Interval

Modify the interval in `index.html`:

```javascript
// Change from 3000ms (3 seconds) to 5000ms (5 seconds)
autoRefreshInterval = setInterval(loadEvents, 5000);
```

### Add More Statistics

Add new stat cards in the HTML:

```html
<div class="stat-card">
    <h3 id="myNewStat">-</h3>
    <p>My New Statistic</p>
</div>
```

And update in the `updateStats()` function:

```javascript
function updateStats(events) {
    // ... existing code
    document.getElementById('myNewStat').textContent = calculateMyStat(events);
}
```

## Production Deployment

For production, consider:

1. **Bundle with backend**: Serve from FastAPI static files
2. **Use CDN**: For better performance
3. **Add authentication**: Protect dashboard access
4. **Enable caching**: For static assets
5. **Use HTTPS**: Secure data transmission

Example: Serve from FastAPI

```python
# In backend/app/main.py
from fastapi.staticfiles import StaticFiles

app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
```

Access at: `http://localhost:8000/dashboard`

## Advanced Features (Future)

Potential enhancements:

- 📊 Charts and graphs (Chart.js, D3.js)
- 🗺️ Heatmap visualization for spatial events
- 📥 Export to CSV/JSON
- 🔍 Advanced filtering and search
- 📊 Real-time WebSocket updates
- 👥 Multi-session comparison
- 📈 Analytics dashboards (retention, funnels)

## Troubleshooting

### Events not loading

1. Check backend is running: `curl http://localhost:8000/`
2. Verify session ID exists in database
3. Check browser console for errors
4. Ensure CORS is configured correctly

### Auto-refresh not working

1. Check browser console for errors
2. Verify backend is accessible
3. Try manual refresh first

### Styling issues

1. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Check browser developer tools for CSS errors

## License

MIT License - See LICENSE file for details
