#!/bin/bash
set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-oak-national-academy}"
REGION="${GCP_REGION:-europe-west2}"
SERVICE_NAME="uk-curriculum-sparql"
IMAGE_NAME="gcr.io/${PROJECT_ID}/fuseki-uk-curriculum"

echo "🚀 Deploying UK Curriculum Fuseki to Google Cloud Run..."

# Validate TTL files locally
echo "📋 Validating TTL files..."
python3 scripts/validate.py || {
    echo "❌ Validation failed. Aborting deployment."
    exit 1
}

# Create deployment directory
echo "📦 Preparing deployment package..."
rm -rf deployment/build
mkdir -p deployment/build/data

# Copy TTL files
cp ontology/*.ttl deployment/build/data/

# Create Dockerfile
cat > deployment/build/Dockerfile <<'EOF'
FROM stain/jena-fuseki:latest

# Copy ontology data
COPY data/*.ttl /fuseki-base/databases/uk-curriculum/

# Create dataset configuration
RUN mkdir -p /fuseki-base/configuration
RUN echo '@prefix fuseki: <http://jena.apache.org/fuseki#> . \
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . \
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . \
@prefix ja: <http://jena.hpl.hp.com/2005/11/Assembler#> . \
\
<#service> a fuseki:Service ; \
    fuseki:name "uk-curriculum" ; \
    fuseki:endpoint [ fuseki:operation fuseki:query ; fuseki:name "query" ] ; \
    fuseki:endpoint [ fuseki:operation fuseki:query ; fuseki:name "sparql" ] ; \
    fuseki:dataset <#dataset> . \
\
<#dataset> a ja:RDFDataset ; \
    ja:defaultGraph <#graph> . \
\
<#graph> a ja:MemoryModel ; \
    ja:content <file:///fuseki-base/databases/uk-curriculum/core.ttl> ; \
    ja:content <file:///fuseki-base/databases/uk-curriculum/subjects.ttl> ; \
    ja:content <file:///fuseki-base/databases/uk-curriculum/keystages.ttl> .' \
    > /fuseki-base/configuration/uk-curriculum.ttl

# Expose port
EXPOSE 3030

# Start Fuseki with configuration
CMD ["/jena-fuseki/fuseki-server", "--config=/fuseki-base/configuration/uk-curriculum.ttl"]
EOF

# Build Docker image
echo "🔨 Building Docker image..."
cd deployment/build
docker build -t ${IMAGE_NAME}:latest .
cd ../..

# Authenticate with Google Cloud (if needed)
echo "🔐 Authenticating with Google Cloud..."
gcloud auth configure-docker --quiet

# Push image to Container Registry
echo "📤 Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 3030 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 300 \
    --project ${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --format 'value(status.url)')

echo "⏳ Waiting for service to be ready..."
sleep 15

# Test the endpoint
echo "🧪 Testing SPARQL endpoint..."
TEST_QUERY="SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/sparql-query" \
    -d "${TEST_QUERY}" \
    "${SERVICE_URL}/uk-curriculum/query" || echo "FAILED")

if [[ "$RESPONSE" == *"count"* ]]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🔗 SPARQL Endpoint: ${SERVICE_URL}/uk-curriculum/query"
    echo "🌐 Fuseki UI: ${SERVICE_URL}"
    echo ""
    echo "📝 Example query:"
    echo "curl -X POST -H \"Content-Type: application/sparql-query\" \\"
    echo "  -d \"SELECT * WHERE { ?s ?p ?o } LIMIT 10\" \\"
    echo "  \"${SERVICE_URL}/uk-curriculum/query\""
else
    echo "❌ Deployment verification failed. Response: ${RESPONSE}"
    exit 1
fi

# Clean up build directory
rm -rf deployment/build