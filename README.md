# MindTrends UK

**Online Search Trends for Mental Health Disorders in the UK: A Web-Based
Study Using Google Trends.**

An MSc research platform for exploring, comparing and analysing UK online
search interest for common mental health disorders (depression, anxiety,
OCD, PTSD, bipolar disorder, eating disorders) using Google Trends data —
with three user roles (Visitor, Researcher, Administrator), a full research
dashboard, and an "Aurora Research Console" dark analytics UI.

## How it works

Single Python **Flask** app (no separate frontend build step):

- **`app/`** — Flask application factory, blueprints (`main`, `auth`,
  `dashboard`, `admin`), MongoDB data-access layer (`app/models/`), and the
  data pipeline (`app/services/`).
- **MongoDB** — stores users, disorders, search queries, saved analyses,
  activity logs, editable content pages and app settings.
- **`app/services/trends_service.py`** — retrieves Google Trends data via
  [`pytrends`](https://github.com/GeneralMills/pytrends) (the unofficial
  Google Trends client — there is no official public API for this use
  case). Every response is cached in MongoDB and clearly labelled
  `live`, `cache`, or `simulated`. If live retrieval fails or is disabled,
  the service transparently falls back to a deterministic, clearly-flagged
  simulated series rather than silently failing — see the "Manage Data
  Retrieval Settings" admin page.
- **`app/services/analysis_service.py`** — turns raw series into trend
  insights (direction, % change, peaks) and disorder/region comparisons.
- **`app/services/export_service.py`** — CSV and PDF (via `reportlab`)
  export.
- Frontend: server-rendered Jinja2 templates + Bootstrap 5 (layout) +
  Chart.js (visualisation) + a hand-built dark "glassmorphic" design system
  in `app/static/css/style.css` — no JS build step required.

## Prerequisites

- [Python](https://www.python.org/downloads/) 3.10+ (works on 3.9+)
- A MongoDB connection string — local `mongod`, Docker, or
  [MongoDB Atlas](https://www.mongodb.com/atlas) free tier

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment template and fill in your Mongo URI:

```bash
cp .env.example .env
```

Key variables in `.env`:

| Variable | Purpose |
|---|---|
| `MONGO_URI` | e.g. `mongodb://localhost:27017` or an Atlas SRV string |
| `TRENDS_MODE` | `auto` (live + simulated fallback), `live`, or `simulated` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | seeded automatically on first run |

## Run

```bash
python run.py
```

Visit `http://localhost:5050`. On first run the app seeds six default
disorders and one administrator account (from `.env`) automatically — no
manual migration step needed.

## Setting up on another machine

To clone this project onto a new computer and get it running:

1. **Install prerequisites** — Python 3.9+ and Git (on macOS: `xcode-select --install`
   for command line tools, then `brew install python3` if needed).
2. **Clone the repo**
   ```bash
   git clone https://github.com/<your-username>/MindTrends_UK.git
   cd MindTrends_UK
   ```
3. **Create the virtualenv and install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Recreate `.env`** — this file is gitignored on purpose (it holds secrets), so
   it is never pushed to GitHub and must be set up separately on each machine:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in real values (see the table in [Setup](#setup)).
   Either point `MONGO_URI` at the same MongoDB Atlas cluster the other machine
   uses (share the connection string out-of-band — password manager, AirDrop,
   `scp` — never via git), or install MongoDB locally and use
   `mongodb://localhost:27017`.
5. **Run it**
   ```bash
   python run.py
   ```
   Visit `http://localhost:5050`.

## Notes for the dissertation

- Google Trends provides **relative search interest (0–100)**, not an
  absolute count of people affected — every page that surfaces trend data
  repeats this distinction, per the project brief.
- `pytrends` is unofficial and can be rate-limited; the `TRENDS_MODE`
  setting and the visible `live` / `cache` / `simulated` badges exist so the
  methodology chapter can document exactly how each figure was produced.
- The system provides informational content about each disorder — it does
  not diagnose or claim to detect individual mental health conditions.
