#!/bin/bash
# Container entrypoint - generates Shiro config and starts Fuseki
set -e

# Generate Shiro configuration from secrets
/docker-entrypoint-scripts/generate-shiro-config.sh

# Start Fuseki server with our configuration
exec /jena-fuseki/fuseki-server --config=/fuseki-base/configuration/config.ttl
