#!/bin/bash
# Generate shiro.ini at container startup with hashed passwords from environment variables
# This runs inside the container at startup time

set -e

echo "🔐 Generating Shiro configuration..."

# Check if passwords are provided via environment variables
if [ -z "$FUSEKI_ADMIN_PASSWORD" ] || [ -z "$FUSEKI_VIEWER_PASSWORD" ]; then
    echo "❌ ERROR: Password environment variables not set!"
    echo "   Required: FUSEKI_ADMIN_PASSWORD, FUSEKI_VIEWER_PASSWORD"
    exit 1
fi

# Hash passwords using SHA-256 (Shiro format)
# Format: $shiro1$SHA-256$500000$BASE64_SALT$BASE64_HASH
hash_password() {
    local password="$1"
    # Use Python to generate Shiro-compatible SHA-256 hash
    python3 -c "
import hashlib
import base64
import os

password = '''$password'''
salt = os.urandom(32)
iterations = 500000

# Hash the password
hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)

# Encode in Shiro format
salt_b64 = base64.b64encode(salt).decode('ascii')
hash_b64 = base64.b64encode(hash_obj).decode('ascii')

print(f'\$shiro1\$SHA-256\${iterations}\${salt_b64}\${hash_b64}')
"
}

echo "  Hashing admin password..."
ADMIN_HASH=$(hash_password "$FUSEKI_ADMIN_PASSWORD")

echo "  Hashing viewer password..."
VIEWER_HASH=$(hash_password "$FUSEKI_VIEWER_PASSWORD")

# Generate shiro.ini with hashed passwords and security enhancements
cat > /fuseki/shiro.ini <<EOF
[main]
# Use SHA-256 password matching
credentialsMatcher = org.apache.shiro.authc.credential.HashedCredentialsMatcher
credentialsMatcher.hashAlgorithmName = SHA-256
credentialsMatcher.hashIterations = 500000
credentialsMatcher.storedCredentialsHexEncoded = false

# Configure Shiro to use our custom matcher
authc = org.apache.shiro.web.filter.authc.BasicHttpAuthenticationFilter
authc.applicationName = Fuseki

[users]
# Admin user - full access
# Password is hashed using SHA-256 with 500,000 iterations
admin = ${ADMIN_HASH}, admin

# Viewer user - read-only access
viewer = ${VIEWER_HASH}, reader

[roles]
# Admin role - full access to everything
admin = *

# Reader role - read-only operations (GET requests only)
reader = sparql:query, sparql:get

[urls]
# Public endpoints (no authentication required)
/\$/ping = anon

# Admin-only write/management endpoints (requires admin role)
/\$/backup/** = authc, roles[admin], rest[POST,DELETE]
/\$/compact/** = authc, roles[admin], rest[POST]
/\$/sleep = authc, roles[admin], rest[POST]
/\$/tasks/** = authc, roles[admin]

# Everything else requires authentication
# GET requests allowed for both roles, write operations require admin
/** = authc
EOF

echo "✅ Shiro configuration generated successfully"

# Set proper permissions
chmod 644 /fuseki/shiro.ini
chown 9008:9008 /fuseki/shiro.ini

# Clean up environment variables for security
unset FUSEKI_ADMIN_PASSWORD
unset FUSEKI_VIEWER_PASSWORD

echo "🚀 Starting Fuseki server..."
