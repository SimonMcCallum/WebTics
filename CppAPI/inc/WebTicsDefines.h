
#ifndef _WEBTICS_EVENTS_
#define _WEBTICS_EVENTS_

#include <vector>
#include <string>

using namespace std;

namespace WebTicsDefines
{
    static const char*  versionLabel = "1.0";
    static const int    defaultI = -999999;
    static const double defaultD = -999999.f;

    enum eventTypes
    {
        PLAYER_DEATH = 0,
        PLAYER_RESPAWN,
        PLAYER_SHOOT,
        PLAYER_HIT,
        MAX_EVENT_TYPES
    };
    
    static const char* const eventTypeNames[MAX_EVENT_TYPES] = {
        "Player died",
        "Player respawed",
        "Player shoot",
        "Player hit"
    };

    enum eventSubtypes
    {
        RIFLE = 0,
        BULLET,
        GRENADE,
        MAX_EVENT_SUBTYPES
    };

    static const char* const eventSubtypeNames[MAX_EVENT_SUBTYPES] = {
        "Rifle",
        "Bullet",
        "Grenade"
    };
};

#endif