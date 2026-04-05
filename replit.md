# HR Agent System

AI-powered HR automation system with a Next.js 15 frontend and Python FastAPI backend.

## Architecture

- **Frontend**: Next.js 15 + React 19, Tailwind CSS, shadcn/ui, NextAuth v4, Prisma ORM
- **Backend**: Python FastAPI with SQLAlchemy, running on port 8000
- **Database**: PostgreSQL (Replit-managed via `DATABASE_URL`)

## Workflows

- **Start application** — Next.js dev server on port 5000 (main web view)
- **Backend API** — FastAPI server on port 8000 (Python)
- **Project** — Runs both in parallel (the run button)

## Key Environment Variables

- `DATABASE_URL` — PostgreSQL connection (auto-provided by Replit)
- `NEXTAUTH_SECRET` — Required for NextAuth session signing (set in Secrets)
- `NEXTAUTH_URL` — Set to `http://localhost:5000`
- `FASTAPI_BASE` — Backend URL, set to `http://localhost:8000`
- `BACKEND_CORS_ORIGINS` — CORS allowed origins, set to `http://localhost:5000`
- Optional AI keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`

## Package Manager

- Node.js: **pnpm** (v10)
- Python: **pip** (packages installed to `.pythonlibs/`)

## Notable Fixes (Vercel → Replit Migration)

1. Dev/start scripts updated to use `-p 5000 -H 0.0.0.0`
2. All context providers (SessionProvider, AuthProvider, etc.) moved into a client component wrapper (`components/providers/providers.tsx`) to fix React Server Components compatibility
3. Backend CORS changed from wildcard `*` to controlled origins list via env var
4. Python backend heavy ML imports (torch, transformers, azure-speech, google-cloud) made optional with graceful degradation
5. SQLAlchemy Base unified across `sql_database.py` and `sql_models.py`
6. Missing `__init__.py` files created for agent packages
7. Prisma schema relation naming fixed for `TrainingNeedsAnalysis`

## Frontend Structure

- `app/` — Next.js App Router pages
- `components/` — React components (shadcn/ui + custom)
- `components/providers/` — Client-side context providers
- `lib/` — Auth, DB (Prisma), and utility helpers
- `prisma/schema.prisma` — Database schema

## Backend Structure

- `backend/main.py` — FastAPI app entry point
- `backend/agents/` — AI agent classes
- `backend/models/` — SQLAlchemy models
- `backend/database/` — DB connection setup
- `backend/utils/config.py` — Settings via pydantic-settings
