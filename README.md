# TravelAI — AI-Powered Trip Planning Platform

A full-stack AI travel planning application built with LangGraph, Gemini, Graphiti, and Qdrant.

## Architecture

- **Frontend**: Next.js 14, TypeScript, Tailwind, Firebase Auth
- **Backend**: FastAPI, LangGraph, Gemini Free API
- **Geo-Service**: Go, Gin, Google Maps API
- **Memory**: Graphiti + Neo4j graph memory
- **Vector DB**: Qdrant for semantic itinerary search
- **Cache**: Redis (LLM outputs, embeddings, geo data)
- **Events**: RabbitMQ for async jobs
- **Observability**: Prometheus + Grafana + Loki

## Quick Start (Local)

### Prerequisites
- Docker + Docker Compose
- API keys (see `.env.example`)

### Setup
```bash
cp .env.example .env
# Edit .env with your API keys:
# - GEMINI_API_KEY (free at ai.google.dev)
# - GOOGLE_MAPS_API_KEY
# - FIREBASE_PROJECT_ID + credentials
# - OPENWEATHER_API_KEY (free tier)

# Start core services (FastAPI + Postgres + Redis + Qdrant)
docker compose --profile ai up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Access the app
open http://localhost:3000     # Frontend
open http://localhost:8000/docs # API Docs
open http://localhost:9090     # Prometheus (with --profile full)
open http://localhost:3001     # Grafana (admin/admin)
```

## Deploy to Google Cloud

### Prerequisites
- GCP project with billing enabled
- `gcloud` CLI authenticated
- Firebase project configured

### Deploy
```bash
export GCP_PROJECT_ID=your-project-id
./infra/scripts/deploy.sh
```

### Required Secrets (Secret Manager)
```
GEMINI_API_KEY
GOOGLE_MAPS_API_KEY
FIREBASE_PROJECT_ID
FIREBASE_CLIENT_EMAIL
FIREBASE_PRIVATE_KEY
OPENWEATHER_API_KEY
```

## Environment Variables

See `.env.example` for the complete list.

## CI/CD

GitHub Actions workflows in `.github/workflows/`:
- `ci.yml` — linting + tests on every PR
- `cd.yml` — build + deploy to Cloud Run + Vercel on merge to main

Required GitHub Secrets:
- `GCP_SA_KEY` — GCP service account JSON
- `GCP_PROJECT_ID` — GCP project ID
- `VERCEL_TOKEN` — Vercel deployment token
- `VERCEL_ORG_ID` — Vercel org ID
- `VERCEL_PROJECT_ID` — Vercel project ID
