import json

INTENTS = {
    "alarm_set", "alarm_query", "calendar_set", "calendar_query",
    "calendar_remove", "weather_query", "datetime_query", "recommendation_events",
}
EXPECTED_KEYS = {"intent", "date", "time", "place"}

def validate_model_text(raw: str) -> dict:
    value = json.loads(raw)
    if not isinstance(value, dict) or set(value) != EXPECTED_KEYS:
        raise ValueError("output must contain exactly four required keys")
    if value["intent"] not in INTENTS:
        raise ValueError("intent is outside the allowed set")
    for slot in ("date", "time", "place"):
        if value[slot] is not None and not isinstance(value[slot], str):
            raise ValueError(f"{slot} must be a string or null")
    return value
