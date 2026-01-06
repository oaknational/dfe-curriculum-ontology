#!/bin/bash
# Setup Google Secret Manager secrets for Fuseki authentication
# Usage: ./deployment/setup-secrets.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}🔐 Setting up Secret Manager${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-oak-ai-playground}"
REGION="${GCP_REGION:-europe-west1}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo ""

# Enable Secret Manager API if not already enabled
echo -e "${BLUE}📋 Step 1: Enabling Secret Manager API...${NC}"
gcloud services enable secretmanager.googleapis.com --project=${PROJECT_ID} || {
    echo -e "${YELLOW}⚠️  Secret Manager API already enabled${NC}"
}
echo -e "${GREEN}✅ Secret Manager API ready${NC}"
echo ""

# Generate secure passwords
echo -e "${BLUE}🔑 Step 2: Generating secure passwords...${NC}"
ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-24)
VIEWER_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-24)
echo -e "${GREEN}✅ Passwords generated${NC}"
echo ""

# Create or update admin password secret
echo -e "${BLUE}🔒 Step 3: Creating/updating admin password secret...${NC}"
if gcloud secrets describe fuseki-admin-password --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Secret already exists, adding new version...${NC}"
    echo -n "${ADMIN_PASSWORD}" | gcloud secrets versions add fuseki-admin-password \
        --data-file=- \
        --project=${PROJECT_ID}
else
    echo -n "${ADMIN_PASSWORD}" | gcloud secrets create fuseki-admin-password \
        --data-file=- \
        --replication-policy="automatic" \
        --project=${PROJECT_ID}
fi
echo -e "${GREEN}✅ Admin password secret created${NC}"
echo ""

# Create or update viewer password secret
echo -e "${BLUE}🔒 Step 4: Creating/updating viewer password secret...${NC}"
if gcloud secrets describe fuseki-viewer-password --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Secret already exists, adding new version...${NC}"
    echo -n "${VIEWER_PASSWORD}" | gcloud secrets versions add fuseki-viewer-password \
        --data-file=- \
        --project=${PROJECT_ID}
else
    echo -n "${VIEWER_PASSWORD}" | gcloud secrets create fuseki-viewer-password \
        --data-file=- \
        --replication-policy="automatic" \
        --project=${PROJECT_ID}
fi
echo -e "${GREEN}✅ Viewer password secret created${NC}"
echo ""

# Grant Cloud Run service account access to secrets
echo -e "${BLUE}👤 Step 5: Granting Cloud Run access to secrets...${NC}"
COMPUTE_SA="${PROJECT_ID}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding fuseki-admin-password \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=${PROJECT_ID} >/dev/null 2>&1 || true

gcloud secrets add-iam-policy-binding fuseki-viewer-password \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=${PROJECT_ID} >/dev/null 2>&1 || true

echo -e "${GREEN}✅ Permissions granted${NC}"
echo ""

# Save credentials to local file (gitignored)
echo -e "${BLUE}💾 Step 6: Saving credentials locally...${NC}"
mkdir -p .secrets
cat > .secrets/fuseki-credentials.txt <<EOF
# Fuseki Credentials - Generated $(date)
# DO NOT COMMIT THIS FILE TO GIT

Admin Username: admin
Admin Password: ${ADMIN_PASSWORD}

Viewer Username: viewer
Viewer Password: ${VIEWER_PASSWORD}

Service URL: https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app

# To retrieve passwords later:
# gcloud secrets versions access latest --secret="fuseki-admin-password" --project=${PROJECT_ID}
# gcloud secrets versions access latest --secret="fuseki-viewer-password" --project=${PROJECT_ID}
EOF

chmod 600 .secrets/fuseki-credentials.txt
echo -e "${GREEN}✅ Credentials saved to .secrets/fuseki-credentials.txt${NC}"
echo ""

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ Secrets Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. View credentials: cat .secrets/fuseki-credentials.txt"
echo "2. Deploy with new secrets: ./deployment/deploy.sh"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Keep .secrets/fuseki-credentials.txt secure and private!${NC}"
echo ""
