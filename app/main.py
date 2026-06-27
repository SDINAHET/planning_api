# from __future__ import annotations

# from datetime import datetime
# from pathlib import Path

# from fastapi import FastAPI, HTTPException, Request, Response
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates

# from .generators import generate_ics, generate_pdf, safe_filename
# from .parser import get_schedule, load_people
# from fastapi.staticfiles import StaticFiles
# from .parser import extract_general
# from .programme_repository import find_talks_for_slot

# BASE_DIR = Path(__file__).resolve().parent.parent

# GOOGLE_SHEET_URL = (
#     "https://docs.google.com/spreadsheets/d/"
#     "1bwjjxQ0bUJixWRclapaiC9ge4fOah5uuS7WYIuXfqpc/"
#     "export?format=xlsx"
# )

# templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# # app = FastAPI(title="Planning bénévoles API", version="1.1.0")
# app = FastAPI(
#     title="Planning bénévoles API - BreizhCamp 2026",
#     version="1.2.0",
#     description="""
# API FastAPI permettant de consulter le planning des bénévoles BreizhCamp 2026.

# Fonctionnalités :
# - liste des bénévoles ;
# - planning individuel ;
# - planning général ;
# - export PDF ;
# - export agenda ICS ;
# - enrichissement des créneaux avec les conférences du programme BreizhCamp.
# """,
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json",
# )

# app.mount(
#     "/static",
#     StaticFiles(directory=BASE_DIR / "app" / "static"),
#     name="static"
# )

# def planning_source() -> str:
#     return GOOGLE_SHEET_URL


# def format_date_fr(date_value: str) -> str:
#     try:
#         return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d/%m/%Y")
#     except ValueError:
#         return date_value


# def add_display_dates(slots: list[dict]) -> list[dict]:
#     for slot in slots:
#         if slot.get("date"):
#             slot["date_fr"] = format_date_fr(slot["date"])
#     return slots


# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     people = sorted(
#         load_people(planning_source()),
#         key=lambda x: x.split()[0].lower()
#     )

#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "people": people,
#         },
#     )


# @app.get("/api/people")
# def people():
#     people_list = sorted(
#         load_people(planning_source()),
#         key=lambda x: x.split()[0].lower()
#     )

#     return {"people": people_list}


# @app.get("/api/planning/{person}")
# def planning(person: str):
#     slots = get_schedule(planning_source(), person)

#     if not slots:
#         raise HTTPException(
#             status_code=404,
#             detail="Personne introuvable ou aucun créneau",
#         )

#     return {
#         "person": person,
#         "total": len(slots),
#         "slots": slots,
#     }

# @app.get("/planning/{person}", response_class=HTMLResponse)
# def planning_page(request: Request, person: str, jour: str | None = None):
#     slots = get_schedule(planning_source(), person)
#     slots = add_display_dates(slots)
#     slots = add_talks_to_slots(slots)

#     if jour:
#         slots = [
#             s for s in slots
#             if s.get("jour", "").lower() == jour.lower()
#         ]

#     return templates.TemplateResponse(
#         "planning.html",
#         {
#             "request": request,
#             "person": person,
#             "slots": slots,
#             "selected_jour": jour or "",
#             "is_general": False,
#             "active_person": person,
#             "query": "",
#         },
#     )


# # @app.get("/planning/{person}", response_class=HTMLResponse)
# # def planning_page(request: Request, person: str, jour: str | None = None):
# #     slots = get_schedule(planning_source(), person)

# #     slots = add_display_dates(slots)

# #     if jour:
# #         slots = [
# #             s for s in slots
# #             if s.get("jour", "").lower() == jour.lower()
# #         ]

# #     return templates.TemplateResponse(
# #         "planning.html",
# #         {
# #             "request": request,
# #             "person": person,
# #             "slots": slots,
# #             "selected_jour": jour or "",
# #             "is_general": False,
# #             "active_person": person,
# #             "query": "",
# #         },
# #     )


# @app.get("/general", response_class=HTMLResponse)
# def general_page(
#     request: Request,
#     jour: str | None = None,
#     q: str | None = None,
#     person: str | None = None,
# ):
#     slots = add_display_dates(extract_general(planning_source()))

#     if jour:
#         slots = [
#             s for s in slots
#             if s.get("jour", "").lower() == jour.lower()
#         ]

#     if q:
#         query = q.lower()
#         slots = [
#             s for s in slots
#             if query in (
#                 f"{s.get('horaire','')} "
#                 f"{s.get('mission','')} "
#                 f"{s.get('lieu','')} "
#                 f"{' '.join(s.get('benevoles', []))}"
#             ).lower()
#         ]

#     return templates.TemplateResponse(
#         "planning.html",
#         {
#             "request": request,
#             "person": "Planning général",
#             "slots": slots,
#             "selected_jour": jour or "",
#             "query": q or "",
#             "is_general": True,
#             "active_person": person or "",
#         },
#     )

# @app.get("/api/planning/{person}/pdf")
# def pdf(person: str):
#     slots = get_schedule(planning_source(), person)

#     if not slots:
#         raise HTTPException(status_code=404, detail="Aucun créneau")

#     slots = add_display_dates(slots)
#     filename = f"planning_{safe_filename(person)}.pdf"

#     return Response(
#         generate_pdf(person, slots),
#         media_type="application/pdf",
#         headers={
#             "Content-Disposition": f'inline; filename="{filename}"',
#         },
#     )


# @app.get("/api/planning/{person}/ics")
# def ics(person: str):
#     slots = get_schedule(planning_source(), person)

#     if not slots:
#         raise HTTPException(status_code=404, detail="Aucun créneau")

#     filename = f"planning_{safe_filename(person)}.ics"

#     return Response(
#         generate_ics(person, slots),
#         media_type="text/calendar; charset=utf-8",
#         headers={
#             "Content-Disposition": f'attachment; filename="{filename}"',
#         },
#     )


# @app.get("/agenda", response_class=HTMLResponse)
# def agenda_general(request: Request):
#     slots = add_display_dates(extract_general(planning_source()))

#     return templates.TemplateResponse(
#         "agenda.html",
#         {
#             "request": request,
#             "slots": slots,
#             "person": "Agenda général",
#             "is_general": True,
#         },
#     )

# def add_talks_to_slots(slots):
#     for slot in slots:
#         if not slot.get("lieu", "").startswith("Amphi"):
#             slot["talks"] = []
#             continue

#         slot["talks"] = find_talks_for_slot(
#             room=slot["lieu"],
#             date=slot["date"],
#             horaire=slot["horaire"],
#         )

#     return slots

# # slots = add_display_dates(get_schedule(planning_source(), person))
# # slots = add_talks_to_slots(slots)



import os
import secrets

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .generators import generate_ics, generate_pdf, safe_filename
from .parser import extract_general, get_schedule, load_people
from .programme_repository import find_talks_for_slot
from apscheduler.schedulers.background import BackgroundScheduler
from .programme_scraper import scrape_breizhcamp_programme
from .programme_repository import init_db, save_talks

BASE_DIR = Path(__file__).resolve().parent.parent

GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1bwjjxQ0bUJixWRclapaiC9ge4fOah5uuS7WYIuXfqpc/"
    "export?format=xlsx"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

app = FastAPI(
    title="Planning bénévoles API - BreizhCamp 2026",
    version="1.2.0",
    description="""
API FastAPI permettant de consulter le planning des bénévoles BreizhCamp 2026.

Fonctionnalités :
- liste des bénévoles ;
- planning individuel ;
- planning général ;
- export PDF ;
- export agenda ICS ;
- enrichissement des créneaux avec les conférences du programme BreizhCamp.
""",
    # docs_url="/docs",
    # redoc_url="/redoc",
    # openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.1.251:8009",
        "http://localhost:8009",
        "http://127.0.0.1:8009",
    ],
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "app" / "static"),
    name="static"
)

app.mount(
    "/templates/assets",
    StaticFiles(directory=BASE_DIR / "app" / "templates" / "assets"),
    name="template_assets"
)

scheduler = BackgroundScheduler(timezone="Europe/Paris")

security = HTTPBasic()

SWAGGER_USER = os.getenv("SWAGGER_USER", "admin")
SWAGGER_PASSWORD = os.getenv("SWAGGER_PASSWORD", "motdepassefort")


def check_docs(credentials: HTTPBasicCredentials = Depends(security)):

    valid_user = secrets.compare_digest(
        credentials.username,
        SWAGGER_USER
    )

    valid_password = secrets.compare_digest(
        credentials.password,
        SWAGGER_PASSWORD
    )

    if not (valid_user and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True

def refresh_programme():
    talks = scrape_breizhcamp_programme()
    count = save_talks(talks)
    print(f"[BreizhCamp] {count} talks mis à jour")


@app.on_event("startup")
def startup_event():
    init_db()
    refresh_programme()
    scheduler.add_job(refresh_programme, "interval", minutes=30)
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

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


def add_talks_to_slots(slots: list[dict]) -> list[dict]:
    for slot in slots:
        lieu = slot.get("lieu", "")

        if not lieu.startswith("Amphi"):
            slot["talks"] = []
            continue

        slot["talks"] = find_talks_for_slot(
            room=lieu,
            date=slot.get("date", ""),
            horaire=slot.get("horaire", ""),
        )

    return slots


@app.get("/", response_class=HTMLResponse, tags=["Pages"])
def home(request: Request):
    people = sorted(
        load_people(planning_source()),
        key=lambda x: x.split()[0].lower(),
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "people": people,
        },
    )


@app.get("/api/people", tags=["API"], summary="Liste des bénévoles")
def people():
    people_list = sorted(
        load_people(planning_source()),
        key=lambda x: x.split()[0].lower(),
    )

    return {"people": people_list}


@app.get("/api/planning/{person}", tags=["API"], summary="Planning individuel JSON")
def planning(person: str):
    slots = get_schedule(planning_source(), person)

    if not slots:
        raise HTTPException(
            status_code=404,
            detail="Personne introuvable ou aucun créneau",
        )

    slots = add_display_dates(slots)
    slots = add_talks_to_slots(slots)

    return {
        "person": person,
        "total": len(slots),
        "slots": slots,
    }


@app.get("/planning/{person}", response_class=HTMLResponse, tags=["Pages"])
def planning_page(request: Request, person: str, jour: str | None = None):
    slots = get_schedule(planning_source(), person)
    slots = add_display_dates(slots)
    slots = add_talks_to_slots(slots)

    if jour:
        slots = [
            s for s in slots
            if s.get("jour", "").lower() == jour.lower()
        ]

    return templates.TemplateResponse(
        "planning.html",
        {
            "request": request,
            "person": person,
            "slots": slots,
            "selected_jour": jour or "",
            "is_general": False,
            "active_person": person,
            "query": "",
        },
    )


@app.get("/general", response_class=HTMLResponse, tags=["Pages"])
def general_page(
    request: Request,
    jour: str | None = None,
    q: str | None = None,
    person: str | None = None,
):
    slots = add_display_dates(extract_general(planning_source()))
    slots = add_talks_to_slots(slots)

    if jour:
        slots = [
            s for s in slots
            if s.get("jour", "").lower() == jour.lower()
        ]

    if q:
        query = q.lower()
        slots = [
            s for s in slots
            if query in (
                f"{s.get('horaire','')} "
                f"{s.get('mission','')} "
                f"{s.get('lieu','')} "
                f"{' '.join(s.get('benevoles', []))} "
                f"{' '.join(t.get('title', '') for t in s.get('talks', []))} "
                f"{' '.join(t.get('speaker', '') for t in s.get('talks', []))}"
            ).lower()
        ]

    return templates.TemplateResponse(
        "planning.html",
        {
            "request": request,
            "person": "Planning général",
            "slots": slots,
            "selected_jour": jour or "",
            "query": q or "",
            "is_general": True,
            "active_person": person or "",
        },
    )


@app.get("/api/planning/{person}/pdf", tags=["Exports"], summary="Export PDF")
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


@app.get("/api/planning/{person}/ics", tags=["Exports"], summary="Export agenda ICS")
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


@app.get("/agenda", response_class=HTMLResponse, tags=["Pages"])
def agenda_general(request: Request):
    slots = add_display_dates(extract_general(planning_source()))
    slots = add_talks_to_slots(slots)

    return templates.TemplateResponse(
        "agenda.html",
        {
            "request": request,
            "slots": slots,
            "person": "Agenda général",
            "is_general": True,
        },
    )


@app.post("/api/programme/refresh", tags=["Programme"], summary="Lancer le scraping du programme")
def refresh_programme_api():
    talks = scrape_breizhcamp_programme()
    count = save_talks(talks)
    return {"message": "Programme mis à jour", "talks": count}


@app.get("/api/programme/talks", tags=["Programme"], summary="Lister les conférences stockées")
def list_programme_talks():
    from .programme_repository import list_talks
    return {"talks": list_talks()}

@app.get("/api/programme/debug", tags=["Programme"])
def debug_programme():
    import requests
    from bs4 import BeautifulSoup

    html = requests.get(
        "https://www.breizhcamp.org/programme",
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    ).text

    soup = BeautifulSoup(html, "lxml")
    lines = [
        line.strip()
        for line in soup.get_text("\n", strip=True).splitlines()
        if line.strip()
    ]

    return {
        "html_size": len(html),
        "lines_count": len(lines),
        "sample": lines[:80],
    }

@app.get("/api/programme/debug-links", tags=["Programme"])
def debug_programme_links():
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    url = "https://www.breizhcamp.org/programme/mercredi"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20).text
    soup = BeautifulSoup(html, "lxml")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/programme/session/" in href:
            links.append({
                "text": a.get_text(" ", strip=True)[:120],
                "href": urljoin(url, href),
            })

    return {
        "count": len(links),
        "sample": links[:20],
    }

@app.get("/docs", include_in_schema=False)
def swagger(_: bool = Depends(check_docs)):

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Swagger"
    )


@app.get("/openapi.json", include_in_schema=False)
def openapi(_: bool = Depends(check_docs)):

    return JSONResponse(app.openapi())
