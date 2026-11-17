#!/usr/bin/env bash
# Deploy the Story-to-Shorts Pipeline to Google Cloud Run Jobs (Zero local CPU/RAM)
set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "your-gcp-project")
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/story-video-pipeline:latest"
JOB_NAME="story-video-pipeline-job"

echo "=================================================="
echo " Deploying Story Video Engine to Google Cloud Run "
echo "=================================================="

# 1. Build & Push Docker image to Google Container Registry
echo "1. Building and pushing container..."
gcloud builds submit --tag "${IMAGE_NAME}" .

# 2. Create or update Cloud Run Job (allocated 4 vCPUs and 8GB RAM for fast rendering)
echo "2. Creating Cloud Run Job '${JOB_NAME}'..."
gcloud run jobs create "${JOB_NAME}" \
  --image "${IMAGE_NAME}" \
  --region "${REGION}" \
  --cpu "4" \
  --memory "8Gi" \
  --max-retries "1" \
  --task-timeout "15m" \
  --command "python3" \
  --args "story_runner.py" \
  --set-env-vars "PYTHONUNBUFFERED=1" \
  || gcloud run jobs update "${JOB_NAME}" --image "${IMAGE_NAME}" --region "${REGION}"

# 3. Schedule automatic execution every 8 hours via Google Cloud Scheduler
echo "3. Creating 8-Hour Cloud Scheduler Trigger..."
gcloud scheduler jobs create http "${JOB_NAME}-trigger" \
  --location "${REGION}" \
  --schedule "0 */8 * * *" \
  --uri "https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" \
  --http-method POST \
  --oauth-service-account-email "${PROJECT_ID}@appspot.gserviceaccount.com" \
  || echo "Scheduler already exists."

echo ""
echo "🎉 Deployment Complete!"
echo "The pipeline will now execute in the cloud every 8 hours completely hands-free."
echo "Your laptop will never run, freeze, or heat up!"
