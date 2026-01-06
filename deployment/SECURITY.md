# Security Configuration

This document describes the security measures implemented for the National Curriculum SPARQL endpoint.

## Authentication & Authorization

### Password Management

**Passwords are stored in Google Secret Manager** (not in code or environment variables):
- `fuseki-admin-password` - Admin user password
- `fuseki-viewer-password` - Viewer user password

**Password hashing:**
- Passwords are hashed using SHA-256 with 500,000 iterations (PBKDF2)
- Hashing occurs at container startup via `/docker-entrypoint-scripts/generate-shiro-config.sh`
- Plaintext passwords are never stored in the container after startup

**Password rotation:**
```bash
# Update passwords
./deployment/setup-secrets.sh

# Redeploy to pick up new passwords
./deployment/deploy.sh
```

### User Roles

**Admin** (`admin` user):
- Full access to all endpoints
- Can perform backup, compact, and server management operations
- Should only be used by infrastructure administrators

**Viewer** (`viewer` user):
- Read-only access to SPARQL queries
- Can view datasets, stats, and server info
- Cannot perform write operations or admin functions
- Suitable for sharing with colleagues and applications

### Retrieving Credentials

```bash
# Get admin password
gcloud secrets versions access latest --secret="fuseki-admin-password" --project=oak-ai-playground

# Get viewer password
gcloud secrets versions access latest --secret="fuseki-viewer-password" --project=oak-ai-playground

# Or view saved credentials (if setup-secrets.sh was run locally)
cat .secrets/fuseki-credentials.txt
```

## Audit Logging

### Cloud Run Request Logs

All HTTP requests are automatically logged by Cloud Run, including:
- Timestamp
- HTTP method and path
- Response status code
- Response time
- Client IP address
- User agent
- Request size

**View logs:**
```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=national-curriculum-for-england-sparql" \
  --limit=50 \
  --project=oak-ai-playground

# View logs in Cloud Console
https://console.cloud.google.com/logs/query?project=oak-ai-playground
```

### SPARQL Query Logging

Fuseki logs all SPARQL queries to stdout, which are captured by Cloud Run:
- Query text
- Execution time
- Result count

**Filter for SPARQL queries:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~'SPARQL'" \
  --limit=50 \
  --project=oak-ai-playground
```

### Log Retention

- **Cloud Run logs:** 30 days by default
- **Custom retention:** Configure in Cloud Logging settings
- **Export to BigQuery:** For long-term analysis and compliance

## Rate Limiting

### Cloud Run Built-in Protections

**Container limits** (configured in `deploy.sh`):
- Max instances: 10 (prevents runaway scaling costs)
- Max concurrency: 80 requests per container
- CPU: 2 vCPUs per container
- Memory: 2GB per container
- Timeout: 300 seconds (5 minutes)

**Automatic throttling:**
- Cloud Run automatically throttles requests when limits are reached
- Returns HTTP 503 (Service Unavailable) when max instances is reached
- Returns HTTP 429 (Too Many Requests) when concurrency limit is exceeded

### Advanced Rate Limiting (Optional)

For more granular rate limiting, consider:

**Option 1: Cloud Armor (Recommended for production)**
```bash
# Requires setting up Cloud Load Balancer
# Provides per-IP rate limiting, geographic restrictions, and DDoS protection
```

**Option 2: API Gateway**
```bash
# Provides per-API-key rate limiting and quota management
# Good for providing different limits to different consumers
```

**Option 3: Reverse Proxy**
```bash
# Add nginx or Envoy in front of Fuseki
# Provides custom rate limiting rules
```

### Monitoring Rate Limit Events

```bash
# View throttling events
gcloud logging read "resource.type=cloud_run_revision AND httpRequest.status>=429" \
  --limit=50 \
  --project=oak-ai-playground
```

## HTTP Method Restrictions

The Shiro configuration enforces read-only access for the viewer role:
- **Viewer role:** Only GET and POST (for SPARQL queries) allowed
- **Admin role:** All HTTP methods allowed
- **Write endpoints:** Require admin role (backup, compact, etc.)

## Network Security

### Cloud Run Security Features

**HTTPS only:**
- All traffic is automatically encrypted with TLS 1.2+
- HTTP is automatically redirected to HTTPS
- Managed SSL certificates (automatic renewal)

**Authentication at edge:**
- HTTP Basic Auth enforced by Fuseki before any processing
- Invalid credentials rejected immediately
- No access to data without valid credentials

### Allowunauthenticated Setting

The service uses `--allow-unauthenticated` for Cloud Run IAM, but:
- This only means "no GCP IAM required"
- Fuseki's HTTP Basic Auth still required
- All requests still need username/password

To add an additional GCP IAM layer:
```bash
# Remove unauthenticated access
gcloud run services remove-iam-policy-binding national-curriculum-for-england-sparql \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=europe-west1 \
  --project=oak-ai-playground

# Grant access to specific service accounts
gcloud run services add-iam-policy-binding national-curriculum-for-england-sparql \
  --member="serviceAccount:your-app@project.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=europe-west1 \
  --project=oak-ai-playground
```

## Security Best Practices

### DO:
- ✅ Rotate passwords regularly (every 90 days)
- ✅ Use the viewer account for read-only applications
- ✅ Monitor audit logs for suspicious activity
- ✅ Keep credentials in Secret Manager (never in code)
- ✅ Use HTTPS for all requests
- ✅ Review access logs monthly

### DON'T:
- ❌ Commit passwords to git
- ❌ Share admin credentials widely
- ❌ Hardcode credentials in applications
- ❌ Use HTTP (always use HTTPS)
- ❌ Share passwords via unencrypted channels (email, Slack)
- ❌ Reuse passwords from other systems

## Incident Response

### Suspected Credential Compromise

If you suspect credentials have been compromised:

```bash
# 1. Rotate passwords immediately
./deployment/setup-secrets.sh

# 2. Redeploy with new passwords
./deployment/deploy.sh

# 3. Review audit logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=national-curriculum-for-england-sparql" \
  --format="table(timestamp,httpRequest.requestMethod,httpRequest.requestUrl,httpRequest.status,httpRequest.remoteIp)" \
  --limit=1000 \
  --project=oak-ai-playground

# 4. Look for suspicious activity:
# - Unusual IP addresses
# - High request volumes
# - Failed authentication attempts
# - Access to admin endpoints from viewer account
```

### Attack Patterns to Monitor

- **Brute force:** Multiple failed auth attempts from same IP
- **Data exfiltration:** Large volume of queries from single source
- **Unauthorized admin access:** Attempts to access /$/backup, /$/compact
- **Geographic anomalies:** Access from unexpected countries

## Compliance

### Data Protection

- **Data in transit:** TLS 1.2+ encryption (automatic)
- **Data at rest:** Container filesystem encrypted (GCP default)
- **Secrets:** Encrypted at rest in Secret Manager (GCP default)

### Audit Requirements

All audit logs contain:
- Who (authenticated user)
- What (HTTP method, path, query)
- When (timestamp with millisecond precision)
- Where (source IP, user agent)
- Outcome (status code, response time)

Logs can be exported to BigQuery for compliance reporting.

## Further Hardening (Future Improvements)

### Short-term:
1. Add IP allowlisting (if internal use only)
2. Implement Cloud Armor with rate limiting
3. Add monitoring alerts for suspicious patterns
4. Enable VPC Service Controls (if highly sensitive)

### Medium-term:
1. Implement API Gateway with API keys
2. Add application-level rate limiting per user
3. Implement query complexity analysis
4. Add Web Application Firewall (WAF) rules

### Long-term:
1. Implement OAuth 2.0 / OpenID Connect
2. Add fine-grained authorization (row-level security)
3. Implement query result caching
4. Add intrusion detection system (IDS)

## Contact

For security concerns or to report vulnerabilities, contact the DfE infrastructure team.
