# Release Process

## Versioning

We follow [Semantic Versioning](https://semver.org/):
- **Major (1.0.0)**: Breaking changes to ontology structure
- **Minor (0.1.0)**: New subjects, properties, or data (backward compatible)
- **Patch (0.0.1)**: Bug fixes, corrections (backward compatible)

Current version: **0.1.0**

## Creating a Release

### 1. Update Version

Update version in:
- `ontology/dfe-curriculum-ontology.ttl` (owl:versionInfo)
- `CHANGELOG.md`

### 2. Test Locally

```bash
# Validate data
./scripts/validate.sh

# Generate JSON
./scripts/build-static-data.sh

# Test Fuseki locally
docker build -t fuseki-test -f deployment/Dockerfile .
docker run -p 3030:3030 fuseki-test
# Test queries...
docker stop fuseki-test
```

### 3. Commit and Tag

```bash
git add .
git commit -m "chore: bump version to 0.1.0"
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin main
git push origin v0.1.0
```

### 4. Create GitHub Release

1. Go to: https://github.com/YOUR-ORG/uk-curriculum-ontology/releases/new
2. Select tag: v0.1.0
3. Title: "Version 0.1.0"
4. Description: Copy from CHANGELOG.md
5. Click "Publish release"

### 5. Automated Deployment

Creating a GitHub Release triggers:
- ✅ JSON generation workflow (generates distributions)
- ✅ Fuseki deployment workflow (deploys to Cloud Run)

### 6. Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe national-curriculum-for-england-sparql \
    --region=europe-west1 \
    --format='value(status.url)')

# Test SPARQL endpoint
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    ${SERVICE_URL}/national-curriculum-for-england/sparql

# Should return updated triple count
```

## Hotfix Process

For urgent fixes:

```bash
# Create hotfix branch
git checkout -b hotfix/0.1.1

# Make fixes
# Test thoroughly

# Commit and release
git commit -m "fix: urgent fix description"
git checkout main
git merge hotfix/0.1.1
git tag v0.1.1
git push origin main --tags
```

## Version History

See `CHANGELOG.md` for detailed version history and release notes.

## Release Checklist

Before creating a release, ensure:

- [ ] All tests pass (`./scripts/validate.sh`)
- [ ] JSON generation works (`./scripts/build-static-data.sh`)
- [ ] Local Fuseki deployment works (Docker build and test)
- [ ] Version updated in `ontology/dfe-curriculum-ontology.ttl`
- [ ] CHANGELOG.md updated with release notes
- [ ] Documentation updated if needed

## Manual Deployment (Alternative)

If GitHub Actions is not configured or you need to deploy manually:

```bash
# Use the deployment script
./deployment/deploy.sh

# Or follow the manual steps in deployment/DEPLOY.md
```

## Troubleshooting

### Release Tag Not Triggering Workflows

- Check that the tag follows the format `vX.Y.Z` (e.g., `v0.1.0`)
- Verify GitHub Actions workflows are configured in `.github/workflows/`
- Check GitHub Actions secrets are configured (see `deployment/GITHUB-ACTIONS-SETUP.md`)

### Deployment Fails

- Check Cloud Run service logs: `gcloud run services logs read national-curriculum-for-england-sparql --region=europe-west1`
- Verify Docker image built successfully in GCR
- Ensure service account has necessary permissions

### Version Mismatch

- Ensure `owl:versionInfo` in ontology matches the Git tag
- Check that `CHANGELOG.md` documents the same version
- Verify all version references are consistent across documentation
