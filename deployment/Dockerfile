# Use official Jena Fuseki image
# Note: Using latest stable release (5.1.0 as of Dec 2024)
FROM stain/jena-fuseki:latest

# Metadata
LABEL maintainer="Department for Education"
LABEL description="UK Curriculum Ontology SPARQL Endpoint"
LABEL version="0.1.0"

# Create staging directory for data files (use /tmp for write permissions)
RUN mkdir -p /tmp/staging

# Copy ontology files
COPY ontology/dfe-curriculum-ontology.ttl /tmp/staging/
COPY ontology/dfe-curriculum-constraints.ttl /tmp/staging/

# Copy programme structure
COPY data/national-curriculum-for-england/programme-structure.ttl /tmp/staging/

# Copy themes
COPY data/national-curriculum-for-england/themes.ttl /tmp/staging/

# Copy all subject data
COPY data/national-curriculum-for-england/subjects/ /tmp/staging/subjects/

# Load all data into TDB2 database (at build time)
# Note: versions/ subdirectories excluded via .dockerignore
# Note: Using /data instead of /fuseki-base because /fuseki is a VOLUME
USER root
RUN mkdir -p /data/national-curriculum-for-england-tdb2 /fuseki-base/configuration && \
    java -cp /jena-fuseki/fuseki-server.jar tdb2.tdbloader \
    --verbose \
    --loc=/data/national-curriculum-for-england-tdb2 \
    /tmp/staging/*.ttl \
    /tmp/staging/subjects/*/*.ttl && \
    echo "Loaded $(find /tmp/staging -name '*.ttl' | wc -l) TTL files into TDB2" && \
    echo "Database files:" && ls -lh /data/national-curriculum-for-england-tdb2/Data-0001/ | head -10

# Copy Fuseki configuration (as root to ensure it's copied)
COPY deployment/fuseki-config.ttl /fuseki-base/configuration/config.ttl

# Fix permissions for fuseki user
RUN chown -R 9008:9008 /data/national-curriculum-for-england-tdb2 /fuseki-base/configuration /fuseki

# Switch back to fuseki user
USER 9008

# Expose Fuseki port
EXPOSE 3030

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3030/$/ping || exit 1

# Start Fuseki with our configuration
CMD ["/jena-fuseki/fuseki-server", "--config=/fuseki-base/configuration/config.ttl"]
