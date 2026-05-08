#!/usr/bin/env bash
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
COMMIT_SHA=$(git rev-parse --short HEAD)

echo "Deploying travelai platform (commit: $COMMIT_SHA)"
echo "Project: $PROJECT_ID | Region: $REGION"

# ── Authenticate ──────────────────────────────────────────────────────────────
gcloud config set project "$PROJECT_ID"
gcloud auth configure-docker --quiet

# ── Build & Push Backend ──────────────────────────────────────────────────────
echo "[1/5] Building backend..."
docker build -t "gcr.io/$PROJECT_ID/travelai-backend:$COMMIT_SHA" ./backend
docker push "gcr.io/$PROJECT_ID/travelai-backend:$COMMIT_SHA"

# ── Build & Push Geo-Service ──────────────────────────────────────────────────
echo "[2/5] Building geo-service..."
docker build -t "gcr.io/$PROJECT_ID/travelai-geo-service:$COMMIT_SHA" ./services/geo-service
docker push "gcr.io/$PROJECT_ID/travelai-geo-service:$COMMIT_SHA"

# ── Deploy Backend to Cloud Run ───────────────────────────────────────────────
echo "[3/5] Deploying backend to Cloud Run..."
gcloud run deploy travelai-backend \
  --image "gcr.io/$PROJECT_ID/travelai-backend:$COMMIT_SHA" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 3 \
  --memory 512Mi \
  --cpu 1 \
  --port 8000 \
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest,GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY:latest,FIREBASE_PROJECT_ID=FIREBASE_PROJECT_ID:latest,FIREBASE_CLIENT_EMAIL=FIREBASE_CLIENT_EMAIL:latest,FIREBASE_PRIVATE_KEY=FIREBASE_PRIVATE_KEY:latest,OPENWEATHER_API_KEY=OPENWEATHER_API_KEY:latest" \
  --set-env-vars "ENVIRONMENT=production"

BACKEND_URL=$(gcloud run services describe travelai-backend --region="$REGION" --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"

# ── Deploy Geo-Service to Cloud Run ──────────────────────────────────────────
echo "[4/5] Deploying geo-service to Cloud Run..."
gcloud run deploy travelai-geo-service \
  --image "gcr.io/$PROJECT_ID/travelai-geo-service:$COMMIT_SHA" \
  --region "$REGION" \
  --platform managed \
  --no-allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --memory 256Mi \
  --cpu 1 \
  --port 8080

# ── Deploy Frontend to Vercel ─────────────────────────────────────────────────
echo "[5/5] Deploying frontend to Vercel..."
cd frontend
if command -v vercel &>/dev/null; then
  vercel deploy --prod \
    --env NEXT_PUBLIC_API_URL="$BACKEND_URL" \
    --yes
else
  echo "Vercel CLI not found. Install with: npm i -g vercel"
fi
cd ..

echo ""
echo "Deployment complete!"
echo "Backend: $BACKEND_URL"
echo "API Docs: $BACKEND_URL/docs"
