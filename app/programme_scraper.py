from __future__ import annotations

# from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta

DAY_PAGES = [
    ("2026-06-24", "https://www.breizhcamp.org/programme/mercredi"),
    ("2026-06-25", "https://www.breizhcamp.org/programme/jeudi"),
    ("2026-06-26", "https://www.breizhcamp.org/programme/vendredi"),
]

LEVELS = {"Introduction", "Standard", "Avancé"}
THEMES = {
    "Architecture", "Data", "Développement", "DevOps", "Écoconception",
    "IA", "IoT Embarqué", "Méthodologie", "Mobile", "Sécurité", "Web"
}
IGNORE = {
    "Accueil", "Accueil / Café", "Universités & conférences",
    "Déjeuner", "Eat", "Pause café", "Pause déjeuner",
    "Programme", "Sponsors", "Infos pratiques", "Équipe", "Billets"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def get_lines(node) -> list[str]:
    return [
        clean_line(line)
        for line in node.get_text("\n", strip=True).splitlines()
        if clean_line(line)
    ]


def is_time_line(value: str) -> bool:
    return bool(re.match(
        r"^\d{1,2}h(?:\d{2})?\s*[—–-]\s*\d{1,2}h(?:\d{2})?$",
        clean_line(value),
    ))


def is_room_text(value: str) -> bool:
    value = clean_line(value).replace("·", "").strip()
    return bool(re.match(
        r"^(Amphi\s+[A-E]|Amphi\s+principal|Hall)$",
        value,
        re.IGNORECASE,
    ))


# def parse_time(date: str, value: str) -> datetime:
#     value = clean_line(value).lower().replace("h", ":")
#     if value.endswith(":"):
#         value += "00"
#     if ":" not in value:
#         value += ":00"

#     hour, minute = value.split(":", 1)

#     return datetime(
#         int(date[:4]),
#         int(date[5:7]),
#         int(date[8:10]),
#         int(hour),
#         int(minute),
#     )

def parse_time(date: str, value: str) -> datetime:
    value = clean_line(value).lower().replace("h", ":")
    if value.endswith(":"):
        value += "00"
    if ":" not in value:
        value += ":00"

    hour, minute = value.split(":", 1)

    return datetime(
        int(date[:4]),
        int(date[5:7]),
        int(date[8:10]),
        int(hour),
        int(minute),
    ) + timedelta(hours=2)


def scrape_breizhcamp_programme() -> list[dict]:
    talks = []

    for date, url in DAY_PAGES:
        talks.extend(scrape_day(date, url))

    return deduplicate_talks(talks)


def scrape_day(date: str, url: str) -> list[dict]:
    response = requests.get(url, timeout=20, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    talks = []

    # for mobile in soup.select(".mobile-only"):
    #     mobile.decompose()

    for article in soup.find_all("article"):
        a = article.find("a", href=True)
        h2 = article.find("h2")
        schedule = article.find("p", class_=lambda c: c and "schedule" in c)

        if not a or not h2 or not schedule:
            continue

        href = a["href"]
        if "/programme/session/" not in href:
            continue

        title = clean_line(h2.get_text(" ", strip=True))
        if not title or "ANNULÉ" in title.upper():
            continue

        schedule_text = clean_line(schedule.get_text(" ", strip=True))
        # exemple : "11h30 — 12h25 · Amphi E"
        match = re.match(
            r"^(\d{1,2}h(?:\d{2})?)\s*[—–-]\s*(\d{1,2}h(?:\d{2})?)\s*·\s*(.+)$",
            schedule_text,
        )

        if not match:
            continue

        start_txt, end_txt, room = match.groups()
        room = clean_line(room)

        if room.lower() == "hall":
            continue

        speakers = [
            clean_line(p.get_text(" ", strip=True))
            for p in article.select(".speaker p")
            if clean_line(p.get_text(" ", strip=True))
        ]

        detail_url = urljoin(url, href)

        talks.append({
            "day": date,
            "title": title,
            "speaker": ", ".join(dict.fromkeys(speakers)),
            "summary": extract_summary_from_lines(get_detail_lines(detail_url)),
            "room": room,
            "start_time": parse_time(date, start_txt),
            "end_time": parse_time(date, end_txt),
            "url": detail_url,
        })

    print(f"[BreizhCamp] {date} : {len(talks)} talks trouvés")
    return talks


def parse_talk_card(date: str, detail_url: str, lines: list[str]) -> dict | None:
    time_line = next((line for line in lines if is_time_line(line)), "")
    room_line = next((line for line in lines if is_room_text(line)), "")

    if not time_line or not room_line:
        return None

    room = room_line.replace("·", "").strip()

    if room.lower() == "hall":
        return None

    match = re.match(
        r"^(\d{1,2}h(?:\d{2})?)\s*[—–-]\s*(\d{1,2}h(?:\d{2})?)$",
        time_line,
    )

    if not match:
        return None

    start_txt, end_txt = match.groups()

    title = extract_title_from_card(lines)

    if not title or "ANNULÉ" in title.upper():
        return None

    detail_lines = get_detail_lines(detail_url)

    return {
        "day": date,
        "title": title,
        "speaker": extract_speaker_from_card(lines, title),
        "summary": extract_summary_from_lines(detail_lines),
        "room": room,
        "start_time": parse_time(date, start_txt),
        "end_time": parse_time(date, end_txt),
        "url": detail_url,
    }


def extract_title_from_card(lines: list[str]) -> str:
    for line in lines:
        if (
            line
            and line not in IGNORE
            and line not in LEVELS
            and line not in THEMES
            and not is_time_line(line)
            and not is_room_text(line)
            and not line.startswith("Jour ")
        ):
            return line

    return ""


def extract_speaker_from_card(lines: list[str], title: str) -> str:
    speakers = []

    for line in lines:
        if (
            line
            and line != title
            and line not in IGNORE
            and line not in LEVELS
            and line not in THEMES
            and not is_time_line(line)
            and not is_room_text(line)
            and not line.startswith("Jour ")
        ):
            speakers.append(line)

    return ", ".join(dict.fromkeys(speakers))


def get_detail_lines(detail_url: str) -> list[str]:
    try:
        response = requests.get(detail_url, timeout=20, headers=HEADERS)
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    return get_lines(soup)


def extract_summary_from_lines(lines: list[str]) -> str:
    if "Description" not in lines:
        return ""

    start = lines.index("Description") + 1
    end = len(lines)

    for marker in ["Orateur·ices", "Actions rapides", "Les sessions futures"]:
        if marker in lines[start:]:
            end = min(end, start + lines[start:].index(marker))

    return " ".join(lines[start:end]).strip()


def deduplicate_talks(talks: list[dict]) -> list[dict]:
    seen = set()
    unique = []

    for talk in talks:
        key = (
            talk["day"],
            talk["room"],
            talk["start_time"],
            talk["title"],
        )

        if key not in seen:
            seen.add(key)
            unique.append(talk)

    return unique
