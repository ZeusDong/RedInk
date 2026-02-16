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
pytest tests/test_recommendation_semantic.py  # Run recommendation tests
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
│   └── recommendation_prompts.py  # Prompts for semantic scoring
├── routes/            # Modular Flask Blueprints
│   ├── outline_routes.py      # POST /api/outline
│   ├── image_routes.py        # POST /api/generate, GET /api/images/<task_id>/<filename>
│   ├── history_routes.py      # CRUD for history records
│   ├── config_routes.py       # GET/POST /api/config
│   ├── content_routes.py      # POST /api/content
│   ├── reference_routes.py    # Feishu reference queries
│   ├── oauth_routes.py        # OAuth authentication
│   ├── analysis_routes.py     # Content analysis features
│   ├── summary_routes.py      # AI summary generation
│   ├── recommendation_routes.py  # V2.0 intelligent recommendations
│   ├── template_routes.py     # Template management
│   ├── optimizer_routes.py    # Content optimization
│   └── image_proxy_routes.py  # Image proxy for external images
├── services/          # Business logic layer
│   ├── outline.py     # Outline generation from AI
│   ├── image.py       # Image generation with SSE streaming
│   ├── history.py     # File-based persistence
│   ├── content.py     # Title/copy/tags generation
│   ├── feishu_service.py  # Feishu/Lark workspace integration (optional)
│   └── recommendation_service.py  # V2.0 recommendation engine
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
│   └── ai-creation/
│       └── smart-recommend/  # Smart recommendation UI components
├── stores/             # Pinia state management
│   ├── generator.ts    # Main workflow state (topic → outline → images → result)
│   ├── layout.ts       # UI layout state (sidebar collapse)
│   ├── reference.ts    # Reference image management
│   ├── analysis.ts     # Content analysis features
│   └── recommendation.ts  # V2.0 recommendation state management
├── views/              # Page components
├── router/             # Vue Router configuration
├── api/                # API client and type definitions
│   └── recommendation.ts  # Recommendation API client
├── types/              # TypeScript type definitions
│   └── recommendation.ts  # Recommendation type definitions
└── composables/        # Vue composables (e.g., useProviderForm)
```

**Frontend Configuration:**
- TypeScript path alias: `@/*` → `./src/*` (use `@/stores/...` in imports)
- Vite dev server proxies `/api` requests to `http://localhost:12398`
- Strict TypeScript enabled with `noUnusedLocals` and `noUnusedParameters`

### State Management Patterns

The frontend uses Pinia for state management with the following key stores:

**Generator Store** ([`stores/generator.ts`](frontend/src/stores/generator.ts)):
- Manages the complete workflow: `input` → `outline` → `generating` → `result`
- Auto-saves to localStorage on every state change (via `watch`)
- Persists: topic, outline, images, progress, taskId, recordId, content
- Excludes: `userImages` (File objects cannot be serialized)
- Methods for page manipulation: `updatePage`, `deletePage`, `addPage`, `insertPage`, `movePage`

**Layout Store** ([`stores/layout.ts`](frontend/src/stores/layout.ts)):
- Manages sidebar collapse state with localStorage persistence
- Simple boolean toggle for responsive UI

**Reference & Analysis Stores**:
- Reference store manages image library for style reference
- Analysis store handles content analysis features

### Key Design Patterns

1. **Blueprint Pattern**: Modular route organization in Flask (`routes/`)
2. **Factory Pattern**: Pluggable image generators (`generators/factory.py`)
3. **Service Layer**: Business logic separated from routes (`services/`)
4. **SSE Streaming**: Real-time image generation progress via `/api/generate`
5. **Repository Pattern**: History service abstracts file-based storage
6. **Hybrid Synonym Expansion**: Manual config + AI approach for keyword expansion
7. **Semantic Scoring**: Multi-dimensional AI scoring with caching
8. **Lazy Loading Insights**: AI extraction of learnable elements on demand
9. **Dual Cache System**: Separate caches for recommendations and semantic scores

### API Endpoints

All APIs are prefixed with `/api`:

**Core Generation:**
- **Outline**: `POST /api/outline` - Generate outline from topic (supports image uploads)
- **Images**: `POST /api/generate`, `GET /api/images/<task_id>/<filename>`, `POST /api/retry`, `POST /api/regenerate`
- **Content**: `POST /api/content` - Generate titles, copy, tags

**History Management:**
- **History**: `GET/POST/PUT/DELETE /api/history`, `GET /api/history/<record_id>/download`
- **Health**: `GET /api/health` - Docker health check endpoint

**Configuration:**
- **Config**: `GET/POST /api/config`, `POST /api/config/test`

**Feishu Integration (Optional):**
- **OAuth**: `GET /api/oauth/authorize`, `GET /api/oauth/callback`
- **Reference**: `GET /api/reference/records`, `GET /api/reference/stats`, `POST /api/reference/sync`

**Analysis:**
- **Analysis**: `GET /api/analysis/pending` - CRUD for pending analysis notes

**Recommendation System (V2.0):**
- **Recommendations**: `POST /api/recommendations` - Get intelligent recommendations with semantic scoring
- **Similar**: `GET /api/recommendations/similar/<record_id>` - Find similar notes
- **Industries**: `GET /api/recommendations/industries` - Get available industries
- **Clear Cache**: `DELETE /api/recommendations/cache` - Clear recommendation cache
- **Cache Stats**: `GET /api/recommendations/cache/stats` - Get cache statistics

## Configuration

### Configuration Files

- `text_providers.yaml` - Text generation API settings (Gemini, OpenAI-compatible)
- `image_providers.yaml` - Image generation API settings
- `feishu_providers.yaml` - Feishu (Lark) workspace integration settings (optional)
- `synonyms.yaml` - Synonym dictionary for recommendation system (in .gitignore)

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

### Synonyms Configuration

- `synonyms.yaml` - Manual synonyms configuration for recommendation system (in .gitignore)
- Hybrid synonym expansion: manual config + AI for keyword expansion
- Thread-safe loading and saving with auto-updates from AI discoveries

## Intelligent Recommendation System (V2.0)

### Core Features

- **Semantic Scoring**: Multi-dimensional AI scoring (0-10 scale) with:
  - Topic Relevance (40%): How well the note matches the search topic
  - Audience Match (30%): Target user alignment
  - Style Fit (20%): Content style compatibility
  - Performance Bonus (10%): Engagement metrics

- **Synonym Expansion**: Hybrid approach using config + AI to prevent keyword dilution
- **Learning Elements Extraction**: AI extracts hooks, structure, tone, CTAs from notes
- **Cache System**: Dual-cache for recommendations (7-day expiry) and semantic scores
- **Match Levels**: High (≥0.7), Medium (≥0.4), Low (<0.4)

### Database Tables

- `recommendation_cache`: Stores AI-extracted insights
- `semantic_scores_cache`: Stores semantic scores for notes

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