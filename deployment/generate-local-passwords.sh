#!/bin/bash
# Generate passwords locally and create shiro.ini with hashed passwords
# This is a fallback method when Secret Manager is not available

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}🔐 Local Password Generation${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is required but not found${NC}"
    exit 1
fi

echo -e "${BLUE}🔑 Step 1: Generating secure passwords...${NC}"

# Generate secure random passwords
ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-24)
VIEWER_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-24)

echo -e "${GREEN}✅ Passwords generated${NC}"
echo ""

# Hash passwords using Python
echo -e "${BLUE}🔒 Step 2: Hashing passwords...${NC}"

hash_password() {
    local password="$1"
    python3 -c "
import hashlib
import base64
import os

password = '''$password'''
salt = os.urandom(32)
iterations = 500000

# Hash the password using PBKDF2
hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)

# Encode in Shiro format
salt_b64 = base64.b64encode(salt).decode('ascii')
hash_b64 = base64.b64encode(hash_obj).decode('ascii')

print(f'\$shiro1\$SHA-256\${iterations}\${salt_b64}\${hash_b64}')
"
}

ADMIN_HASH=$(hash_password "$ADMIN_PASSWORD")
VIEWER_HASH=$(hash_password "$VIEWER_PASSWORD")

echo -e "${GREEN}✅ Passwords hashed with SHA-256 (500,000 iterations)${NC}"
echo ""

# Create shiro.ini with hashed passwords
echo -e "${BLUE}📝 Step 3: Creating shiro.ini with hashed passwords...${NC}"

cat > deployment/shiro.ini <<EOF
[main]

[users]
# Admin user - full access
# Password is hashed using SHA-256 with 500,000 iterations
# Shiro auto-detects the \$shiro1\$ format
admin = ${ADMIN_HASH}, admin

# Viewer user - read-only access
viewer = ${VIEWER_HASH}, reader

[roles]
# Admin role - full access to everything
admin = *

# Reader role - read-only operations
reader = sparql:query, sparql:get

[urls]
# Public endpoints (no authentication required)
/\$/ping = anon

# Admin-only write/management endpoints (requires admin role)
/\$/backup/** = authcBasic, roles[admin]
/\$/compact/** = authcBasic, roles[admin]
/\$/sleep = authcBasic, roles[admin]
/\$/tasks/** = authcBasic, roles[admin]

# Everything else requires authentication
/** = authcBasic
EOF

echo -e "${GREEN}✅ shiro.ini created with hashed passwords${NC}"
echo ""

# Save plaintext passwords to local file (gitignored)
echo -e "${BLUE}💾 Step 4: Saving credentials to local file...${NC}"

mkdir -p .secrets
cat > .secrets/fuseki-credentials.txt <<EOF
# Fuseki Credentials - Generated $(date)
# DO NOT COMMIT THIS FILE TO GIT
# This file is automatically gitignored

Admin Username: admin
Admin Password: ${ADMIN_PASSWORD}

Viewer Username: viewer
Viewer Password: ${VIEWER_PASSWORD}

Service URL: https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app

# NOTE: Passwords are hashed in deployment/shiro.ini
# Plaintext passwords only stored in this local file
# Keep this file secure!
EOF

chmod 600 .secrets/fuseki-credentials.txt

echo -e "${GREEN}✅ Credentials saved to .secrets/fuseki-credentials.txt${NC}"
echo ""

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ Password Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. View your credentials: cat .secrets/fuseki-credentials.txt"
echo "2. Deploy to Cloud Run: ./deployment/deploy-without-secrets.sh"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  - deployment/shiro.ini now contains hashed passwords (safe to commit)"
echo "  - .secrets/fuseki-credentials.txt contains plaintext passwords (DO NOT COMMIT)"
echo "  - To rotate passwords, run this script again and redeploy"
echo ""
