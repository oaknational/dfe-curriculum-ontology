#!/bin/bash
# Deploy National Curriculum for England SPARQL endpoint to Google Cloud Run
# WITHOUT Secret Manager (fallback method)
# Usage: ./deployment/deploy-without-secrets.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}🚀 Deploying National Curriculum SPARQL${NC}"
echo -e "${BLUE}   (Without Secret Manager)${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-oak-ai-playground}"
REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="national-curriculum-for-england-sparql"
IMAGE="gcr.io/${PROJECT_ID}/national-curriculum-for-england-fuseki"

echo -e "${BLUE}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo "  Image: $IMAGE:latest"
echo ""

# Check if shiro.ini exists
if [ ! -f "deployment/shiro.ini" ]; then
    echo -e "${RED}❌ deployment/shiro.ini not found${NC}"
    echo -e "${YELLOW}Run: ./deployment/generate-local-passwords.sh${NC}"
    exit 1
fi

# Check if shiro.ini contains hashed passwords (not plaintext)
if grep -q "admin = fuseki-admin-" deployment/shiro.ini 2>/dev/null; then
    echo -e "${RED}❌ shiro.ini contains plaintext passwords${NC}"
    echo -e "${YELLOW}Run: ./deployment/generate-local-passwords.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ shiro.ini found with hashed passwords${NC}"
echo ""

# Step 1: Validate TTL files
echo -e "${BLUE}📋 Step 1: Validating TTL files...${NC}"
if [ -f "scripts/validate.sh" ]; then
    ./scripts/validate.sh || {
        echo -e "${RED}❌ Validation failed. Aborting deployment.${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Validation passed${NC}"
else
    echo -e "${YELLOW}⚠️  Validation script not found, skipping...${NC}"
fi
echo ""

# Step 2: Build Docker image (using simplified Dockerfile)
echo -e "${BLUE}🔨 Step 2: Building Docker image...${NC}"
docker build -t ${IMAGE}:latest -f deployment/Dockerfile.no-secrets . || {
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Docker image built successfully${NC}"
echo ""

# Step 3: Configure Docker for GCR
echo -e "${BLUE}🔐 Step 3: Configuring Docker authentication...${NC}"
gcloud auth configure-docker --quiet || {
    echo -e "${RED}❌ Docker authentication failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Docker authenticated${NC}"
echo ""

# Step 4: Push to Google Container Registry
echo -e "${BLUE}📤 Step 4: Pushing image to GCR...${NC}"
docker push ${IMAGE}:latest || {
    echo -e "${RED}❌ Docker push failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Image pushed to GCR${NC}"
echo ""

# Step 5: Deploy to Cloud Run (without secrets)
echo -e "${BLUE}☁️  Step 5: Deploying to Cloud Run...${NC}"
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
    --concurrency=80 \
    --project=${PROJECT_ID} || {
    echo -e "${RED}❌ Cloud Run deployment failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Deployed to Cloud Run${NC}"
echo ""

# Step 6: Get service URL
echo -e "${BLUE}🔗 Step 6: Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format='value(status.url)' 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}❌ Failed to get service URL${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Service URL retrieved${NC}"
echo ""

# Step 7: Wait for service to be ready
echo -e "${BLUE}⏳ Step 7: Waiting for service to be ready...${NC}"
sleep 15
echo -e "${GREEN}✅ Service should be ready${NC}"
echo ""

# Step 8: Test deployment
echo -e "${BLUE}🧪 Step 8: Testing SPARQL endpoint...${NC}"

# Test 1: Health check
echo -n "  Testing health endpoint... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${SERVICE_URL}/\$/ping)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Failed (HTTP $HTTP_CODE)${NC}"
    exit 1
fi

# Test 2: Check if credentials are in local file
if [ -f ".secrets/fuseki-credentials.txt" ]; then
    echo -n "  Testing SPARQL query with credentials... "

    # Extract passwords from credentials file
    VIEWER_PASSWORD=$(grep "Viewer Password:" .secrets/fuseki-credentials.txt | cut -d':' -f2 | xargs)

    TRIPLE_COUNT=$(curl -u viewer:${VIEWER_PASSWORD} -s -X POST \
        -H "Content-Type: application/sparql-query" \
        -H "Accept: application/json" \
        --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
        ${SERVICE_URL}/national-curriculum-for-england/sparql | \
        jq -r '.results.bindings[0].count.value' 2>/dev/null)

    if [ "$TRIPLE_COUNT" -gt "0" ]; then
        echo -e "${GREEN}✅ OK (${TRIPLE_COUNT} triples)${NC}"
    else
        echo -e "${RED}❌ Failed (no triples returned)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Cannot test authentication (.secrets/fuseki-credentials.txt not found)${NC}"
    echo -e "${YELLOW}   You'll need to test manually with your credentials${NC}"
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ Deployment Successful!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}Service Details:${NC}"
echo "  Name: ${SERVICE_NAME}"
echo "  Region: ${REGION}"
echo "  URL: ${SERVICE_URL}"
echo ""
echo -e "${BLUE}SPARQL Endpoint:${NC}"
echo "  ${SERVICE_URL}/national-curriculum-for-england/sparql"
echo ""
echo -e "${BLUE}Health Check:${NC}"
echo "  ${SERVICE_URL}/\$/ping"
echo ""

if [ -f ".secrets/fuseki-credentials.txt" ]; then
    echo -e "${BLUE}Credentials:${NC}"
    echo "  View: cat .secrets/fuseki-credentials.txt"
    echo ""
fi

echo -e "${BLUE}Example Query:${NC}"
echo "  curl -u viewer:YOUR_PASSWORD \\"
echo "    -X POST \\"
echo "    -H \"Content-Type: application/sparql-query\" \\"
echo "    -H \"Accept: application/json\" \\"
echo "    --data \"SELECT * WHERE { ?s ?p ?o } LIMIT 10\" \\"
echo "    \"${SERVICE_URL}/national-curriculum-for-england/sparql\""
echo ""
echo -e "${BLUE}View Logs:${NC}"
echo "  gcloud run services logs read ${SERVICE_NAME} --region=${REGION}"
echo ""
echo -e "${BLUE}View Metrics:${NC}"
echo "  https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
echo ""
echo -e "${YELLOW}⚠️  Security Note:${NC}"
echo "  Passwords are hashed in the container (secure)"
echo "  To rotate: run ./deployment/generate-local-passwords.sh and redeploy"
echo ""
