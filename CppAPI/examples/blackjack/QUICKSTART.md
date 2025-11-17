# Quick Start Guide - WebTics Blackjack Server

Get up and running with the WebTics Blackjack example in 5 minutes!

## Option 1: Visual Studio (Recommended for Windows)

### Step 1: Open Visual Studio Developer Command Prompt
- Start Menu → Visual Studio 2019 → Developer Command Prompt
- Or run `vcvarsall.bat` from your Visual Studio installation

### Step 2: Navigate to the Blackjack Directory
```cmd
cd WebTics\CppAPI\examples\blackjack
```

### Step 3: Run the Build Script
```cmd
build.bat
```

### Step 4: Run the Server
```cmd
BlackjackServer.exe
```

## Option 2: MinGW (Alternative)

### Step 1: Install MinGW
Download and install MinGW with g++ support from mingw.org

### Step 2: Navigate to the Blackjack Directory
```cmd
cd WebTics\CppAPI\examples\blackjack
```

### Step 3: Build with Make
```cmd
make
```

### Step 4: Run the Server
```cmd
make run
```

## Option 3: Manual Compilation

### Using Visual Studio Compiler (cl.exe)
```cmd
cl /EHsc /std:c++14 /I..\..\inc BlackjackServer.cpp ..\..\src\WebTics.cpp /Fe:BlackjackServer.exe /link Winhttp.lib
```

### Using MinGW (g++)
```cmd
g++ -std=c++11 -I../../inc -o BlackjackServer.exe BlackjackServer.cpp ../../src/WebTics.cpp -lwinhttp
```

## Playing the Game

1. **Start the game** - Run `BlackjackServer.exe`
2. **Place a bet** - Enter an amount (e.g., 100) or 0 to quit
3. **Play your hand** - Type `h` to hit, `s` to stand
4. **View results** - See if you won, lost, or pushed
5. **Continue playing** - Repeat until you run out of chips or quit

### Example Session

```
=== WebTics Blackjack Server ===
Initializing WebTics telemetry system...

You have $1000 in chips.
Enter bet amount (or 0 to quit): $50

--- Your Turn ---
Dealer shows: 7 of Hearts
Your hand:
  Cards: King of Spades, 6 of Diamonds (Value: 16)

(H)it or (S)tand? h

You drew: 4 of Clubs
Your hand:
  Cards: King of Spades, 6 of Diamonds, 4 of Clubs (Value: 20)

(H)it or (S)tand? s

--- Dealer's Turn ---
Dealer reveals:
  Cards: 7 of Hearts, 9 of Clubs (Value: 16)

Dealer hits...
Dealer drew: 10 of Spades

Dealer BUSTS!

=== Results ===
You WIN! (Dealer bust)

Current chips: $1050
```

## Telemetry Integration

The blackjack server automatically logs all game events to WebTics:

### What's Being Tracked?
- Every card dealt
- Every player decision (hit/stand)
- Every bet placed
- Game outcomes (win/loss/push)
- Dealer actions
- Player statistics

### Viewing Telemetry (Optional)

To view telemetry data, you need a WebTics backend server:

1. **Install WAMP/LAMP**
   - Download WAMP (Windows) or LAMP (Linux)
   - Install Apache, MySQL, and PHP

2. **Set up WebTics Backend**
   - Copy PHP files to web server directory
   - Configure MySQL database
   - See main WebTics documentation

3. **Update Server Address** (if not localhost)
   - Edit `BlackjackServer.cpp`
   - Change line: `string server = "localhost";`
   - Rebuild the application

4. **View Data**
   - Access WebTics web interface
   - Query MySQL database directly
   - Export data for analysis

### Running Without Telemetry Backend

The game works perfectly fine without a WebTics backend server! The telemetry HTTP requests will simply fail silently, and the game will continue normally. This allows you to:
- Test the game immediately without setup
- Play offline
- Focus on the game logic without infrastructure

## Troubleshooting

### "cl.exe not found"
**Solution**: Run from Visual Studio Developer Command Prompt

### "Cannot open include file 'WebTics.h'"
**Solution**: Ensure you're in the correct directory (`CppAPI/examples/blackjack`)

### "Unresolved external symbol WinHttpOpen"
**Solution**: Add `Winhttp.lib` to linker: `/link Winhttp.lib`

### Connection to localhost fails
**Solution**: This is normal if you don't have a WebTics backend. The game will still work!

## Next Steps

- Read the full [README.md](README.md) for detailed information
- Explore the source code in `BlackjackServer.cpp`
- Modify event types in `BlackjackEvents.h`
- Set up a WebTics backend to view telemetry data
- Extend the game with new features (splits, insurance, etc.)

## Need Help?

- Check the main WebTics documentation in `/docs`
- Review the sample usage in `/CppAPI/src/SampleUsage.cpp`
- Open an issue on the GitHub repository

---

**Have fun playing and tracking!**
