# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RedInk (红墨) is an AI-powered content generation tool for creating Xiaohongshu (Little Red Book) posts. It generates complete graphic-text content including outlines, titles, body copy, tags, and images from a single user input.

**Tech Stack:**
- Backend: Python 3.11+ / Flask
- Frontend: Vue 3 + TypeScript / Vite
- Package Managers: uv (backend), pnpm (frontend)
- AI: Google Gemini 2.0 Flash (text), Google GenAI/OpenAI-compatible APIs (images)

## Common Commands

### Development

```bash
# Backend (run from project root)
uv sync                          # Install backend dependencies
uv run python -m backend.app     # Start backend (port 12398)

# Frontend
cd frontend
pnpm install                     # Install frontend dependencies
pnpm dev                         # Start frontend dev server (port 5173)
pnpm build                       # Build for production
pnpm preview                     # Preview production build
```

### Quick Start Scripts

```bash
# Windows: Double-click start.bat
# macOS: ./start.sh or double-click scripts/start-macos.command
# Linux: ./start.sh
```

### Docker

```bash
docker build -t redink .
docker run -d -p 12398:12398 -v ./history:/app/history -v ./output:/app/output histonemax/redink:latest
docker-compose up -d
```

### Testing

```bash
pytest                           # Run all backend tests
pytest tests/test_outline.py     # Run specific test file
pytest -k "test_outline"         # Run tests matching pattern
```

## Architecture

### Backend Structure

```
backend/
├── app.py              # Flask application factory, entry point
├── config.py           # Configuration management (Config class)
├── generators/         # Image generation strategy pattern (Factory)
│   ├── base.py        # ImageGeneratorBase abstract class
│   ├── factory.py     # Creates generator by provider type
│   ├── google_genai.py
│   ├── openai_compatible.py
│   └── image_api.py
├── prompts/           # AI prompt templates
├── routes/            # Modular Flask Blueprints
│   ├── outline_routes.py   # POST /api/outline
│   ├── image_routes.py     # POST /api/generate, GET /api/images/<task_id>/<filename>
│   ├── history_routes.py   # CRUD for history records
│   ├── config_routes.py    # GET/POST /api/config
│   └── content_routes.py   # POST /api/content
├── services/          # Business logic layer
│   ├── outline.py     # Outline generation from AI
│   ├── image.py       # Image generation with SSE streaming
│   ├── history.py     # File-based persistence
│   └── content.py     # Title/copy/tags generation
└── utils/
    ├── genai_client.py    # Google GenAI client wrapper
    ├── text_client.py     # Text generation client
    └── image_compressor.py
```

### Frontend Structure

```
frontend/src/
├── main.ts             # Vue app initialization
├── App.vue             # Root component
├── components/         # Reusable Vue components
├── stores/             # Pinia state management
├── views/              # Page components
└── router/             # Vue Router configuration
```

### Key Design Patterns

1. **Blueprint Pattern**: Modular route organization in Flask (`routes/`)
2. **Factory Pattern**: Pluggable image generators (`generators/factory.py`)
3. **Service Layer**: Business logic separated from routes (`services/`)
4. **SSE Streaming**: Real-time image generation progress via `/api/generate`
5. **Repository Pattern**: History service abstracts file-based storage

### API Endpoints

All APIs are prefixed with `/api`:

- **Outline**: `POST /api/outline` - Generate outline from topic (supports image uploads)
- **Images**: `POST /api/generate`, `GET /api/images/<task_id>/<filename>`, `POST /api/retry`, `POST /api/regenerate`
- **History**: `GET/POST/PUT/DELETE /api/history`, `GET /api/history/<record_id>/download`
- **Config**: `GET/POST /api/config`, `POST /api/config/test`
- **Content**: `POST /api/content` - Generate titles, copy, tags

## Configuration

### Configuration Files

- `text_providers.yaml` - Text generation API settings (Gemini, OpenAI-compatible)
- `image_providers.yaml` - Image generation API settings

**Structure:**
```yaml
active_provider: provider_name
providers:
  provider_name:
    type: google_gemini | openai_compatible | google_genai | image_api
    api_key: sk-xxxx
    base_url: https://...
    model: model_name
    high_concurrency: false  # Enable for parallel image generation (max 15)
```

### Configuration Loading

- Backend uses singleton pattern with caching in `backend/config.py`
- Web UI at `/settings` provides visual configuration management
- Config changes reload immediately (cache invalidation)
- On startup, `create_app()` validates config and logs warnings for missing API keys

## Data Persistence

### Storage Structure

```
history/
├── {record_id}.json          # History record metadata
└── {task_id}/                # Task-specific directory
    ├── 0.png                 # Generated images
    ├── thumb_0.png           # Thumbnails (300px width)
    └── cover_image.png       # Cover reference for regeneration

output/                        # Legacy output directory
```

### History Record Schema

```json
{
  "id": "uuid",
  "title": "Topic",
  "status": "draft|generating|partial|completed|error",
  "outline": { "raw": "...", "pages": [...] },
  "images": { "task_id": "...", "generated": ["0.png", "1.png"] },
  "thumbnail": "0.png",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

## Important Deployment Notes

### Development vs Production Mode

- **Development**: Frontend runs on Vite dev server (5173), Flask on 12398, CORS enabled
- **Production (Docker)**: Flask serves both API and static frontend files from `frontend/dist/`
- Backend auto-detects `frontend/dist/` existence and switches to static file serving mode

### High Concurrency Mode

- **Disabled (default)**: Images generated sequentially (safe for GCP $300 trial accounts with rate limits)
- **Enabled**: Images generated in parallel (up to 15 concurrent), faster but requires API that supports high concurrency
- Set via `high_concurrency: true` in `image_providers.yaml`

### Docker Deployment

- Multi-stage build: Node.js builder → Python 3.11 slim runtime
- Health check: `/api/health`
- Volume mounts required for persistence: `./history:/app/history`, `./output:/app/output`
- Configuration files optional (can use Web UI)

## License

This project is licensed under **CC BY-NC-SA 4.0** (non-commercial). For commercial use, contact the author at histonemax@gmail.com.