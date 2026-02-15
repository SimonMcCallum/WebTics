# WebTics Unreal Engine Plugin

Lightweight telemetry and metrics system for Unreal Engine games.

## Features

- ✅ **Cross-Platform**: Windows, Linux, Mac, Android, iOS
- ✅ **Blueprint Support**: Full Blueprint exposure for all functions
- ✅ **Async Operations**: Non-blocking HTTP requests with delegates
- ✅ **Game Instance Subsystem**: Automatic lifecycle management
- ✅ **Event Types**: Predefined event types for common game actions
- ✅ **Position Logging**: Helper functions for 3D position tracking
- ✅ **Privacy-First**: Self-hosted backend, full data control

## Installation

### Method 1: Plugin Directory

1. Copy the `WebTics` folder to your project's `Plugins/` directory
2. Regenerate project files (right-click `.uproject` → Generate Visual Studio project files)
3. Compile your project
4. Enable the plugin in Edit → Plugins → Analytics → WebTics

### Method 2: Engine Plugins (Global)

1. Copy the `WebTics` folder to `UE_5.x/Engine/Plugins/`
2. Restart Unreal Editor
3. Enable in Edit → Plugins

## Quick Start (C++)

```cpp
#include "WebTicsSubsystem.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // Get the WebTics subsystem
    UWebTicsSubsystem* WebTics = GetGameInstance()->GetSubsystem<UWebTicsSubsystem>();

    // Configure backend URL
    WebTics->Configure("http://localhost:8000");

    // Open metric session
    WebTics->OpenMetricSession("player_123", "1.0.0");

    // Bind to session created delegate
    WebTics->OnSessionCreated.AddDynamic(this, &AMyGameMode::OnWebTicsSessionCreated);
}

void AMyGameMode::OnWebTicsSessionCreated(int32 SessionId)
{
    UWebTicsSubsystem* WebTics = GetGameInstance()->GetSubsystem<UWebTicsSubsystem>();

    // Start play session
    WebTics->StartPlaySession();
}

void AMyCharacter::OnDeath()
{
    UWebTicsSubsystem* WebTics = GetGameInstance()->GetSubsystem<UWebTicsSubsystem>();

    // Log death event with position
    WebTics->LogEventAtPosition(
        EWebTicsEventType::PLAYER_DEATH,
        GetActorLocation(),
        0.0f  // magnitude
    );
}
```

## Quick Start (Blueprints)

1. **Get WebTics Subsystem**:
   - Get Game Instance → Get Subsystem (UWebTicsSubsystem)

2. **Configure and Start Session**:
   - Call `Configure` with your backend URL
   - Call `Open Metric Session` with unique player ID
   - Bind to `On Session Created` event
   - In the event handler, call `Start Play Session`

3. **Log Events**:
   - Call `Log Event` with event type and parameters
   - Or use `Log Event At Position` for location-based events

4. **Clean Up**:
   - Call `Close Play Session` when gameplay ends
   - Call `Close Metric Session` on exit

## Event Types

The plugin includes predefined event types:

- **Player Events**: Death, Respawn, Shoot, Hit
- **Navigation**: Waypoint Reached, Level Complete/Failed
- **UI**: Button Click, Menu Open/Close
- **Assessment**: Task Start/Complete, Correct/Incorrect Response, Timeout
- **ADHD Assessment**: Attention Task, Impulsive Response, Sustained/Selective Attention
- **Custom**: For game-specific events

## API Reference

### Configure
```cpp
void Configure(const FString& URL)
```
Set the WebTics backend URL.

### OpenMetricSession
```cpp
void OpenMetricSession(const FString& UniqueID, const FString& BuildNumber = "")
```
Create a new metric session. Fires `OnSessionCreated` delegate.

### CloseMetricSession
```cpp
void CloseMetricSession()
```
Close the current metric session.

### StartPlaySession
```cpp
void StartPlaySession()
```
Start a new play session. Fires `OnPlaySessionCreated` delegate.

### ClosePlaySession
```cpp
void ClosePlaySession()
```
Close the current play session.

### LogEvent
```cpp
void LogEvent(
    EWebTicsEventType EventType,
    int32 EventSubtype = 0,
    int32 X = 0,
    int32 Y = 0,
    int32 Z = 0,
    float Magnitude = 0.0f,
    const TMap<FString, FString>& AdditionalData = {}
)
```
Log a telemetry event with optional position, magnitude, and custom data.

### LogEventAtPosition
```cpp
void LogEventAtPosition(
    EWebTicsEventType EventType,
    FVector Position,
    float Magnitude = 0.0f,
    int32 EventSubtype = 0
)
```
Log an event at a specific 3D position.

## Delegates

Connect to these delegates for async feedback:

- `OnSessionCreated(int32 SessionId)` - Metric session created
- `OnPlaySessionCreated(int32 PlaySessionId)` - Play session created
- `OnEventLogged(bool bSuccess)` - Event logged successfully
- `OnWebTicsError(FString ErrorMessage)` - Error occurred

## Blueprint Example

See `Content/Examples/BP_WebTicsExample` for a complete Blueprint implementation.

## Mobile Platform Support (Android/iOS)

The plugin works on mobile platforms with no code changes. Add these permissions:

### Android (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
```

### iOS (Info.plist)
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

**Note**: For production, use HTTPS and restrict to your domain instead of allowing arbitrary loads.

## Performance Considerations

- Events are sent asynchronously and don't block game thread
- Consider batching events for high-frequency logging
- Mobile: Monitor data usage, use WiFi when possible
- Battery: Event logging has minimal battery impact

## Troubleshooting

### Events not appearing in backend

1. Check backend is running: `curl http://localhost:8000/`
2. Verify `Configure()` called with correct URL
3. Ensure session and play session created before logging
4. Check Output Log for WebTics errors
5. Verify CORS headers in backend allow your domain

### Compile errors

1. Ensure HTTP, Json, JsonUtilities modules in Build.cs
2. Regenerate project files
3. Clean and rebuild solution

## Example: ADHD Assessment Game

```cpp
void UReactionTestWidget::OnTargetClicked()
{
    UWebTicsSubsystem* WebTics = GetGameInstance()->GetSubsystem<UWebTicsSubsystem>();

    float ReactionTime = GetWorld()->GetTimeSeconds() - TaskStartTime;

    TMap<FString, FString> Data;
    Data.Add("trial", FString::FromInt(CurrentTrial));
    Data.Add("reaction_time_ms", FString::SanitizeFloat(ReactionTime * 1000.0f));

    WebTics->LogEvent(
        EWebTicsEventType::CORRECT_RESPONSE,
        0,  // subtype
        0, 0, 0,  // position (not used for UI)
        ReactionTime,  // magnitude
        Data
    );
}
```

## License

MIT License - See LICENSE file for details

## Support

- Documentation: [WebTics GitHub](https://github.com/SimonMcCallum/WebTics)
- Issues: [GitHub Issues](https://github.com/SimonMcCallum/WebTics/issues)
- Backend Setup: See `/TESTING.md` in repository
