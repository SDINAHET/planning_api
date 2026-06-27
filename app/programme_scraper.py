from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

PARIS_TZ = ZoneInfo("Europe/Paris")

DAY_PAGES = [
    ("2026-06-24", "https://www.breizhcamp.org/programme/mercredi"),
    ("2026-06-25", "https://www.breizhcamp.org/programme/jeudi"),
    ("2026-06-26", "https://www.breizhcamp.org/programme/vendredi"),
]

LEVELS = {"Introduction", "Standard", "Avancé"}
THEMES = {"Architecture", "Data", "Développement", "DevOps", "Écoconception", "IA", "IoT Embarqué", "Méthodologie", "Mobile", "Sécurité", "Web"}
IGNORE = {"Accueil", "Accueil / Café", "Universités & conférences", "Déjeuner", "Eat"}


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def is_time_line(value: str) -> bool:
    return bool(re.match(r"^\d{1,2}h(?:\d{2})?\s*[—–-]\s*\d{1,2}h(?:\d{2})?$", value))


# def is_room_line(value: str) -> bool:
#     return bool(re.match(r"^·\s*(Amphi\s+[A-E]|Hall)$", value))

def is_room_line(value: str) -> bool:
    return bool(re.match(
        r"^·\s*(Amphi\s+[A-E]|Amphi\s+principal|Hall)$",
        value,
        re.IGNORECASE,
    ))


def parse_time(date: str, value: str) -> datetime:
    value = value.strip().lower().replace("h", ":")
    if value.endswith(":"):
        value += "00"
    if ":" not in value:
        value += ":00"

    hour, minute = value.split(":", 1)
    return datetime(int(date[:4]), int(date[5:7]), int(date[8:10]), int(hour), int(minute), tzinfo=PARIS_TZ)


def scrape_breizhcamp_programme() -> list[dict]:
    talks = []
    for date, url in DAY_PAGES:
        talks.extend(scrape_day(date, url))
    return deduplicate_talks(talks)


def scrape_day(date: str, url: str) -> list[dict]:
    response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    session_links = [
        urljoin(url, a["href"])
        for a in soup.find_all("a", href=True)
        if "/programme/session/" in a["href"]
    ]

    lines = [
        clean_line(line)
        for line in soup.get_text("\n", strip=True).splitlines()
        if clean_line(line)
    ]

    talks = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if not is_time_line(line):
            i += 1
            continue

        if i + 1 >= len(lines) or not is_room_line(lines[i + 1]):
            i += 1
            continue

        room = lines[i + 1].replace("·", "").strip()
        if room == "Hall":
            i += 2
            continue

        time_match = re.match(r"^(\d{1,2}h(?:\d{2})?)\s*[—–-]\s*(\d{1,2}h(?:\d{2})?)$", line)
        if not time_match:
            i += 2
            continue

        block = []
        j = i - 1

        while j >= 0:
            previous = lines[j]
            if is_time_line(previous) or is_room_line(previous):
                break

            if previous not in LEVELS and previous not in THEMES and previous not in IGNORE and not previous.startswith("Jour "):
                block.append(previous)

            j -= 1

        block.reverse()

        if not block:
            i += 2
            continue

        title = block[0]
        if "ANNULÉ" in title.upper():
            i += 2
            continue

        detail_url = session_links[len(talks)] if len(talks) < len(session_links) else url
        summary = scrape_summary(detail_url)

        start_txt, end_txt = time_match.groups()

        talks.append({
            "day": date,
            "title": title,
            "speaker": ", ".join(block[1:]),
            "summary": summary,
            "room": room,
            "start_time": parse_time(date, start_txt),
            "end_time": parse_time(date, end_txt),
            "url": detail_url,
        })

        i += 2

    return talks


def scrape_summary(detail_url: str) -> str:
    if not detail_url or "/programme/session/" not in detail_url:
        return ""

    response = requests.get(detail_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    lines = [
        clean_line(line)
        for line in soup.get_text("\n", strip=True).splitlines()
        if clean_line(line)
    ]

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
        key = (talk["day"], talk["room"], talk["start_time"], talk["title"])
        if key not in seen:
            seen.add(key)
            unique.append(talk)

    return unique
