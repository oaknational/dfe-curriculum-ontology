# GitHub Actions Setup - Admin Required

## Current Status

⚠️ **GitHub Actions automated deployment is NOT YET CONFIGURED** due to IAM permissions.

Manual deployment works perfectly (see `DEPLOY.md`). Automated deployment requires a GCP admin to create the service account.

## What's Needed

To enable automated deployment via GitHub Actions (`.github/workflows/deploy-fuseki.yml`), a GCP admin needs to:

### 1. Create Service Account

```bash
export PROJECT_ID="oak-ai-playground"

# Create service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions" \
    --description="Service account for GitHub Actions CI/CD pipeline"
```

### 2. Grant Required Roles

```bash
# Cloud Run Admin (to deploy services)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Storage Admin (to push Docker images to GCR)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Service Account User (to act as service accounts)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

### 3. Create Service Account Key

```bash
# Create key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Display key (to copy to GitHub)
cat github-actions-key.json
```

### 4. Provide to Repository Owner

Send the repository owner:
1. The JSON key file contents (securely - e.g., via encrypted email or password manager)
2. Confirmation that the service account has all 3 roles

### 5. Clean Up

```bash
# After providing the key, delete the local copy
rm github-actions-key.json
```

## Adding Secrets to GitHub

Once you have the service account key from your GCP admin:

1. Go to: https://github.com/oak-national/uk-curriculum-ontology/settings/secrets/actions
2. Add `GCP_SA_KEY`: Paste the entire JSON key file contents
3. Add `GCP_PROJECT_ID`: `oak-ai-playground`
4. Test by triggering: https://github.com/oak-national/uk-curriculum-ontology/actions/workflows/deploy-fuseki.yml

## Alternative: Workload Identity Federation

For better security (no keys), consider Workload Identity Federation. This also requires GCP admin to set up.

See: https://github.com/google-github-actions/auth#setup

## Current Deployment Method

Until GitHub Actions is configured, use manual deployment:

```bash
# From project root
./deployment/deploy.sh
```

See `deployment/DEPLOY.md` for full manual deployment guide.

## Security Notes

- Service account keys are sensitive credentials
- Never commit keys to git
- Store keys only in GitHub Secrets or secure credential managers
- Rotate keys periodically (every 90 days recommended)
- Consider Workload Identity Federation to eliminate keys entirely
