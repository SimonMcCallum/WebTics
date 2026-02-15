# Mobile Platform Support for WebTics

Guide for integrating WebTics telemetry in mobile games (Android and iOS).

## Overview

WebTics SDKs (Godot and Unreal Engine) work cross-platform including mobile with minimal platform-specific configuration. The main considerations are network permissions, data usage, and battery optimization.

## Android Integration

### Permissions

Add to `AndroidManifest.xml`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Internet access for telemetry -->
    <uses-permission android:name="android.permission.INTERNET"/>

    <!-- Check network state (optional, recommended) -->
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>

    <application>
        <!-- Your app configuration -->
    </application>
</manifest>
```

### Network Security Configuration (Android 9+)

For production, use HTTPS. For local testing, allow cleartext HTTP:

Create `res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Production: Use HTTPS only -->
    <base-config cleartextTrafficPermitted="false" />

    <!-- Development: Allow localhost cleartext (REMOVE IN PRODUCTION) -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">localhost</domain>
        <domain includeSubdomains="true">10.0.2.2</domain>  <!-- Android emulator host -->
        <domain includeSubdomains="true">192.168.1.100</domain>  <!-- Your dev server IP -->
    </domain-config>
</network-security-config>
```

Reference in `AndroidManifest.xml`:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config">
```

### Godot Export Settings (Android)

1. Project → Export → Android
2. Permissions:
   - Enable `INTERNET`
   - Enable `ACCESS_NETWORK_STATE` (optional)
3. Export and install APK

### Unreal Engine Android Settings

1. Edit → Project Settings → Platforms → Android
2. Android Package Name: `com.yourcompany.yourgame`
3. APK Packaging → Extra Permissions to Add:
   - `android.permission.INTERNET`
   - `android.permission.ACCESS_NETWORK_STATE`
4. Build and deploy

## iOS Integration

### App Transport Security (ATS)

iOS requires HTTPS by default. For local testing with HTTP:

Add to `Info.plist`:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <!-- Development: Allow all HTTP (REMOVE IN PRODUCTION) -->
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

**Production**: Remove `NSAllowsArbitraryLoads` and use HTTPS, or allow specific domains:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>webtics.yourdomain.com</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <false/>
            <key>NSExceptionRequiresForwardSecrecy</key>
            <true/>
            <key>NSIncludesSubdomains</key>
            <true/>
        </dict>
    </dict>
</dict>
```

### Godot Export Settings (iOS)

1. Project → Export → iOS
2. Bundle Identifier: `com.yourcompany.yourgame`
3. Custom Info.plist entries for ATS (see above)
4. Export Xcode project and build

### Unreal Engine iOS Settings

1. Edit → Project Settings → Platforms → iOS
2. Bundle Identifier: `com.yourcompany.yourgame`
3. Info.plist → Add `NSAppTransportSecurity` configuration
4. Build and deploy

## Platform-Specific Considerations

### Data Usage

Mobile users often have limited data plans. Best practices:

1. **Batch Events**: Use batch API instead of logging each event individually
   ```gdscript
   # Godot: Accumulate events and send batch
   var event_batch = []
   event_batch.append({
       "event_type": EventTypes.Type.PLAYER_DEATH,
       "x": position.x,
       "y": position.y
   })
   # Send when batch size reaches threshold or timer expires
   WebTics.log_events_batch(event_batch)
   ```

2. **WiFi Preference**: Detect network type and queue events for WiFi upload
   ```gdscript
   # GDScript example (requires custom native plugin or GDExtension)
   if is_wifi_connected():
       WebTics.log_event(...)
   else:
       queue_event_for_later(...)
   ```

3. **Compression**: Enable gzip in nginx (already configured in provided nginx.conf)

4. **Data Minimization**: Only log essential events on mobile

### Battery Optimization

HTTP requests consume battery. Optimize with:

1. **Event Batching**: Reduce number of HTTP requests
2. **Smart Timing**: Send batches during natural breaks (level complete, menu)
3. **Background Limits**: Don't log events when app is in background
4. **Connection Pooling**: Reuse HTTP connections (handled by SDK)

### Offline Support

Mobile games often go offline. Handle with:

1. **Local Queue**: Store events in SQLite when offline (Godot SDK planned feature)
2. **Sync on Reconnect**: Upload queued events when network returns
3. **Storage Limits**: Cap offline queue size (e.g., 1000 events or 1MB)

Example (pseudocode):

```gdscript
func log_event_with_offline_support(event):
    if is_online():
        WebTics.log_event(event)
    else:
        local_queue.append(event)
        save_queue_to_disk()

func on_network_reconnected():
    if local_queue.size() > 0:
        WebTics.log_events_batch(local_queue)
        local_queue.clear()
        delete_queue_from_disk()
```

### Network Detection

#### Godot

Requires platform-specific code or GDExtension. Use:

```gdscript
# Check if device is online (basic check)
func is_online() -> bool:
    var http = HTTPRequest.new()
    # Attempt small request to backend health endpoint
    # Return true if succeeds
    return true  # Simplified
```

#### Unreal Engine

```cpp
#include "Runtime/Online/HTTP/Public/HttpManager.h"

bool IsOnline()
{
    return FHttpModule::Get().GetHttpManager().IsHttpEnabled();
}

bool IsWiFiConnected()
{
    // Platform-specific implementation
    #if PLATFORM_ANDROID
        // Use JNI to call Android ConnectivityManager
    #elif PLATFORM_IOS
        // Use Objective-C to check Reachability
    #endif
    return false;
}
```

### Testing on Mobile Devices

#### Local Backend Access

Mobile devices can't access `localhost:8013`. Options:

1. **Use Device IP**: Configure backend URL to your computer's local IP
   ```gdscript
   WebTics.configure("http://192.168.1.100:8013")
   ```

2. **Use ngrok**: Tunnel localhost to public URL
   ```bash
   ngrok http 8013
   # Use the ngrok URL in your app: https://abc123.ngrok.io
   ```

3. **Deploy to Cloud**: Use production backend for testing

#### Android Emulator

- Host machine is accessible at `10.0.2.2`
- Configure: `WebTics.configure("http://10.0.2.2:8013")`

#### iOS Simulator

- Host machine is accessible at `localhost` (shares network with host)
- Configure: `WebTics.configure("http://localhost:8013")`

## Production Deployment Checklist

### Backend
- [ ] Deploy backend to cloud server with public IP or domain
- [ ] Configure HTTPS with valid SSL certificate (Let's Encrypt)
- [ ] Set up CORS to allow your mobile app's domain
- [ ] Enable gzip compression in nginx
- [ ] Set up monitoring and alerts

### Mobile App
- [ ] Use HTTPS backend URL (not HTTP)
- [ ] Remove `NSAllowsArbitraryLoads` from iOS Info.plist
- [ ] Remove cleartext traffic from Android network_security_config.xml
- [ ] Implement event batching
- [ ] Add offline queue support
- [ ] Test on real devices over cellular and WiFi
- [ ] Monitor data usage in analytics
- [ ] Battery testing under normal usage

## Platform-Specific SDKs (Future)

Currently, WebTics uses the game engine SDKs (Godot/Unreal). Future platform-specific SDKs:

### Native Android SDK (Kotlin)

Planned features:
- Background event syncing
- Native network detection
- Battery-aware scheduling
- Integration with Android JobScheduler

### Native iOS SDK (Swift)

Planned features:
- URLSession with background transfer
- Reachability monitoring
- Low Power Mode detection
- iOS privacy consent prompts

### React Native / Flutter

For hybrid mobile games:
- JavaScript/Dart SDK
- Cross-platform offline queue
- Native bridge for network detection

## Privacy Considerations (Mobile)

Mobile platforms have stricter privacy requirements:

### iOS App Store
- Declare data collection in App Privacy section
- Obtain user consent before collecting telemetry
- Provide data deletion mechanism
- Comply with Apple's privacy guidelines

### Google Play Store
- Complete Data Safety section
- Declare data types collected
- Explain purpose of data collection
- Provide privacy policy URL

### GDPR/COPPA Compliance
- Implement consent dialogs
- Allow data export and deletion
- Age gate for children's games
- Document data retention policies

Example consent flow:

```gdscript
func show_consent_dialog():
    var dialog = AcceptDialog.new()
    dialog.dialog_text = """
    This game collects anonymous gameplay data to improve your experience.

    We collect:
    - Gameplay events (level complete, scores)
    - Device type (for compatibility)
    - Session duration

    We do NOT collect:
    - Personal information
    - Location data
    - Contacts or photos

    Data is stored securely and never sold to third parties.

    Accept data collection?
    """
    dialog.add_button("Accept", true, "accept")
    dialog.add_button("Decline", false, "decline")
    dialog.custom_action.connect(_on_consent_response)
    add_child(dialog)
    dialog.popup_centered()

func _on_consent_response(action):
    if action == "accept":
        # Enable WebTics
        WebTics.open_metric_session(player_id)
    else:
        # Disable telemetry
        pass
```

## Performance Benchmarks (Mobile)

Target metrics for mobile telemetry:

- **Event Logging Latency**: < 5ms (non-blocking)
- **Batch Upload Time**: < 500ms for 100 events over WiFi
- **Battery Impact**: < 1% over 1 hour of gameplay
- **Data Usage**: < 100KB per hour of gameplay (with batching)
- **Storage**: < 1MB for offline queue

## Support and Resources

- **WebTics Backend**: See `/TESTING.md` for deployment
- **Godot Mobile Export**: [Godot Docs - Exporting](https://docs.godotengine.org/en/stable/tutorials/export/)
- **Unreal Mobile**: [UE Docs - Mobile Development](https://docs.unrealengine.com/5.0/en-US/mobile-development-in-unreal-engine/)
- **Android Permissions**: [Android Developer Guide](https://developer.android.com/guide/topics/permissions/overview)
- **iOS Privacy**: [Apple App Privacy](https://developer.apple.com/app-store/user-privacy-and-data-use/)

## Example Mobile Games Using WebTics

See `examples/mobile/` for complete mobile game examples:
- `reaction_time_mobile/` - Android/iOS ADHD assessment
- `platformer_mobile/` - Cross-platform action game with telemetry
