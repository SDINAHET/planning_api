from datetime import datetime

from app.programme_scraper import (
    clean_line,
    is_time_line,
    is_room_text,
    parse_time,
    extract_summary_from_lines,
    deduplicate_talks,
    extract_title_from_card,
    extract_speaker_from_card,
    parse_talk_card,
    get_lines,
)


def test_clean_line():
    assert clean_line("  Bonjour   monde ") == "Bonjour monde"


def test_is_time_line():
    assert is_time_line("10h-12h")
    assert is_time_line("10h30 — 12h25")
    assert not is_time_line("Accueil")


def test_is_room_text():
    assert is_room_text("Amphi A")
    assert is_room_text("Amphi principal")
    assert not is_room_text("Accueil")


def test_parse_time():
    result = parse_time("2026-06-24", "10h30")

    assert result == datetime(2026, 6, 24, 12, 30)


def test_extract_summary():
    lines = [
        "Titre",
        "Description",
        "Ligne 1",
        "Ligne 2",
        "Orateur·ices",
        "Nom",
    ]

    assert extract_summary_from_lines(lines) == "Ligne 1 Ligne 2"


def test_deduplicate():
    talk = {
        "day": "2026-06-24",
        "room": "Amphi A",
        "start_time": datetime(2026, 6, 24, 10),
        "title": "Test",
    }

    result = deduplicate_talks([talk, talk])

    assert len(result) == 1





def test_extract_title_from_card():
    lines = [
        "Programme",
        "10h-11h",
        "Amphi A",
        "Mon super talk",
        "Speaker Test",
    ]

    assert extract_title_from_card(lines) == "Mon super talk"


def test_extract_speaker_from_card():
    lines = [
        "Mon super talk",
        "Speaker One",
        "Speaker Two",
        "Amphi A",
        "10h-11h",
    ]

    result = extract_speaker_from_card(lines, "Mon super talk")

    assert "Speaker One" in result
    assert "Speaker Two" in result


def test_parse_talk_card(monkeypatch):
    monkeypatch.setattr(
        "app.programme_scraper.get_detail_lines",
        lambda url: ["Description", "Résumé test", "Orateur·ices"]
    )

    lines = [
        "10h-11h",
        "Amphi A",
        "Talk Test",
        "Speaker Test",
    ]

    talk = parse_talk_card(
        "2026-06-24",
        "https://example.com/session/test",
        lines,
    )

    assert talk is not None
    assert talk["title"] == "Talk Test"
    assert talk["speaker"] == "Speaker Test"
    assert talk["summary"] == "Résumé test"
    assert talk["room"] == "Amphi A"


def test_parse_talk_card_without_time():
    talk = parse_talk_card(
        "2026-06-24",
        "https://example.com/session/test",
        ["Amphi A", "Talk Test"],
    )

    assert talk is None


def test_parse_talk_card_hall_ignored():
    talk = parse_talk_card(
        "2026-06-24",
        "https://example.com/session/test",
        ["10h-11h", "Hall", "Talk Test"],
    )

    assert talk is None
