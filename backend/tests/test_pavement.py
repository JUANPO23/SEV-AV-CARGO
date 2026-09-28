from app.pavement import parse_pcn, pressure_limit_mpa
from app.demo import AIRCRAFT

def test_parse_pcn():
    p = parse_pcn("PCN 75/F/B/X/T")
    assert p and p.value == 75 and p.pavement_type == "F" and p.subgrade == "B"

def test_pressure_limit():
    assert pressure_limit_mpa("X") == 1.75

def test_aircraft_profile_seed():
    assert AIRCRAFT.variant == "A330-243F"
    assert AIRCRAFT.minimum_runway_length_m == 1400
