WebTics
=======

**Modern Game Telemetry and Metrics System**

WebTics is a lightweight, self-hosted telemetry system for game developers who want full control over their analytics data. Originally designed in 2013, it has been modernized for 2026 with focus on privacy, data sovereignty, and cross-platform support.

## Features

- ✅ **Privacy-First**: Self-hosted, full data ownership
- ✅ **Cross-Platform**: Windows, Linux, Mac, Android, iOS
- ✅ **Multi-Engine**: Godot and Unreal Engine SDKs
- ✅ **Real-Time**: Async event logging with minimal latency
- ✅ **Research-Grade**: NZ Privacy Act 2020 & HIPC 2020 compliance features
- ✅ **Therapeutic Games**: Built-in support for ADHD and mental health assessment
- ✅ **Easy Deployment**: Docker Compose + nginx for quick setup

## Quick Start

### 1. Start the Backend

```bash
# Clone the repository
git clone https://github.com/SimonMcCallum/WebTics.git
cd WebTics

# Start backend with Docker
docker-compose up -d

# Verify it's running
curl http://localhost:8000/
```

### 2. Integrate with Your Game

#### Godot Engine

```gdscript
# Copy SDK to your project
cp -r sdk/godot/addons/webtics addons/

# In your game code
func _ready():
    WebTics.configure("http://localhost:8000")
    WebTics.open_metric_session("player_123", "1.0.0")
    await WebTics.session_created

    WebTics.start_play_session()
    await WebTics.play_session_created

    # Log events
    WebTics.log_event(
        EventTypes.Type.PLAYER_DEATH,
        EventTypes.DeathSubtype.FALLING,
        position.x, position.y, 0
    )
```

#### Unreal Engine

```cpp
// Get WebTics subsystem
UWebTicsSubsystem* WebTics = GetGameInstance()->GetSubsystem<UWebTicsSubsystem>();

// Configure and start session
WebTics->Configure("http://localhost:8000");
WebTics->OpenMetricSession("player_123", "1.0.0");

// Log events
WebTics->LogEventAtPosition(
    EWebTicsEventType::PLAYER_DEATH,
    GetActorLocation()
);
```

## Documentation

- **[TESTING.md](TESTING.md)** - Complete testing and deployment guide
- **[docs/Executive_Summary.md](docs/Executive_Summary.md)** - Strategic assessment and market analysis
- **[docs/Mobile_Platform_Guide.md](docs/Mobile_Platform_Guide.md)** - Android and iOS integration
- **[sdk/godot/addons/webtics/README.md](sdk/godot/addons/webtics/README.md)** - Godot SDK documentation
- **[sdk/unreal/WebTics/README.md](sdk/unreal/WebTics/README.md)** - Unreal Engine plugin documentation
- **[docs/WebTics_Modern_Assessment_2026.tex](docs/WebTics_Modern_Assessment_2026.tex)** - Technical report (LaTeX)

## Architecture

```
WebTics/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # API endpoints
│   │   ├── models.py       # SQLAlchemy models
│   │   └── schemas.py      # Pydantic schemas
│   └── Dockerfile
├── sdk/
│   ├── godot/              # Godot SDK (GDScript)
│   │   └── addons/webtics/
│   └── unreal/             # Unreal Engine plugin (C++)
│       └── WebTics/
├── minigame/
│   └── reaction_test/      # Example ADHD assessment game
├── nginx/                  # Nginx reverse proxy config
└── docker-compose.yml      # Development environment
```

## Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 16
- SQLAlchemy ORM
- Docker & Docker Compose

**SDKs:**
- Godot: GDScript with HTTPRequest
- Unreal Engine: C++ with HTTP module
- Future: Unity C#, React Native, Flutter

**Deployment:**
- Nginx reverse proxy
- Let's Encrypt SSL
- Catalyst Cloud NZ (for data sovereignty)

## Use Cases

### 1. Indie Game Development
Self-hosted analytics without vendor lock-in or data sharing.

### 2. Educational Research
GDPR/HIPC compliant telemetry for serious games research.

### 3. Therapeutic Games
ADHD assessment, mental health interventions, cognitive training with IRB-compliant data collection.

### 4. NZ Health Data Sovereignty
Only telemetry system designed for NZ Privacy Act 2020 and Health Information Privacy Code 2020 compliance.

## Example: Reaction Time Test

Complete ADHD assessment minigame included:

```bash
# Open in Godot
godot --path minigame/reaction_test

# Start backend first
docker-compose up -d
```

The game logs:
- Task start/complete events
- Reaction times
- Click positions
- Accuracy metrics
- Trial-by-trial performance

View the data:

```bash
# Query events via API
curl http://localhost:8000/api/v1/sessions/1/events | jq '.'

# Or query database directly
docker-compose exec db psql -U webtics -d webtics
```

## Deployment

### Local Testing

```bash
docker-compose up -d
```

### Production (with SSL)

See [TESTING.md](TESTING.md) for complete deployment guide including:
- Nginx Proxy Manager setup
- Let's Encrypt SSL
- Database backups
- Security hardening
- Performance optimization

## Mobile Support

WebTics SDKs work on mobile platforms (Android/iOS) with minimal configuration:

- **Android**: Add `INTERNET` permission
- **iOS**: Configure App Transport Security
- **Offline Support**: Local event queuing (planned feature)
- **Battery Optimization**: Event batching and smart timing

See [docs/Mobile_Platform_Guide.md](docs/Mobile_Platform_Guide.md) for details.

## Roadmap

### Phase 1 (Complete ✅)
- [x] FastAPI backend with event ingestion
- [x] PostgreSQL database schema
- [x] Godot SDK with async logging
- [x] Unreal Engine plugin
- [x] Docker Compose setup
- [x] Nginx configuration
- [x] Example minigame

### Phase 2 (Planned)
- [ ] Web dashboard (Grafana or custom React app)
- [ ] Unity C# SDK
- [ ] Offline event queue with SQLite
- [ ] Batch event API optimization
- [ ] Real-time analytics queries

### Phase 3 (Future)
- [ ] NZ Privacy Act 2020 compliance features
- [ ] HIPC 2020 health data safeguards
- [ ] Consent management system
- [ ] k-anonymity and differential privacy
- [ ] IRB protocol management
- [ ] Data export for researchers

### Phase 4 (Research)
- [ ] ML-based player modeling
- [ ] Churn prediction
- [ ] Engagement scoring
- [ ] Automated A/B testing

## Market Positioning

**WebTics is NOT:**
- A competitor to GameAnalytics (excellent free tier for general indie use)
- A full backend-as-a-service like PlayFab
- A mobile-first analytics platform like Firebase

**WebTics IS:**
- The privacy-first, self-hosted option
- The only NZ health data sovereign analytics platform
- An educational resource for learning game analytics
- A research-grade tool for serious games studies

## Contributing

Contributions welcome! Areas of interest:

- Unity SDK development
- Dashboard/visualization improvements
- Mobile platform optimizations
- Documentation and tutorials
- Example games and use cases

## License

- **SDKs and Client Libraries**: MIT License (maximum adoption)
- **Backend Services**: (TBD - considering AGPL to protect against cloud competitors)
- **Documentation**: CC BY 4.0

## Support

- **Documentation**: See `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/SimonMcCallum/WebTics/issues)
- **Email**: simon.mccallum@gmail.com

## Citation

If you use WebTics in research, please cite:

```bibtex
@incollection{mccallum2013webtics,
  author = {McCallum, Simon and Mackie, Jayson},
  title = {WebTics: A Web Based Telemetry and Metrics System for Small and Medium Games},
  booktitle = {Game Analytics: Maximizing the Value of Player Data},
  year = {2013},
  publisher = {Springer-Verlag London},
  pages = {169--193},
  doi = {10.1007/978-1-4471-4769-5_10}
}
```

## Acknowledgments

- Original WebTics concept: Simon McCallum & Jayson Mackie (2013)
- Prik's Game Metrics thesis: Yann Prik (2011)
- Modern assessment and implementation: Claude Sonnet 4.5 (2026)

---

**Status**: Beta - Proof of concept complete, production features in development

**Last Updated**: February 15, 2026