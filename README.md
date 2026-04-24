# Redishort 🤖 - Full-Stack YouTube Shorts Creator

![Logo](redishort.png)

> **Project Status: Active Development / Evolution**  
> This project originally started as an autonomous Python script scraping Reddit. It has now evolved into a **multi-tenant full-stack application** featuring a React frontend, a FastAPI backend, JWT authentication, AWS S3 storage, and RSS/URL-based content ingestion.

---

## 📊 Real-World Results (V1 Autonomous Script)

The original version of this bot worked in production:

| Metric               | Value                                      |
| -------------------- | ------------------------------------------ |
| **Total Views**      | 200,000 - 300,000+                         |
| **Timeframe**        | 2 months                                   |
| **Platforms**        | YouTube, TikTok, Facebook, Instagram       |
| **Infrastructure**   | Self-hosted Docker on personal laptop      |
| **Automation Level** | 100% autonomous (content hunting → upload) |

**YouTube Channel**: [@reditoktv](https://www.youtube.com/@reditoktv)

All videos on this channel were generated and uploaded **completely autonomously** by V1 of this bot.

---

## 💼 Technical Highlights

| Category             | Technologies & Skills                                                          |
| -------------------- | ------------------------------------------------------------------------------ |
| **Backend API**      | FastAPI, SQLAlchemy, Pydantic, Alembic Migrations, Threading                   |
| **Frontend UI**      | React, Vite, Tailwind CSS, React Router, Lucide Icons                          |
| **Security/Auth**    | JWT (JSON Web Tokens), `python-jose`, `passlib[bcrypt]`, Multi-tenancy         |
| **Cloud/Infra**      | AWS S3 (`boto3`), Docker, Docker Compose                                       |
| **AI/ML**            | LLM Integration (Gemini), Speech-to-Text (Whisper), Text-to-Speech (Coqui TTS) |
| **Content Scraping** | RSS Feeds (`feedparser`), Web Scraping (`BeautifulSoup4`), Reddit (legacy)     |
| **Video Processing** | MoviePy, FFmpeg, Dynamic Subtitles, Progress Bar Animation                     |

---

## 🎯 What It Does

**Redishort** is an automation system that transforms text-based stories (from URLs or RSS feeds) into engaging YouTube Shorts videos. It manages the entire production pipeline via a structured workflow state machine:

```mermaid
graph TD
    A[🔍 Ingest Content (RSS/URL)] --> B[✍️ Generate Draft Script with AI]
    B --> C[🕵️ User Approval (Frontend)]
    C --> D[🎙️ Synthesize Voice TTS]
    D --> E[🎬 Assemble Final Video]
    E --> F[📤 Upload to AWS S3 / YouTube]
```

### ✨ Key Features

| Feature                        | Description                                                      |
| ------------------------------ | ---------------------------------------------------------------- |
| 🛡️ **User Accounts**            | Secure multi-tenant architecture with JWT authentication         |
| 🧠 **Smart Content Ingestion** | Extract article text from RSS feeds and standard URLs            |
| 🎯 **Retention Optimization**  | Word-by-word subtitles with karaoke effect and neon progress bar |
| 🗣️ **Dynamic Voices**          | Realistic voice cloning using Coqui TTS with gender variation    |
| ☁️ **Cloud Storage**            | Final videos automatically uploaded to AWS S3 to save space      |
| 🐳 **Dockerized**              | Simple consistent deployment with one command                    |

---

## ✅ Testing Status (Current) + Coverage Goals

Current repository test suites:

- `tests/test_content_ingester_ssrf.py` → SSRF and URL safety checks for ingestion logic.
- `tests/test_workflow.py` → workflow drafting error-path behavior.
- `tests/test_reddit_scraper.py` → legacy Reddit filtering rules.
- `tests/test_youtube_uploader.py` → upload behavior with mocked YouTube API client.

Current state in a fresh environment: tests are present and runnable with `pytest`, but collection fails until optional runtime dependencies are installed (e.g. `feedparser`, `boto3`, Google API libs), and one legacy test module mocking strategy conflicts with `requests` imports.

Next practical coverage goals:

1. Add lightweight dependency groups (or test-only extras) so CI can install a deterministic test stack.
2. Expand API route tests for auth/projects/sources/workflow endpoints with `TestClient`.
3. Add database-level tests around multi-tenant isolation and status transitions.
4. Add frontend unit tests (Vitest + React Testing Library) for dashboard and workflow UX.

---

## 🧭 Legacy vs Current Code Paths

### Current (actively used by API-driven app)

- `app/main.py` → FastAPI app entrypoint.
- `app/api/` → route modules for auth, projects, source ingestion, workflow actions.
- `app/content_ingester.py` → URL/RSS ingestion used by API routes.
- `app/workflow.py` → drafting + generation orchestration used by workflow routes.
- `app/database/` and `app/models/` → persistence + domain models.

### Legacy / standalone scripts (kept for V1 compatibility and utilities)

- `main.py` → old autonomous script entrypoint.
- `reddit_scraper.py` → Reddit-based source collector from V1 flow.
- `text_processor.py`, `tts_generator.py`, `video_assembler.py`, `video_downloader.py`, `video_segmenter.py`, `youtube_uploader.py` → standalone modules from script-based pipeline, some still imported by newer orchestration but not exposed directly as API route modules.

If you're building new backend features, prefer adding functionality under `app/` and exposing it through `app/api/*`.

---

## 🔌 Backend API Quick Start

Run backend (Docker or local) and open interactive API docs:

- Swagger UI: `http://localhost:8080/docs`
- OpenAPI JSON: `http://localhost:8080/openapi.json`
- Health check: `GET /health`

Key endpoint groups (all mounted under `/api`):

- **Auth**
  - `POST /api/register`
  - `POST /api/token`
- **Projects**
  - `GET /api/projects`
  - `GET /api/projects/{project_id}`
- **Sources**
  - `GET /api/sources`
  - `POST /api/sources/url`
  - `POST /api/sources/rss`
  - `POST /api/sources/{source_id}/fetch`
- **Workflow**
  - `POST /api/projects/{project_id}/draft`
  - `PUT /api/projects/{project_id}/draft`
  - `POST /api/projects/{project_id}/approve`

---

## 📁 Project Structure

```text
Redishort/
├── app/                         # FastAPI backend (current architecture)
│   ├── api/                     # Route modules (auth/projects/sources/workflows)
│   │   ├── auth.py
│   │   ├── routes.py
│   │   ├── source_routes.py
│   │   └── workflow_routes.py
│   ├── database/                # SQLAlchemy base/session/models wiring
│   ├── models/                  # Pydantic/domain schemas
│   ├── content_ingester.py      # URL + RSS ingestion logic (current path)
│   ├── workflow.py              # Workflow orchestration (current path)
│   └── main.py                  # FastAPI app entrypoint
├── tests/                       # Pytest suites
├── frontend/                    # React/Vite frontend
├── assets/                      # Generated/raw media assets
├── prompts/                     # Prompt templates for generation
├── main.py                      # Legacy autonomous entrypoint (V1)
├── reddit_scraper.py            # Legacy Reddit collector (V1)
├── text_processor.py            # Shared/legacy generation module
├── tts_generator.py             # Shared/legacy TTS module
├── video_assembler.py           # Shared/legacy video assembly module
├── youtube_uploader.py          # Shared/legacy YouTube upload module
├── docker-compose.yml
└── Dockerfile
```

---

## 🔧 Development Setup

### Prerequisites

- Git
- Docker and Docker Compose
- AWS Account (for S3 bucket)
- Google API Key (for Gemini)

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/izan-co/Redishort.git
cd Redishort
```

#### 2️⃣ Configure Environment Variables

```bash
cp .env.example .env
```

> 💡 Open `.env` and fill in your credentials for Google Gemini, AWS S3, and JWT secrets.

#### 3️⃣ Prepare Assets

- **Voice Samples**: Place `.wav` files in `assets/voice_samples/male/` and `assets/voice_samples/female/`

#### 4️⃣ Launch

```bash
docker compose up --build -d api
```

The FastAPI backend will be available on `http://localhost:8080`.

---

## 🏃 Run modes

Redishort supports two runtime modes, with **API mode as the default**:

- **API mode (default, recommended)**
  - Entry point: `app/main.py` (FastAPI app)
  - Compose service: `api`
  - Start command: `docker compose up --build -d api`
  - Use this when running the React frontend and backend APIs together.

- **Autonomous mode (legacy V1 bot loop)**
  - Entry point: `main.py`
  - Compose service/profile: `autonomous` under `--profile autonomous`
  - Start command: `docker compose --profile autonomous up --build -d autonomous`
  - Use this when you want the old fully automated script loop (scrape → generate → upload) without the frontend workflow.

---

## ⚠️ Disclaimer

This project was created for **educational purposes** and personal task automation. Compliance with platform Terms of Service, content copyright, and API usage limits is the user's responsibility.

---

<div align="center">

**Built by Izan Cano** • Summer 2025

[🔗 View Live Channel](https://www.youtube.com/@reditoktv)

</div>
