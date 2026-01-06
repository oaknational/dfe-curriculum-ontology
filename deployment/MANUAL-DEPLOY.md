# Manual Deployment (Without Secret Manager)

This guide is for deploying when you don't have access to Google Secret Manager API.

## Overview

This method:
- ✅ Generates cryptographically secure passwords locally
- ✅ Hashes passwords using SHA-256 with 500,000 iterations (industry standard)
- ✅ Stores plaintext passwords in a local gitignored file
- ✅ Stores hashed passwords in shiro.ini (safe to commit)
- ✅ No passwords in environment variables or logs
- ❌ No automatic password rotation (requires manual steps)

## Security Level

**Good for:** Internal/prototype deployments, development environments

**Consider upgrading to Secret Manager for:** Production systems with sensitive data, compliance requirements

## Deployment Steps

### Step 1: Generate Passwords and Hashed shiro.ini

```bash
./deployment/generate-local-passwords.sh
```

This will:
- Generate two secure random passwords (24 characters each)
- Hash them using SHA-256 with 500,000 iterations
- Create `deployment/shiro.ini` with hashed passwords
- Save plaintext passwords to `.secrets/fuseki-credentials.txt` (gitignored)

**Output:**
```
🔐 Local Password Generation
========================================

🔑 Step 1: Generating secure passwords...
✅ Passwords generated

🔒 Step 2: Hashing passwords...
✅ Passwords hashed with SHA-256 (500,000 iterations)

📝 Step 3: Creating shiro.ini with hashed passwords...
✅ shiro.ini created with hashed passwords

💾 Step 4: Saving credentials to local file...
✅ Credentials saved to .secrets/fuseki-credentials.txt
```

### Step 2: View Your Credentials

```bash
cat .secrets/fuseki-credentials.txt
```

**Example output:**
```
Admin Username: admin
Admin Password: xK9mPq2nR4sT7vW8yZ3aC5bD

Viewer Username: viewer
Viewer Password: fG6hJ8kL0mN2pQ4rS6tV9wX1
```

**Save these passwords securely** - they're only stored in this local file!

### Step 3: Validate Data

```bash
./scripts/validate.sh
```

Ensures your TTL files are valid before deploying.

### Step 4: Deploy to Cloud Run

```bash
./deployment/deploy-without-secrets.sh
```

This will:
1. Validate TTL files
2. Build Docker image with hashed passwords baked in
3. Push to Google Container Registry
4. Deploy to Cloud Run
5. Test authentication

**Deployment takes ~5-10 minutes**

### Step 5: Test Your Deployment

```bash
# Get your viewer password
VIEWER_PW=$(grep "Viewer Password:" .secrets/fuseki-credentials.txt | cut -d':' -f2 | xargs)

# Test a query
curl -u viewer:${VIEWER_PW} \
  -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/json" \
  --data "SELECT * WHERE { ?s ?p ?o } LIMIT 5" \
  "https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql"
```

## Sharing Credentials with Colleagues

### For Viewer Access (Read-Only)

Share these details securely (e.g., via password manager, encrypted email):

```
URL: https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app
Username: viewer
Password: [from .secrets/fuseki-credentials.txt]
```

**What they can do:**
- Query the SPARQL endpoint
- View datasets and statistics
- Use the Fuseki web UI

**What they cannot do:**
- Modify data
- Access admin endpoints (backup, compact, etc.)
- Change configuration

### For Admin Access

Only share admin credentials with infrastructure administrators:

```
Username: admin
Password: [from .secrets/fuseki-credentials.txt]
```

## Password Rotation

To change passwords:

```bash
# 1. Generate new passwords
./deployment/generate-local-passwords.sh

# 2. Redeploy with new passwords
./deployment/deploy-without-secrets.sh

# 3. Share new credentials with colleagues
cat .secrets/fuseki-credentials.txt
```

**Recommended:** Rotate passwords every 90 days.

## File Structure

After running `generate-local-passwords.sh`:

```
deployment/
├── shiro.ini                    # Hashed passwords (SAFE to commit)
├── generate-local-passwords.sh  # Password generation script
├── deploy-without-secrets.sh    # Deployment script
├── Dockerfile.no-secrets        # Simplified Dockerfile
└── MANUAL-DEPLOY.md            # This file

.secrets/                        # Gitignored directory
└── fuseki-credentials.txt       # Plaintext passwords (DO NOT COMMIT)
```

## What Gets Committed to Git?

✅ **Safe to commit:**
- `deployment/shiro.ini` - Contains only hashed passwords
- `deployment/generate-local-passwords.sh` - Script
- `deployment/deploy-without-secrets.sh` - Script
- `deployment/Dockerfile.no-secrets` - Dockerfile

❌ **Never commit:**
- `.secrets/fuseki-credentials.txt` - Contains plaintext passwords
- `.secrets/` directory - Automatically gitignored

## Troubleshooting

### "shiro.ini not found" error

```bash
./deployment/generate-local-passwords.sh
```

### "shiro.ini contains plaintext passwords" error

The old shiro.ini has plaintext passwords. Regenerate it:

```bash
./deployment/generate-local-passwords.sh
```

### Authentication not working after deployment

1. Check deployment logs:
```bash
gcloud run services logs read national-curriculum-for-england-sparql \
  --limit=50 \
  --project=oak-ai-playground \
  --region=europe-west1
```

2. Verify shiro.ini was copied into container:
```bash
gcloud run services logs read national-curriculum-for-england-sparql \
  --limit=200 \
  --project=oak-ai-playground \
  --region=europe-west1 | grep -i shiro
```

3. Test with correct password from `.secrets/fuseki-credentials.txt`

### Lost your passwords

If you lost `.secrets/fuseki-credentials.txt`:

**Option 1:** Regenerate everything
```bash
./deployment/generate-local-passwords.sh
./deployment/deploy-without-secrets.sh
```

**Option 2:** Keep existing passwords
Unfortunately, you can't recover hashed passwords. You'll need to regenerate and redeploy.

## Comparison: Manual vs Secret Manager

| Feature | Manual Method | Secret Manager |
|---------|---------------|----------------|
| **Setup Complexity** | Easy | Requires API & permissions |
| **Password Storage** | Local file (gitignored) | Google Cloud (encrypted) |
| **Password Hashing** | Yes ✅ | Yes ✅ |
| **Rotation Process** | Run script + redeploy | Script updates secrets + redeploy |
| **Audit Trail** | Manual | Automatic (who accessed when) |
| **Cost** | Free | ~$0.06/month per secret |
| **Access Control** | File system | IAM policies |
| **Best For** | Dev/staging | Production |

## Migrating to Secret Manager Later

When you get Secret Manager API access:

```bash
# 1. Enable Secret Manager API (via console or admin)
# 2. Run the Secret Manager setup
./deployment/setup-secrets.sh

# 3. Deploy with Secret Manager
./deployment/deploy.sh

# 4. (Optional) Delete local credentials
rm .secrets/fuseki-credentials.txt
```

The Secret Manager method provides:
- Centralized password management
- Automatic rotation support
- Audit logging of secret access
- IAM-based access control
- No local password files to manage

## Security Best Practices

Even without Secret Manager, follow these practices:

✅ **DO:**
- Keep `.secrets/fuseki-credentials.txt` secure
- Rotate passwords every 90 days
- Use viewer account for applications
- Monitor Cloud Run logs
- Share passwords via secure channels
- Back up `.secrets/fuseki-credentials.txt` to secure location

❌ **DON'T:**
- Commit `.secrets/` directory to git
- Share passwords via email or Slack
- Use the same passwords in multiple environments
- Give everyone admin access
- Forget to rotate passwords

## Getting Help

- **Security documentation:** See `deployment/SECURITY.md`
- **Full setup guide:** See `deployment/SETUP.md`
- **Validation issues:** Check `scripts/validate.sh` output
- **Deployment issues:** Check Cloud Run logs
