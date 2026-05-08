# ── GCP Setup Script for TravelAI ────────────────────────────────────────────
# Run this AFTER installing Google Cloud SDK and restarting your terminal
# Usage: .\infra\scripts\setup-gcp.ps1 -ProjectId "your-project-id"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,

    [string]$Region = "us-central1",

    [Parameter(Mandatory=$true)]
    [string]$DatabaseUrl,   # Neon PostgreSQL URL

    [Parameter(Mandatory=$true)]
    [string]$RedisUrl        # Upstash Redis URL
)

$ErrorActionPreference = "Stop"

Write-Host "Setting up TravelAI on GCP project: $ProjectId" -ForegroundColor Cyan

# ── Authenticate & configure ──────────────────────────────────────────────────
Write-Host "`n[1/7] Authenticating..." -ForegroundColor Yellow
gcloud auth login
gcloud config set project $ProjectId
gcloud config set run/region $Region

# ── Enable required APIs ──────────────────────────────────────────────────────
Write-Host "`n[2/7] Enabling APIs..." -ForegroundColor Yellow
gcloud services enable `
    run.googleapis.com `
    containerregistry.googleapis.com `
    secretmanager.googleapis.com `
    cloudbuild.googleapis.com

# ── Store secrets in Secret Manager ──────────────────────────────────────────
Write-Host "`n[3/7] Storing secrets..." -ForegroundColor Yellow

function Set-Secret($name, $value) {
    $value | gcloud secrets create $name --data-file=- 2>$null
    if ($LASTEXITCODE -ne 0) {
        $value | gcloud secrets versions add $name --data-file=-
    }
    Write-Host "  Stored: $name" -ForegroundColor Green
}

# Read from local .env
$env_content = Get-Content ".env" | Where-Object { $_ -match "^[A-Z_]+=.+" }
$env_vars = @{}
foreach ($line in $env_content) {
    $parts = $line -split "=", 2
    $env_vars[$parts[0]] = $parts[1].Trim('"')
}

Set-Secret "GEMINI_API_KEY"       $env_vars["GEMINI_API_KEY"]
Set-Secret "GOOGLE_MAPS_API_KEY"  $env_vars["GOOGLE_MAPS_API_KEY"]
Set-Secret "OPENWEATHER_API_KEY"  $env_vars["OPENWEATHER_API_KEY"]
Set-Secret "DATABASE_URL"         $DatabaseUrl
Set-Secret "REDIS_URL"            $RedisUrl
Set-Secret "SECRET_KEY"           [System.Web.Security.Membership]::GeneratePassword(32, 4)

# ── Build & push backend ──────────────────────────────────────────────────────
Write-Host "`n[4/7] Building backend image..." -ForegroundColor Yellow
$commitSha = git rev-parse --short HEAD
$backendImage = "gcr.io/$ProjectId/travelai-backend:$commitSha"
gcloud auth configure-docker --quiet
podman build -t $backendImage ./backend
podman push $backendImage

# ── Build & push geo-service ──────────────────────────────────────────────────
Write-Host "`n[5/7] Building geo-service image..." -ForegroundColor Yellow
$geoImage = "gcr.io/$ProjectId/travelai-geo-service:$commitSha"
podman build -t $geoImage ./services/geo-service
podman push $geoImage

# ── Deploy backend to Cloud Run ───────────────────────────────────────────────
Write-Host "`n[6/7] Deploying backend to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy travelai-backend `
    --image $backendImage `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --min-instances 1 `
    --max-instances 3 `
    --memory 512Mi `
    --cpu 1 `
    --port 8000 `
    --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest,GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY:latest,OPENWEATHER_API_KEY=OPENWEATHER_API_KEY:latest,DATABASE_URL=DATABASE_URL:latest,REDIS_URL=REDIS_URL:latest,SECRET_KEY=SECRET_KEY:latest" `
    --set-env-vars "ENVIRONMENT=production,DEV_MODE=true,GEO_SERVICE_URL=https://travelai-geo-service-$Region.run.app,GRAPHITI_SERVICE_URL=https://travelai-graphiti-service-$Region.run.app"

$backendUrl = gcloud run services describe travelai-backend --region=$Region --format="value(status.url)"
Write-Host "  Backend: $backendUrl" -ForegroundColor Green

# ── Deploy geo-service to Cloud Run ──────────────────────────────────────────
Write-Host "`n[7/7] Deploying geo-service to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy travelai-geo-service `
    --image $geoImage `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --min-instances 0 `
    --max-instances 2 `
    --memory 256Mi `
    --cpu 1 `
    --port 8080 `
    --set-secrets "GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY:latest" `
    --set-env-vars "REDIS_URL=$RedisUrl"

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Deployment complete!" -ForegroundColor Green
Write-Host " Backend API: $backendUrl" -ForegroundColor White
Write-Host " API Docs:    $backendUrl/docs" -ForegroundColor White
Write-Host "`n Next: Deploy frontend to Vercel" -ForegroundColor Yellow
Write-Host "  1. Go to vercel.com/new" -ForegroundColor White
Write-Host "  2. Import github.com/balajisainath/PromptWars" -ForegroundColor White
Write-Host "  3. Set NEXT_PUBLIC_API_URL=$backendUrl" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
