# WebTics - Web-Based Game Telemetry & Metrics System

[![License](https://img.shields.io/badge/license-Open%20Source-blue.svg)]()

## Overview

**WebTics** is a comprehensive web-based telemetry and metrics collection system designed for video game developers. It provides real-time tracking, storage, and visualization of in-game player behavior, enabling data-driven game design, balance analysis, bug detection, and A/B testing.

Originally developed as an open-source alternative to commercial services like Playtomic, WebTics offers small to medium-sized game studios a drop-in solution for collecting and analyzing player telemetry without subscription fees.

## Key Features

- **Real-time Telemetry Collection** - Track player positions, actions, events, and custom metrics
- **Visual Analytics** - Interactive heatmaps using D3.js and heatmap.js for spatial data visualization
- **A/B Testing** - Dynamic parameter requests allow server-controlled game variable testing
- **Game Balance Analysis** - Identify dominant strategies, overpowered weapons, and design issues
- **Bug Detection** - Discover crash patterns and problematic game areas through behavioral data
- **Event Logging System** - Flexible event types with subtypes, magnitudes, and custom data
- **Version Tracking** - Build and version control integration for longitudinal studies
- **Privacy Controls** - Authorization system for GDPR compliance and player data protection
- **Debug Mode** - Conditional logging for development vs. production environments

## Architecture

### Client-Side (Game Integration)
```
Game Code → WebTics C++ API → HTTP Requests → Web Server → MySQL Database
```

The system uses a **Singleton pattern** C++ API that communicates with PHP backend endpoints via HTTP.

### Server-Side Components
- **PHP Backend** - RESTful-style endpoints for session management and event logging
- **MySQL Database** - Stores metric sessions, play sessions, and event data
- **JavaScript Frontend** - Real-time visualization with heatmaps and filtering

### Communication Flow
1. **Initialize** - Connect to metrics server (localhost or remote)
2. **Open Metric Session** - Establish session with unique ID (returns MD5 hash)
3. **Register Events** - Define event types and subtypes (version-specific)
4. **Start Play Session** - Begin gameplay tracking
5. **Log Events** - Continuous event logging with position, type, magnitude, timestamp
6. **Stop Play Session** - End gameplay tracking
7. **Close Metric Session** - Disconnect from server

## Quick Start

### Prerequisites
- C++ compiler (Visual Studio on Windows)
- WAMP/LAMP server (Apache, MySQL, PHP)
- Web browser for visualization

### Basic Integration Example

```cpp
#include "WebTics.h"
#include "WebTicsDefines.h"

// Initialize WebTics
WebTics* metrics = WebTics::getInstance();
metrics->initialize("localhost", "myGame", "1.0");

// Open metric session
std::string sessionID = metrics->openMetricSession();

// Register event types
metrics->registerEvent(PLAYER_DEATH, "Player Death Event");
metrics->registerEvent(PLAYER_SHOOT, "Player Shoot Event");

// Start play session
metrics->startPlaySession();

// Log events during gameplay
metrics->LogEvent(PLAYER_SHOOT, RIFLE, playerX, playerY, playerZ, damage);
metrics->LogEvent(PLAYER_DEATH, enemyX, enemyY, enemyZ);

// Stop play session
metrics->stopPlaySession();

// Close metric session
metrics->closeMetricSession();
```

## Event Types

### Pre-defined Events
```cpp
PLAYER_DEATH = 0     // Player death event
PLAYER_RESPAWN = 1   // Player respawn event
PLAYER_SHOOT = 2     // Player shooting event
PLAYER_HIT = 3       // Player hit event
```

### Event Subtypes (e.g., Weapons)
```cpp
RIFLE = 0
BULLET = 1
GRENADE = 2
```

### Flexible LogEvent API
```cpp
// Full version with all parameters
LogEvent(type, subtype, x, y, z, magnitude, customData)

// Position and magnitude
LogEvent(type, subtype, x, y, z, magnitude)

// Position only
LogEvent(type, subtype, x, y, z)

// Magnitude only
LogEvent(type, magnitude)

// Custom data string
LogEvent(type, customData)

// Debug versions (only log when _DEBUG is defined)
LogEventDebug(...)
```

## Use Cases

1. **Game Balance** - Identify weapon imbalances and dominant strategies
2. **Level Design** - Optimize map layouts based on player movement patterns
3. **Quality Assurance** - Track crashes and bugs through player behavior
4. **Player Research** - Study learning curves and skill progression
5. **A/B Testing** - Compare different game parameters across player groups
6. **Academic Studies** - Research player behavior in serious games

## Example Projects

### Blackjack Server (Test Case)
See `/CppAPI/examples/blackjack/` for a complete text-based blackjack server implementation with WebTics telemetry integration. This demonstrates:
- Session management
- Event logging for game actions (deal, hit, stand, bust, win/loss)
- Custom metrics tracking (bet amounts, card values, outcomes)
- Real-time telemetry during gameplay

## Technical Details

### Technology Stack
- **C++** - Client-side API (Windows WinHTTP)
- **PHP** - Server-side backend
- **MySQL** - Database storage
- **JavaScript** - Frontend visualization (D3.js, heatmap.js)
- **HTML** - Web interface

### Database Schema
- `metricession` - Metric session management
- `playsession` - Play session tracking
- `eventdata` - Event storage (positions, types, timestamps, magnitudes)

### PHP Endpoints
- `openMetricSession.php` - Session initialization
- `closeMetricSession.php` - Session termination
- `registerEvents.php` - Event type registration
- `startPlaySession.php` - Play session start
- `stopPlaySession.php` - Play session end
- `logEvent.php` - Event logging
- `requestParameters.php` - Dynamic parameter requests (A/B testing)
- `isAuthorised.php` / `setAuthorised.php` - Authorization management

## Documentation

- **[Webtics.pdf](/docs/Webtics.pdf)** - Comprehensive paper on game metrics and sampling strategies (9.1MB)
- **[Prik_Game_Metrics.pdf](/docs/Prik_Game_Metrics.pdf)** - Student project report implementing WebTics with Quake III (438KB)
- **[Architecture Diagram](/Untitled%20Diagram.svg)** - System architecture visualization

## Platform Support

Currently supports **Windows** platforms using the WinHTTP API. Cross-platform support (Linux/Mac) can be added by replacing WinHTTP with libcurl or similar HTTP libraries.

## License

Open source project - Free for educational and commercial use by small developers.

## Contributing

Contributions are welcome! Areas for improvement:
- Cross-platform HTTP library integration
- Additional visualization types (graphs, timelines, player paths)
- Enhanced filtering and query capabilities
- Map background overlay support
- Real-time dashboard improvements

## Academic Use

WebTics has been used in academic research on game analytics and player behavior. If you use WebTics in your research, please cite the original documentation.

## Contact & Support

For questions, bug reports, or feature requests, please open an issue on this repository.

---

**WebTics** - Making game telemetry accessible to everyone.