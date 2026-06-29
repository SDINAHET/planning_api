from app.main import (
    format_date_fr,
    add_display_dates,
)


def test_format_date():
    assert format_date_fr("2026-06-24") == "24/06/2026"


def test_add_display_dates():
    slots = [{
        "date": "2026-06-24"
    }]

    result = add_display_dates(slots)

    assert result[0]["date_fr"] == "24/06/2026"
