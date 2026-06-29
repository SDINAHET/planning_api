import os
from datetime import datetime
from zoneinfo import ZoneInfo
import unicodedata
import re
import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://planning:planning@postgres:5432/planning",
)

PARIS_TZ = ZoneInfo("Europe/Paris")

# def format_hour(dt) -> str:
#     if not dt:
#         return ""

#     return dt.astimezone(PARIS_TZ).strftime("%Hh%M")
def format_hour(dt) -> str:
    if not dt:
        return ""
    return dt.strftime("%Hh%M")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


# def normalize_room(room: str) -> str:
#     return (
#         room.replace("(principal)", "")
#         .replace("  ", " ")
#         .strip()
#     )

def normalize_room(room: str) -> str:
    if not room:
        return ""

    room = unicodedata.normalize("NFKC", room)
    room = room.replace("\xa0", " ")
    room = re.sub(r"\s+", " ", room).strip()

    lower = room.lower()

    if "principal" in lower and "(d)" in lower:
        return "Amphi D"

    if "principal" in lower:
        return "Amphi C"

    room = room.replace("(principal)", "").strip()

    return room


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS talks;")
            cur.execute(
                """
                CREATE TABLE talks (
                    id SERIAL PRIMARY KEY,
                    day DATE NOT NULL,
                    title TEXT NOT NULL,
                    speaker TEXT,
                    summary TEXT,
                    room TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    url TEXT,
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(day, room, start_time, title)
                );
                """
            )


def save_talks(talks: list[dict]) -> int:
    if not talks:
        return 0

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE talks RESTART IDENTITY;")

            for talk in talks:
                cur.execute(
                    """
                    INSERT INTO talks (
                        day, title, speaker, summary, room,
                        start_time, end_time, url, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (day, room, start_time, title)
                    DO NOTHING;
                    """,
                    (
                        talk["day"],
                        talk["title"],
                        talk.get("speaker", ""),
                        talk.get("summary", ""),
                        normalize_room(talk["room"]),
                        talk["start_time"],
                        talk["end_time"],
                        talk.get("url", ""),
                    ),
                )

    return len(talks)


def find_talks_for_slot(room: str, date: str, horaire: str) -> list[dict]:
    room = normalize_room(room)

    if not room or not date or not horaire:
        return []

    try:
        start, end = parse_slot_datetime(date, horaire)
    except Exception:
        return []

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT title, speaker, summary, room, start_time, end_time, url
                FROM talks
                WHERE room = %s
                AND day = %s
                AND start_time >= %s
                AND start_time < %s
                ORDER BY start_time;
                """,
                (room, date, start, end),
            )
            rows = cur.fetchall()

    return [
        {
            "title": r[0],
            "speaker": r[1],
            "summary": r[2],
            "room": r[3],

            # Pour API/debug
            "start_time": r[4].isoformat() if r[4] else None,
            "end_time": r[5].isoformat() if r[5] else None,

            # Pour affichage UX
            "start_fr": format_hour(r[4]),
            "end_fr": format_hour(r[5]),

            "url": r[6],
        }
        for r in rows
    ]


def parse_slot_datetime(date: str, horaire: str):
    clean = (
        horaire.replace(" ", "")
        .replace("–", "-")
        .replace("—", "-")
    )

    if "-" not in clean:
        raise ValueError(f"Horaire invalide : {horaire}")

    start_txt, end_txt = clean.split("-", 1)

    return parse_one(date, start_txt), parse_one(date, end_txt)


def parse_one(date: str, value: str):
    value = value.lower().replace("h", ":")
    if value.endswith(":"):
        value += "00"
    if ":" not in value:
        value += ":00"

    hour, minute = value.split(":", 1)

    # return datetime(
    #     int(date[:4]),
    #     int(date[5:7]),
    #     int(date[8:10]),
    #     int(hour),
    #     int(minute),
    #     tzinfo=PARIS_TZ,
    # )
    return datetime(
        int(date[:4]),
        int(date[5:7]),
        int(date[8:10]),
        int(hour),
        int(minute),
    )


def list_talks() -> list[dict]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT day, title, speaker, summary, room, start_time, end_time, url, updated_at
                FROM talks
                ORDER BY day, start_time, room;
                """
            )
            rows = cur.fetchall()

    return [
        {
            "day": str(r[0]),
            "title": r[1],
            "speaker": r[2],
            "summary": r[3],
            "room": r[4],
            "start_time": r[5].isoformat() if r[5] else None,
            "end_time": r[6].isoformat() if r[6] else None,
            "url": r[7],
            "updated_at": r[8].isoformat() if r[8] else None,
        }
        for r in rows
    ]
