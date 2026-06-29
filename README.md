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


table create:
```sql
CREATE TABLE IF NOT EXISTS talks (
    id SERIAL PRIMARY KEY,
    day DATE NOT NULL,
    title TEXT NOT NULL,
    speaker TEXT,
    room TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    url TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(day, room, start_time, title)
);
```


docker compose down -v
docker compose up -d --build

Ou sans supprimer la base :
0docker exec -i planning_postgres psql -U planning -d planning < init.sql


documentation API: http://localhost:8009/docs



-on ajoute programme_scraper.py pour remplir la table depuis https://www.breizhcamp.org/programme.


docker compose down
docker compose up -d --build
docker compose logs -f planning-api


swagger
http://localhost:8009/docs



Dans PowerShell Admin, lance ça :

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8009 connectaddress=172.18.71.179 connectport=8009

netsh advfirewall firewall add rule name="Planning API 8009" dir=in action=allow protocol=TCP localport=8009

Pour PostgreSQL aussi, si tu veux l’accès réseau :

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=5442 connectaddress=172.18.71.179 connectport=5442

netsh advfirewall firewall add rule name="Planning Postgres 5442" dir=in action=allow protocol=TCP localport=5442

Vérifie :

netsh interface portproxy show all

Tu dois voir :

0.0.0.0    8009    172.18.71.179    8009
0.0.0.0    5442    172.18.71.179    5442

Puis mobile :

http://192.168.1.251:8009



