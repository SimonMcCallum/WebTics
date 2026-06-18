"""GA4 / Apple-style named-event registry.

Bridges the new named-event API (``level_up``, ``post_score``, ...) to WebTics' existing
integer ``event_type`` codes (see ``sdk/godot/addons/webtics/EventTypes.gd``). Unknown /
custom names fall through to the ``CUSTOM`` bucket (1000) with the original name preserved
in the event's ``data`` JSON, so nothing is ever lost.

Names are deliberately aligned with Google Analytics 4 recommended events and Apple's
App Analytics vocabulary so students' instincts transfer to those paid tools later.
"""

CUSTOM_EVENT_TYPE = 1000

# name -> (event_type, event_subtype). Subtype 0 unless a meaningful split exists.
NAME_TO_CODE: dict[str, tuple[int, int]] = {
    # Lifecycle / engagement (GA4 automatic + Apple session events)
    "session_start": (100, 0),
    "session_end": (101, 0),
    "screen_view": (21, 0),
    "first_open": (100, 1),
    "app_open": (100, 2),
    "user_engagement": (202, 0),
    # Gameplay (GA4 "games" recommended events)
    "level_start": (100, 0),
    "level_end": (101, 0),
    "level_up": (11, 0),
    "level_complete": (11, 0),
    "level_failed": (12, 0),
    "post_score": (101, 3),
    "unlock_achievement": (101, 4),
    "tutorial_begin": (100, 5),
    "tutorial_complete": (101, 5),
    "checkpoint": (10, 0),
    "waypoint_reached": (10, 0),
    # Player actions
    "player_death": (0, 0),
    "player_respawn": (1, 0),
    "player_shoot": (2, 0),
    "player_hit": (3, 0),
    # UI / navigation
    "button_click": (20, 0),
    "select_content": (20, 0),
    "menu_open": (21, 0),
    "menu_close": (22, 0),
    # Monetisation (GA4 ecommerce — kept for skill transfer even if unused in coursework)
    "purchase": (300, 0),
    "in_app_purchase": (300, 0),
    "ad_impression": (301, 0),
    # Assessment / research
    "correct_response": (102, 0),
    "incorrect_response": (103, 0),
    "timeout": (104, 0),
}

# Params commonly carrying spatial / scalar data — auto-promoted into table columns
# so existing dashboards/queries keep working.
COORD_PARAM_KEYS = {"x": "x", "y": "y", "z": "z"}
MAGNITUDE_PARAM_KEYS = ("value", "score", "magnitude", "reaction_time_ms", "amount")


def resolve_event_type(name: str) -> tuple[int, int]:
    """Map a GA4-style name to (event_type, event_subtype)."""
    return NAME_TO_CODE.get(name.lower(), (CUSTOM_EVENT_TYPE, 0))


def _coerce_int(v):
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def _coerce_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def extract_columns(params: dict) -> dict:
    """Pull x/y/z + magnitude out of the params map into typed columns.

    The full params map is still stored in ``data`` (lossless); this just makes the
    common analytics fields queryable in the existing schema.
    """
    out = {"x": None, "y": None, "z": None, "magnitude": None}
    for src, dest in COORD_PARAM_KEYS.items():
        if src in params:
            out[dest] = _coerce_int(params[src])
    for key in MAGNITUDE_PARAM_KEYS:
        if key in params:
            out["magnitude"] = _coerce_float(params[key])
            break
    return out


def known_event_names() -> list[str]:
    return sorted(NAME_TO_CODE.keys())
