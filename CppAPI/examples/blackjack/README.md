# WebTics Blackjack Server

A complete text-based blackjack game server with integrated WebTics telemetry tracking. This example demonstrates how to integrate WebTics into a real application to track game events, player behavior, and game statistics.

## Overview

This blackjack implementation showcases WebTics telemetry integration by logging:
- **Game Events**: Start, end, hand dealt, wins/losses
- **Player Actions**: Hit, stand, bust, blackjack
- **Dealer Actions**: Turn start, hit, stand, bust
- **Betting**: Bet amounts and outcomes
- **Card Dealing**: Individual card tracking with suit and value
- **Statistics**: Win rates, chip counts, game progression

## Features

### Game Features
- Standard blackjack rules (dealer hits on 16, stands on 17+)
- Blackjack pays 3:2
- Multiple hands per session
- Chip/betting system (starts with $1000)
- Automatic deck reshuffling
- Real-time statistics

### Telemetry Features
- **15 Custom Event Types** defined for blackjack
- Session management (metric sessions and play sessions)
- Event logging with magnitude and custom data strings
- Real-time telemetry upload to WebTics server
- Comprehensive game state tracking

## Custom Event Types

The blackjack server defines custom events in `BlackjackEvents.h`:

```cpp
GAME_START = 100        // New game started
GAME_END                // Game ended
HAND_DEALT              // Initial cards dealt
PLAYER_HIT              // Player requested a card
PLAYER_STAND            // Player stands
PLAYER_BUST             // Player busted (over 21)
PLAYER_BLACKJACK        // Player got blackjack
DEALER_TURN             // Dealer's turn started
DEALER_HIT              // Dealer drew a card
DEALER_BUST             // Dealer busted
PLAYER_WIN              // Player won the hand
PLAYER_LOSE             // Player lost the hand
PLAYER_PUSH             // Push (tie)
BET_PLACED              // Bet was placed
CARD_DEALT              // Individual card dealt
```

## Building the Server

### Prerequisites
- Windows OS (uses WinHTTP API)
- Visual Studio 2015 or later
- WebTics C++ API (included in parent directory)
- WAMP/LAMP server for telemetry backend (optional for testing)

### Compilation

#### Using Visual Studio

1. Open Visual Studio
2. Create a new C++ Console Application project
3. Add the following files to your project:
   - `BlackjackServer.cpp`
   - `BlackjackEvents.h`
   - `../../inc/WebTics.h`
   - `../../inc/WebTicsDefines.h`
   - `../../src/WebTics.cpp`

4. Configure project settings:
   - **Platform**: Windows (x86 or x64)
   - **Additional Include Directories**: Add `../../inc`
   - **Additional Libraries**: Add `Winhttp.lib`
   - **Preprocessor Definitions**: Add `_CRT_SECURE_NO_WARNINGS` if needed

5. Build the solution (F7 or Build > Build Solution)
6. Run the executable

#### Using Command Line (cl.exe)

```bash
cl BlackjackServer.cpp ..\..\src\WebTics.cpp /I..\..\inc /link Winhttp.lib
```

#### Using Makefile (MinGW on Windows)

```bash
g++ -o BlackjackServer BlackjackServer.cpp ../../src/WebTics.cpp -I../../inc -lwinhttp -std=c++11
```

## Running the Server

### Without WebTics Backend (Standalone Mode)

You can run the blackjack server without a WebTics backend server. The game will function normally, but telemetry HTTP requests will fail silently. The game logic is independent of the telemetry system.

```bash
./BlackjackServer.exe
```

### With WebTics Backend (Full Telemetry)

1. Set up a WAMP/LAMP server with the WebTics PHP backend
2. Configure the MySQL database (see main WebTics documentation)
3. Update the server address in `BlackjackServer.cpp` if needed:
   ```cpp
   string server = "localhost";  // Change to your server IP
   string path = "/WebTics/";    // Change to your WebTics path
   ```
4. Run the server:
   ```bash
   ./BlackjackServer.exe
   ```
5. View telemetry data in the WebTics visualization dashboard

## Gameplay Instructions

1. **Start the game**: Run the executable
2. **Place bet**: Enter bet amount (or 0 to quit)
3. **Player turn**: Choose (H)it or (S)tand
4. **Dealer turn**: Automatic play (hits on 16, stands on 17+)
5. **Results**: View winner and chip count
6. **Repeat**: Continue playing or quit (bet 0)

### Example Session

```
=== WebTics Blackjack Server ===
Initializing WebTics telemetry system...
WebTics telemetry active!

Starting chips: $1000

==================================================
You have $1000 in chips.
Enter bet amount (or 0 to quit): $100

--- Your Turn ---

Dealer shows: Seven of Hearts
Your hand:
  Cards: King of Spades, Nine of Diamonds (Value: 19)

(H)it or (S)tand? s

--- Dealer's Turn ---
Dealer reveals:
  Cards: Seven of Hearts, Queen of Clubs (Value: 17)

Dealer stands at 17

=== Results ===
Your hand: 19
Dealer hand: 17

You WIN!

Current chips: $1100
```

## Telemetry Data Collected

For each game session, the following data is tracked:

### Per-Hand Metrics
- Hand number
- Initial cards dealt (player and dealer)
- Player actions (hit/stand decisions)
- Dealer actions (automatic play)
- Final hand values
- Outcome (win/loss/push)
- Bet amount and payout

### Per-Card Metrics
- Card rank and suit
- Recipient (player or dealer)
- Card value contribution

### Session Statistics
- Total hands played
- Win/loss/push counts
- Win rate percentage
- Chip balance over time
- Net gain/loss

## Viewing Telemetry Data

Once the WebTics backend is set up, you can:

1. **Database Queries**: Query MySQL `eventdata` table for raw telemetry
2. **Heatmaps**: Not applicable for blackjack (no spatial data)
3. **Custom Dashboards**: Build custom visualizations using event types
4. **Statistical Analysis**: Export data for analysis in R, Python, Excel, etc.

### Example Database Query

```sql
SELECT et, est, m, data, tick
FROM eventdata
WHERE metricSessionMD5 = 'your_session_id'
ORDER BY tick ASC;
```

## Code Structure

### Files
- **BlackjackServer.cpp** (450+ lines) - Main game implementation
  - `Card` struct - Card representation
  - `Deck` class - Deck management and shuffling
  - `Hand` class - Hand evaluation and display
  - `BlackjackGame` class - Game logic and WebTics integration
  - `main()` - Entry point

- **BlackjackEvents.h** (80 lines) - Custom event definitions
  - Event type enumerations
  - Card suit/rank definitions
  - Event name strings for logging

### Key Classes

#### BlackjackGame
Main game controller with WebTics integration:
- `initialize()` - Sets up WebTics connection
- `placeBet()` - Handles betting and logs bet events
- `dealInitialCards()` - Deals initial hand and logs cards
- `playerTurn()` - Player decision loop with event logging
- `dealerTurn()` - Dealer automatic play with logging
- `determineWinner()` - Outcome evaluation and logging
- `playHand()` - Complete hand workflow
- `run()` - Main game loop
- `displayStatistics()` - Final stats summary

## Extending the Example

This example can be extended in several ways:

### Additional Features
- **Multiple players**: Track multiple simultaneous players
- **Split hands**: Implement split functionality
- **Double down**: Add double down betting option
- **Insurance**: Add insurance betting
- **Shoe system**: Multi-deck shoe with cut card
- **Advanced strategy**: Track optimal play vs. actual play

### Additional Telemetry
- **Decision quality**: Log whether player made optimal decision
- **Timing data**: Track time taken for each decision
- **Betting patterns**: Analyze betting behavior over time
- **Card counting metrics**: Track true count (educational purposes)
- **Session duration**: Track total play time
- **Heat maps**: (With position data) Track betting patterns by position

### Integration Ideas
- **Web interface**: Convert to WebSocket server for browser clients
- **Mobile app**: Create mobile blackjack with telemetry
- **Tournament mode**: Track multi-player tournament statistics
- **AI opponent**: Implement AI players and track their performance

## Troubleshooting

### Build Issues

**Error: Cannot open include file 'WebTics.h'**
- Solution: Ensure include path `../../inc` is set correctly
- Check that WebTics.h exists in `/CppAPI/inc/`

**Error: Unresolved external symbol WinHttpOpen**
- Solution: Add `Winhttp.lib` to linker dependencies
- Visual Studio: Project Properties > Linker > Input > Additional Dependencies

**Error: 'string' does not name a type**
- Solution: Add `using namespace std;` or use `std::string`
- Ensure `#include <string>` is present

### Runtime Issues

**WebTics connection fails**
- The game will continue to work, but telemetry will not be logged
- Check that the WebTics server URL is correct
- Verify WAMP/LAMP server is running
- Check firewall settings

**Deck runs out of cards**
- Automatic reshuffling should occur
- Check console for "[Reshuffling deck...]" message

**Invalid bet amounts**
- Enter only positive integers within chip balance
- Bet 0 to quit the game

## Performance Notes

- **Network overhead**: Each event triggers an HTTP request
  - For production, consider batching events or using async requests
  - Current implementation uses synchronous WinHTTP calls

- **Memory usage**: Minimal (<1 MB typical)
  - Deck stored as vector of 52 cards
  - Hands stored as small vectors (typically 2-6 cards)

- **CPU usage**: Negligible for game logic
  - Most overhead is from HTTP requests to telemetry server

## Academic Use

This example is suitable for:
- **Game development courses**: Example of event-driven telemetry
- **Data analytics courses**: Real gameplay data generation
- **Statistics courses**: Probability and outcome analysis
- **Software engineering courses**: Integration patterns and API usage
- **Research projects**: Player behavior studies

## License

Same as WebTics - Open source for educational and commercial use.

## Credits

Built as a demonstration of WebTics telemetry integration.

---

**Happy Gaming and Happy Tracking!**
