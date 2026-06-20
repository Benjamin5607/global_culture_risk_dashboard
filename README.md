# Global Culture Risk Dashboard

Unified platform consolidating four repositories into a single dashboard:

| Former Repository | Module |
|---|---|
| `global_culture_risk_dashboard` | Culture Risk Monitor |
| `global_slang_dictionary` | Multilingual Slang Dictionary (crawlers + pipeline) |
| `slang_dictionary` | Slang AI Curator |
| `global-risk-war-room` | Risk War Room |

## Modules

### 1. Culture Risk Monitor
Browse AI-curated risk data for public figures, dangerous groups, and platform trends. Data is auto-updated every 4 hours via GitHub Actions.

### 2. Slang Dictionary
Search 4,800+ slang terms crawled daily from Urban Dictionary, Wiktionary, Reddit, and GitHub lists across 14 languages.

### 3. Slang AI Curator
Country-aware slang analysis powered by Groq AI with multilingual UI (EN, KR, JP, ES).

### 4. Risk War Room
Real-time strategic risk intelligence: Top 3 urgent signals, forensic incident analysis (STAR framework), and country dashboards.

## Quick Start

### Static Dashboard (GitHub Pages)
The dashboard is deployed automatically to GitHub Pages. Modules 1 and 2 work without a backend.

### Full Platform (with AI features)
```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
python app.py
```
Open http://localhost:8080 for all four modules including AI features.

### Deploy Backend (Render / Railway)
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```
Set `GROQ_API_KEY` as an environment variable.

## Data Pipelines

| Script | Purpose | Schedule |
|---|---|---|
| `brain.py` | Daily risk data update | Every 4 hours |
| `seed.py` | Bulk risk data generation | Manual |
| `crawlers/*.py` | Slang term crawling | Daily at 02:00 UTC |
| `pipeline/deduplicate.py` | Merge and deduplicate slang data | After crawl |

## Project Structure

```
├── index.html              # Unified dashboard UI
├── app.py                  # Flask API server (AI features)
├── brain.py                # Daily risk updater
├── seed.py                 # Bulk risk generator
├── data.json               # Risk database
├── crawlers/               # Slang crawlers (4 sources)
├── pipeline/               # Data deduplication
├── config/                 # Language/source config
├── output/                 # Crawled slang CSV
├── modules/
│   ├── slang_curator.py    # Slang AI logic
│   └── risk_war_room.py    # Risk War Room logic
└── .github/workflows/
    ├── update.yml          # Risk data + Pages deploy
    ├── seed.yml            # Bulk generator
    ├── daily_crawl.yml     # Slang crawl
    └── wake_up.yml         # Backend keep-alive
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes (AI features) | Groq API key for AI modules |
| `GH_PAT` | Optional | GitHub token for CSV sync |
| `BACKEND_URL` | Optional | Backend URL for wake-up workflow |

## Languages Supported (Slang Dictionary)

EN, KO, JA, TH, VI, ID, MS, ES, PT, TL, DE, FR, RU, IT
