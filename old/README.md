# 📅 Planning Bénévoles API

API développée avec **FastAPI** permettant d'exploiter automatiquement le planning des bénévoles à partir d'un document Google Sheets.

L'application génère pour chaque bénévole :

* 🌐 Une page web individuelle ;
* 📄 Un planning PDF imprimable ;
* 📆 Un agenda `.ics` compatible iPhone, Apple Calendar, Google Calendar et Outlook ;
* 🔗 Une API JSON ;
* 🔍 Une recherche dynamique des bénévoles ;
* 📱 Une interface responsive mobile.

---

# Fonctionnalités

## Interface Web

* Recherche instantanée des bénévoles ;
* Tri alphabétique par prénom ;
* Interface responsive ;
* Export PDF ;
* Export Agenda `.ics` ;
* Consultation JSON.

## API

| Endpoint                     | Description         |
| ---------------------------- | ------------------- |
| `/`                          | Liste des bénévoles |
| `/planning/{person}`         | Planning HTML       |
| `/api/people`                | Liste JSON          |
| `/api/planning/{person}`     | Planning JSON       |
| `/api/planning/{person}/pdf` | PDF                 |
| `/api/planning/{person}/ics` | Agenda iCalendar    |

---

# Environnement Python

## Création du venv

```bash
python3 -m venv venv
```

Activation :

Linux

```bash
source venv/bin/activate
```

Installation :

```bash
pip install -r requirements.txt
```

Lancement :

```bash
uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000
```

---

# Docker

Construction :

```bash
docker build -t planning-api .
```

Exécution :

```bash
docker run -d \
-p 8000:8000 \
--name planning-api \
planning-api
```

---

## Docker Compose

```bash
docker compose up --build -d
```
 Front Api disponible: [http//:localhost:8000](http://localhost:8000/)


Arrêt :

```bash
docker compose down
```

Logs :

```bash
docker logs -f planning-api
```

---

# Déploiement

DNS :

```text
planning.xxxxxxxxxxx.fr
```

Apache :

```apache
ProxyPass / http://127.0.0.1:8000/
ProxyPassReverse / http://127.0.0.1:8000/
```

HTTPS :

```bash
sudo certbot --apache \
-d planning.xxxxxxxxxxxx.fr
```

---

# Architecture

```text
Google Sheets
       │
       ▼
FastAPI
       │
       ├── HTML
       ├── JSON
       ├── PDF
       └── ICS
```

---

# Technologies

* FastAPI
* Uvicorn
* Jinja2
* ReportLab
* OpenPyXL
* Docker
* Apache
* Let's Encrypt
* Google Sheets
* iCalendar (.ics)


