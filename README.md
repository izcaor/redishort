# Redishort 🤖 - Full-Stack YouTube Shorts Creator

![Logo](redishort.png)

> **Project Status: Active Development / Evolution**
> This project originally started as an autonomous python script scraping Reddit. It has now evolved into a **multi-tenant full-stack SaaS-like application** featuring a React frontend, a FastAPI backend, JWT authentication, AWS S3 storage, and RSS/URL-based content ingestion!

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

This project demonstrates proficiency across the stack:

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

| Feature                       | Description                                                      |
| ----------------------------- | ---------------------------------------------------------------- |
| 🛡️ **User Accounts**           | Secure multi-tenant architecture with JWT authentication         |
| 🧠 **Smart Content Ingestion**| Extract article text from RSS feeds and standard URLs            |
| 🎯 **Retention Optimization** | Word-by-word subtitles with karaoke effect and neon progress bar |
| 🗣️ **Dynamic Voices**         | Realistic voice cloning using Coqui TTS with gender variation    |
| ☁️ **Cloud Storage**           | Final videos automatically uploaded to AWS S3 to save space      |
| 🐳 **Dockerized**             | Simple consistent deployment with one command                    |

---

## 🚀 Possible Upgrades & Roadmap

We are continuously looking to improve the system. Potential future enhancements include:

- **Asynchronous Task Queues**: Integrate **Celery** and Redis/RabbitMQ to handle video rendering and long-running AI tasks reliably outside the main web process.
- **Automated Testing**: Add `pytest` for the backend and `Vitest` or `Jest` for the frontend to ensure stability across features.
- **Enhanced Frontend Workflow**: Improve UI for reviewing AI-generated scripts and selecting different background videos manually.
- **More Content Sources**: Add integrations for Twitter/X threads, HackerNews, and direct PDF/Text uploads.
- **Multi-Platform Publishing**: Automatically schedule and post not just to YouTube, but also to TikTok and Instagram Reels via their APIs.
- **Database Switch**: Move from SQLite/Local DBs to PostgreSQL for true production scaling.

---

## 📁 Project Structure

```
Redishort/
├── app/                  # FastAPI Backend
│   ├── api/              # Route controllers (auth, projects, workflows)
│   ├── database/         # SQLAlchemy models and connection
│   └── models/           # Pydantic domain schemas
├── frontend/             # React/Vite Frontend
│   ├── src/              # React components and views
│   └── public/           # Static assets
├── assets/               # Generated and raw video assets (local cache)
├── prompts/              # System prompts for Gemini LLM
├── config.py             # Central configuration
├── main.py               # Legacy autonomous entry point (V1)
├── app/main.py           # New FastAPI entry point (V2)
├── content_ingester.py   # RSS and URL parsing logic
├── text_processor.py     # LLM script generation
├── tts_generator.py      # Text-to-speech
├── video_assembler.py    # Video composition
├── video_downloader.py   # Background video download
├── video_segmenter.py    # Video processing
├── youtube_uploader.py   # YouTube API upload
├── docker-compose.yml    # Infrastructure setup
└── Dockerfile            # Application container setup
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
docker-compose up --build -d
```

The FastAPI backend will be available on `http://localhost:8080`.
*(Note: To develop the frontend independently, navigate to `frontend/` and run `npm run dev`)*

---

## ⚠️ Disclaimer

This project was created for **educational purposes** and personal task automation. Compliance with platform Terms of Service, content copyright, and API usage limits is the user's responsibility.

---

<div align="center">

**Built by Izan Cano** • Summer 2025

[🔗 View Live Channel](https://www.youtube.com/@reditoktv)

</div>
