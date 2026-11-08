import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "service"))
from validation import validate_model_text

def test_valid_schema():
    value = validate_model_text('{"intent":"weather_query","date":null,"time":null,"place":"paris"}')
    assert value["place"] == "paris"

def test_invalid_intent():
    with pytest.raises(ValueError):
        validate_model_text('{"intent":"unknown","date":null,"time":null,"place":null}')

def test_extra_key():
    with pytest.raises(ValueError):
        validate_model_text('{"intent":"weather_query","date":null,"time":null,"place":null,"x":1}')

def test_slot_type():
    with pytest.raises(ValueError):
        validate_model_text('{"intent":"weather_query","date":7,"time":null,"place":null}')
