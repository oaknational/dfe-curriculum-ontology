# Security Setup Guide

This guide walks you through setting up secure authentication for the Fuseki SPARQL endpoint.

## Prerequisites

1. **Google Cloud Project Access:**
   - Project: `oak-ai-playground`
   - Required roles: Secret Manager Admin, Cloud Run Admin

2. **Enable Secret Manager API:**

   **Option A - Via Console (recommended if you don't have API enabling permissions):**
   - Visit: https://console.cloud.google.com/apis/library/secretmanager.googleapis.com?project=oak-ai-playground
   - Click "Enable"
   - Wait 2-3 minutes for propagation

   **Option B - Via gcloud (requires serviceusage.services.enable permission):**
   ```bash
   gcloud services enable secretmanager.googleapis.com --project=oak-ai-playground
   ```

## Setup Methods

### Method 1: Automated Setup (Recommended)

Once Secret Manager API is enabled:

```bash
# Generate secure passwords and create secrets
./deployment/setup-secrets.sh

# This will:
# - Generate cryptographically secure passwords
# - Create secrets in Google Secret Manager
# - Grant Cloud Run access to the secrets
# - Save credentials locally to .secrets/fuseki-credentials.txt
```

### Method 2: Manual Setup

If you prefer to set your own passwords or the script doesn't work:

#### Step 1: Create Secrets via Console

1. **Navigate to Secret Manager:**
   https://console.cloud.google.com/security/secret-manager?project=oak-ai-playground

2. **Create admin password secret:**
   - Click "Create Secret"
   - Name: `fuseki-admin-password`
   - Secret value: Your chosen admin password (24+ characters recommended)
   - Click "Create Secret"

3. **Create viewer password secret:**
   - Click "Create Secret"
   - Name: `fuseki-viewer-password`
   - Secret value: Your chosen viewer password (24+ characters recommended)
   - Click "Create Secret"

#### Step 2: Grant Cloud Run Access

For each secret, grant access to the Compute Engine default service account:

1. Click on the secret name
2. Click "Permissions" tab
3. Click "Grant Access"
4. Principal: `<project-number>-compute@developer.gserviceaccount.com`
   - Find your project number: https://console.cloud.google.com/home/dashboard?project=oak-ai-playground
5. Role: "Secret Manager Secret Accessor"
6. Click "Save"

#### Step 3: Save Credentials Locally

Create `.secrets/fuseki-credentials.txt` with your passwords for reference:

```bash
mkdir -p .secrets
cat > .secrets/fuseki-credentials.txt <<EOF
# Fuseki Credentials

Admin Username: admin
Admin Password: YOUR_ADMIN_PASSWORD_HERE

Viewer Username: viewer
Viewer Password: YOUR_VIEWER_PASSWORD_HERE

Service URL: https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app
EOF

chmod 600 .secrets/fuseki-credentials.txt
```

## Deploy

Once secrets are set up:

```bash
# Deploy with new secure configuration
./deployment/deploy.sh

# This will:
# - Verify secrets exist
# - Build Docker image with security scripts
# - Deploy to Cloud Run with secret references
# - Test authentication is working
```

## Verify Deployment

```bash
# Get passwords
ADMIN_PW=$(gcloud secrets versions access latest --secret="fuseki-admin-password" --project=oak-ai-playground)
VIEWER_PW=$(gcloud secrets versions access latest --secret="fuseki-viewer-password" --project=oak-ai-playground)

# Test viewer access
curl -u viewer:${VIEWER_PW} \
  -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/json" \
  --data "SELECT * WHERE { ?s ?p ?o } LIMIT 5" \
  "https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql"

# Test admin access
curl -u admin:${ADMIN_PW} \
  "https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/\$/stats"
```

## Troubleshooting

### Secret Manager API Not Enabled

```
ERROR: API [secretmanager.googleapis.com] not enabled
```

**Solution:** Enable the API via Console (see Prerequisites above), wait 2-3 minutes, then retry.

### Permission Denied Creating Secrets

```
ERROR: Permission denied to create secret
```

**Solution:** You need the "Secret Manager Admin" role. Ask a project owner to grant you this role:

```bash
gcloud projects add-iam-policy-binding oak-ai-playground \
  --member="user:your-email@domain.com" \
  --role="roles/secretmanager.admin"
```

### Secrets Not Found During Deployment

```
❌ Secret 'fuseki-admin-password' not found
```

**Solution:** Create the secrets first using Method 1 or Method 2 above.

### Authentication Not Working

If you can access the endpoint without credentials:

1. Check the deployment logs:
   ```bash
   gcloud run services logs read national-curriculum-for-england-sparql \
     --limit=100 \
     --project=oak-ai-playground \
     --region=europe-west1
   ```

2. Look for errors in shiro.ini generation:
   ```bash
   gcloud run services logs read national-curriculum-for-england-sparql \
     --limit=100 \
     --project=oak-ai-playground \
     --region=europe-west1 | grep -i "shiro\|password\|auth"
   ```

3. Verify secrets are accessible to Cloud Run:
   ```bash
   # Check if secrets exist
   gcloud secrets describe fuseki-admin-password --project=oak-ai-playground
   gcloud secrets describe fuseki-viewer-password --project=oak-ai-playground

   # Check permissions
   gcloud secrets get-iam-policy fuseki-admin-password --project=oak-ai-playground
   ```

## Password Rotation

To change passwords:

```bash
# Method 1: Automated (generates new random passwords)
./deployment/setup-secrets.sh

# Method 2: Manual
echo -n "NEW_ADMIN_PASSWORD" | gcloud secrets versions add fuseki-admin-password \
  --data-file=- \
  --project=oak-ai-playground

echo -n "NEW_VIEWER_PASSWORD" | gcloud secrets versions add fuseki-viewer-password \
  --data-file=- \
  --project=oak-ai-playground

# Redeploy to apply new passwords
./deployment/deploy.sh
```

## Next Steps

- Review [SECURITY.md](SECURITY.md) for security best practices
- Set up monitoring alerts (see SECURITY.md)
- Schedule regular password rotation (every 90 days recommended)
- Share viewer credentials securely with colleagues
