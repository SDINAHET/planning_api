from datetime import datetime

from app.programme_repository import (
    normalize_room,
    format_hour,
    parse_one,
    parse_slot_datetime,
)


def test_normalize_room():
    assert normalize_room("Amphi C (principal)") == "Amphi C"
    assert normalize_room("Amphi principal") == "Amphi C"
    assert normalize_room("Amphi principal (D)") == "Amphi D"


def test_format_hour():
    dt = datetime(2026, 6, 24, 10, 30)

    assert format_hour(dt) == "10h30"


def test_parse_one():
    dt = parse_one("2026-06-24", "10h30")

    assert dt.hour == 10
    assert dt.minute == 30


def test_parse_slot():
    start, end = parse_slot_datetime("2026-06-24", "10h30-12h25")

    assert start.hour == 10
    assert end.hour == 12
