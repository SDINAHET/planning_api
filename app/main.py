from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .generators import generate_ics, generate_pdf, safe_filename
from .parser import get_schedule, load_people

BASE_DIR = Path(__file__).resolve().parent.parent

GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1bwjjxQ0bUJixWRclapaiC9ge4fOah5uuS7WYIuXfqpc/"
    "export?format=xlsx"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

app = FastAPI(title="Planning bénévoles API", version="1.1.0")


def planning_source() -> str:
    return GOOGLE_SHEET_URL


def format_date_fr(date_value: str) -> str:
    try:
        return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return date_value


def add_display_dates(slots: list[dict]) -> list[dict]:
    for slot in slots:
        if slot.get("date"):
            slot["date_fr"] = format_date_fr(slot["date"])
    return slots


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    people = sorted(
        load_people(planning_source()),
        key=lambda x: x.split()[0].lower()
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "people": people,
        },
    )


@app.get("/api/people")
def people():
    people_list = sorted(
        load_people(planning_source()),
        key=lambda x: x.split()[0].lower()
    )

    return {"people": people_list}


@app.get("/api/planning/{person}")
def planning(person: str):
    slots = get_schedule(planning_source(), person)

    if not slots:
        raise HTTPException(
            status_code=404,
            detail="Personne introuvable ou aucun créneau",
        )

    return {
        "person": person,
        "total": len(slots),
        "slots": slots,
    }


@app.get("/planning/{person}", response_class=HTMLResponse)
def planning_page(request: Request, person: str):
    slots = get_schedule(planning_source(), person)

    if not slots:
        raise HTTPException(
            status_code=404,
            detail="Personne introuvable ou aucun créneau",
        )

    slots = add_display_dates(slots)

    return templates.TemplateResponse(
        "planning.html",
        {
            "request": request,
            "person": person,
            "slots": slots,
        },
    )


@app.get("/api/planning/{person}/pdf")
def pdf(person: str):
    slots = get_schedule(planning_source(), person)

    if not slots:
        raise HTTPException(status_code=404, detail="Aucun créneau")

    slots = add_display_dates(slots)
    filename = f"planning_{safe_filename(person)}.pdf"

    return Response(
        generate_pdf(person, slots),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )


@app.get("/api/planning/{person}/ics")
def ics(person: str):
    slots = get_schedule(planning_source(), person)

    if not slots:
        raise HTTPException(status_code=404, detail="Aucun créneau")

    filename = f"planning_{safe_filename(person)}.ics"

    return Response(
        generate_ics(person, slots),
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
