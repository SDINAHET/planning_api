from __future__ import annotations
from datetime import datetime
from io import BytesIO
from typing import List
import re
import qrcode
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def safe_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", name).strip("_")


def schedule_text(person: str, slots: List[dict]) -> str:
    lines = [f"Planning {person}", ""]
    for s in slots:
        lines.append(f"{s['jour']} {s['horaire']} | {s['mission']} | {s.get('lieu','')}")
    return "\n".join(lines)


def generate_qr_png(person: str, slots: List[dict]) -> bytes:
    img = qrcode.make(schedule_text(person, slots))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_pdf(person: str, slots: List[dict]) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf)
    styles = getSampleStyleSheet()

    story = [
        Paragraph(f"Planning bénévole - {person}", styles["Title"]),
        Spacer(1, 12)
    ]

    data = [["Jour", "Date", "Horaire", "Mission", "Lieu"]]

    data += [
        [
            s.get("jour", ""),
            s.get("date_fr", s.get("date", "")),
            s.get("horaire", ""),
            s.get("mission", ""),
            s.get("lieu", ""),
        ]
        for s in slots
    ]

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#EEF2FF")
        ]),
    ]))

    story.append(table)
    doc.build(story)

    return buf.getvalue()


def parse_time_range(date_str: str, horaire: str):
    h = (
        horaire
        .replace(" ", "")
        .replace("–", "-")
        .replace("—", "-")
    )

    if "-" in h:
        start, end = h.split("-", 1)
    else:
        start, end = h, h

    def conv(t):
        t = t.strip().replace("H", "h").replace("h", ":")
        if t.endswith(":"):
            t += "00"
        if ":" not in t:
            t += ":00"
        hour, minute = t.split(":", 1)
        # important : 8:30 devient 08:30
        t = f"{int(hour):02d}:{int(minute):02d}"
        return datetime.fromisoformat(f"{date_str}T{t}")
    return conv(start), conv(end)


def generate_ics(person: str, slots: List[dict]) -> str:
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Planning API//FR"]
    for s in slots:
        if not s.get("date"):
            continue
        start, end = parse_time_range(s["date"], s["horaire"])
        out += [
            "BEGIN:VEVENT",
            f"SUMMARY:{s['mission']}",
            f"LOCATION:{s.get('lieu','')}",
            f"DESCRIPTION:Planning bénévole - {person}",
            f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
            "END:VEVENT",
        ]
    out.append("END:VCALENDAR")
    return "\n".join(out)

def generate_ics_qr_png(ics_url: str) -> bytes:
    img = qrcode.make(ics_url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
