# Deployment Guide

This guide covers deploying the National Curriculum for England SPARQL endpoint to Google Cloud Run.

## Quick Start (TL;DR)

**Just want to deploy?**

```bash
./deployment/deploy.sh
```

That's it! The script will:
- ✅ Validate your data
- ✅ Build the Docker image
- ✅ Push to Google Container Registry
- ✅ Deploy to Cloud Run
- ✅ Test the deployment
- ✅ Show you the service URL

**For detailed step-by-step instructions, troubleshooting, and monitoring, see the sections below.**

---

## Prerequisites

Before deploying, ensure you have:

- **Google Cloud SDK** installed and configured (`gcloud` command)
- **Docker** installed and running
- **GCP project** with billing enabled
- **Required APIs enabled**:
  - Cloud Run API (`run.googleapis.com`)
  - Container Registry API (`containerregistry.googleapis.com`)
  - Cloud Build API (`cloudbuild.googleapis.com`)

See [Step 17 in IMPLEMENTATION-PLAN.md](../IMPLEMENTATION-PLAN.md#step-17-set-up-google-cloud-project) for detailed setup instructions.

---

## Manual Deployment

### 1. Set Environment Variables

```bash
# Set your GCP project ID
export PROJECT_ID="oak-ai-playground"

# Set deployment region
export REGION="europe-west1"

# Set service name
export SERVICE_NAME="national-curriculum-for-england-sparql"

# Set image name
export IMAGE="gcr.io/${PROJECT_ID}/national-curriculum-for-england-fuseki"

# Verify settings
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Image: $IMAGE"
```

**Note:** `europe-west1` (Belgium) is more cost-effective than `europe-west2` (London) with minimal performance difference.

---

### 2. Build Docker Image

```bash
# Build with GCR tag
docker build -t ${IMAGE}:latest -f deployment/Dockerfile .

# Expected output:
# - Loaded 10 TTL files into TDB2
# - 1,380 triples loaded
# - TDB2 indexes created (SPO, POS, OSP)
```

**Build Details:**
- Base image: `stain/jena-fuseki:latest` (Fuseki 5.1.0)
- Data location: `/data/national-curriculum-for-england-tdb2/`
- Storage: TDB2 (high-performance triple store)
- Data loaded at build time (immutable deployment)

---

### 3. Authenticate and Push to GCR

```bash
# Configure Docker authentication for GCR
gcloud auth configure-docker

# Push image to Google Container Registry
docker push ${IMAGE}:latest
```

**What happens:**
- Image is pushed to `gcr.io/oak-ai-playground/`
- Layers are cached (subsequent pushes are faster)
- Image becomes available for Cloud Run deployment

---

### 4. Deploy to Cloud Run

```bash
gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE}:latest \
    --platform=managed \
    --region=${REGION} \
    --allow-unauthenticated \
    --port=3030 \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --min-instances=0 \
    --timeout=300 \
    --concurrency=80
```

**Configuration Explained:**
- `--allow-unauthenticated`: Public SPARQL endpoint (no API key required)
- `--port=3030`: Fuseki's default port
- `--memory=2Gi`: 2GB RAM (handles moderate query load)
- `--cpu=2`: 2 vCPU (good query performance)
- `--max-instances=10`: Auto-scale up to 10 containers under load
- `--min-instances=0`: Scale to zero when idle (cost savings)
- `--timeout=300`: 5-minute timeout for complex SPARQL queries
- `--concurrency=80`: Handle 80 concurrent requests per container

**Deployment time:** ~1-2 minutes

---

### 5. Get Service URL

```bash
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)')

echo "Service URL: ${SERVICE_URL}"
echo "SPARQL Endpoint: ${SERVICE_URL}/national-curriculum-for-england/sparql"
```

**Example Output:**
```
Service URL: https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app
SPARQL Endpoint: https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

---

## Testing Deployment

### Test 1: Health Check

```bash
curl -i ${SERVICE_URL}/\$/ping

# Expected: HTTP 200 OK
```

### Test 2: Count Triples

```bash
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    ${SERVICE_URL}/national-curriculum-for-england/sparql | jq .

# Expected: ~1,373 triples
```

### Test 3: Query Subjects

```bash
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data-binary @queries/subjects-index.sparql \
    ${SERVICE_URL}/national-curriculum-for-england/sparql | jq '.results.bindings'

# Expected: History and Science subjects
```

---

## Automated Deployment Script

For convenience, use the provided deployment script:

```bash
./deployment/deploy.sh
```

This script:
1. Validates TTL files locally
2. Builds the Docker image
3. Pushes to GCR
4. Deploys to Cloud Run
5. Tests the deployment
6. Outputs the service URL

---

## Updating the Deployment

To update curriculum data or configuration:

1. **Edit TTL files** in `data/` or `ontology/`
2. **Validate changes** locally:
   ```bash
   ./scripts/validate.sh
   ```
3. **Rebuild and redeploy**:
   ```bash
   docker build -t ${IMAGE}:latest -f deployment/Dockerfile .
   docker push ${IMAGE}:latest
   gcloud run deploy ${SERVICE_NAME} --image=${IMAGE}:latest --region=${REGION}
   ```

**Important:** Each deployment creates a new revision. Cloud Run supports zero-downtime deployments with automatic traffic migration.

---

## Monitoring

### View Logs

```bash
# Recent logs
gcloud run services logs read ${SERVICE_NAME} \
    --region=${REGION} \
    --limit=50

# Follow logs in real-time
gcloud run services logs tail ${SERVICE_NAME} \
    --region=${REGION}
```

### View Metrics

```bash
# Open Cloud Run metrics in browser
echo "https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
```

**Key Metrics:**
- Request count
- Request latency (P50, P95, P99)
- Container instance count
- CPU and memory utilization
- Error rate

### View Revisions

```bash
# List all revisions
gcloud run revisions list \
    --service=${SERVICE_NAME} \
    --region=${REGION}

# Traffic routing between revisions
gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.traffic)'
```

---

## Rollback

To rollback to a previous revision:

```bash
# List revisions to find the revision name
gcloud run revisions list --service=${SERVICE_NAME} --region=${REGION}

# Route 100% of traffic to a specific revision
gcloud run services update-traffic ${SERVICE_NAME} \
    --region=${REGION} \
    --to-revisions=REVISION_NAME=100
```

---

## Cost Estimates

**Monthly Operating Costs (based on actual usage):**

| Usage Level | Requests/Day | Estimated Cost |
|-------------|--------------|----------------|
| **Low** | 1,000 | $10-15/month |
| **Medium** | 10,000 | $20-30/month |
| **High** | 100,000 | $100-150/month |

**Pricing Factors:**
- vCPU-seconds used
- Memory (GB-seconds)
- Request count
- No charge when scaled to zero

**Cost Optimization:**
- Service auto-scales to zero when idle (free)
- Consider `--min-instances=1` to avoid cold starts (adds ~$10/month)

See [GCP Cloud Run Pricing](https://cloud.google.com/run/pricing) for details.

---

## Custom Domain Setup

To use a custom domain (e.g., `sparql.curriculum.education.gov.uk`):

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service=${SERVICE_NAME} \
    --domain=sparql.curriculum.education.gov.uk \
    --region=${REGION}

# Follow instructions to add DNS records
# (Cloud Run will provide the records to add)
```

---

## Security Considerations

**Current Configuration:**
- ✅ **Read-only access**: Only query and GSP-read endpoints enabled
- ✅ **No write operations**: Data cannot be modified via SPARQL
- ✅ **Public access**: No authentication required (intended for public curriculum data)
- ✅ **Query timeout**: 5-minute limit prevents runaway queries
- ✅ **Resource limits**: 2GB memory, 2 vCPU caps per container

**Future Enhancements:**
- Add rate limiting to prevent abuse
- Enable Cloud CDN for query caching
- Add request logging and monitoring
- Implement CORS headers if browser access needed

---

## Troubleshooting

### Issue: Deployment fails with "permission denied"

**Solution:**
```bash
# Ensure you have the necessary IAM roles
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="user:YOUR_EMAIL@example.com" \
    --role="roles/run.admin"
```

### Issue: Service returns 503 (Service Unavailable)

**Causes:**
- Container startup timeout
- Insufficient memory/CPU
- Health check failing

**Solution:**
```bash
# Check logs
gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --limit=100

# Increase resources
gcloud run services update ${SERVICE_NAME} \
    --region=${REGION} \
    --memory=4Gi \
    --cpu=4
```

### Issue: SPARQL queries timeout

**Solution:**
- Optimize query (add LIMIT clause, reduce complexity)
- Increase timeout: `--timeout=600` (10 minutes max)
- Consider adding indexes to TDB2 (already done in Dockerfile)

### Issue: Cold start latency is too high

**Solution:**
```bash
# Keep at least 1 instance warm
gcloud run services update ${SERVICE_NAME} \
    --region=${REGION} \
    --min-instances=1
```

**Trade-off:** Adds ~$10/month cost but eliminates cold starts.

---

## Architecture Alignment

This deployment follows the architecture defined in [ARCHITECTURE.md](../ARCHITECTURE.md):

- ✅ **Immutable deployments**: Data baked into container at build time
- ✅ **TDB2 storage**: High-performance indexed triple store
- ✅ **Read-only access**: Public SPARQL queries only
- ✅ **Auto-scaling**: 0-10 instances based on load
- ✅ **Serverless**: No infrastructure management required
- ✅ **Cost-effective**: Pay only for actual usage

---

## Related Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Complete system architecture
- [IMPLEMENTATION-PLAN.md](../IMPLEMENTATION-PLAN.md) - Implementation steps
- [BUILD.md](../BUILD.md) - Build instructions
- [CLAUDE.md](../CLAUDE.md) - Project standards and conventions

---

## Support

For deployment issues:
1. Check Cloud Run logs: `gcloud run services logs read ${SERVICE_NAME} --region=${REGION}`
2. Verify Docker image builds locally: `docker run -p 3030:3030 ${IMAGE}:latest`
3. Review Cloud Run metrics in GCP Console
4. Open an issue in the GitHub repository

---

**Last Updated:** 2025-12-15
**Service Name:** `national-curriculum-for-england-sparql`
**Current Deployment:** `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app`
