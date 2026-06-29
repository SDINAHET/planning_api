from app.generators import (
    safe_filename,
    schedule_text,
    parse_time_range,
    generate_ics,
    generate_pdf,
    generate_qr_png,
    generate_ics_qr_png,
)


def test_safe_filename():
    assert safe_filename("Stéphane DINAHET") == "St_phane_DINAHET"


def test_schedule_text():
    slots = [
        {
            "jour": "Mercredi",
            "horaire": "10h-12h",
            "mission": "Surveillance salle",
            "lieu": "Amphi A",
        }
    ]

    text = schedule_text("Stephane", slots)

    assert "Planning Stephane" in text
    assert "Surveillance salle" in text


def test_parse_time_range():
    start, end = parse_time_range("2026-06-24", "10h-12h")

    assert start.hour == 10
    assert end.hour == 12


def test_generate_ics():
    slots = [{
        "jour": "Mercredi",
        "date": "2026-06-24",
        "horaire": "10h-12h",
        "mission": "Surveillance",
        "lieu": "Amphi A",
    }]

    ics = generate_ics("Stephane", slots)

    assert "BEGIN:VCALENDAR" in ics
    assert "SUMMARY:Surveillance" in ics
    assert "END:VCALENDAR" in ics





def sample_slots():
    return [{
        "jour": "Mercredi",
        "date": "2026-06-24",
        "date_fr": "24/06/2026",
        "horaire": "10h-12h",
        "mission": "Accueil",
        "lieu": "Amphi A",
    }]


def test_generate_pdf():
    pdf = generate_pdf("Stephane", sample_slots())

    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF")


def test_generate_qr_png():
    qr = generate_qr_png("Stephane", sample_slots())

    assert isinstance(qr, bytes)
    assert qr[:8] == b"\x89PNG\r\n\x1a\n"


def test_generate_ics_qr_png():
    qr = generate_ics_qr_png("https://example.com/test.ics")

    assert isinstance(qr, bytes)
    assert qr[:8] == b"\x89PNG\r\n\x1a\n"


def test_generate_ics_empty():
    text = generate_ics("Stephane", [])

    assert "BEGIN:VCALENDAR" in text
    assert "END:VCALENDAR" in text
    assert "VEVENT" not in text


def test_parse_time_without_end():
    start, end = parse_time_range("2026-06-24", "10h")

    assert start == end
