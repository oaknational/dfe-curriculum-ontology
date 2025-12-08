# deployment/Dockerfile

FROM stain/jena-fuseki:latest

# Metadata
LABEL maintainer="Oak National Academy"
LABEL description="UK Curriculum Ontology SPARQL Endpoint"

# Copy ontology data files
COPY ontology/*.ttl /fuseki-base/databases/uk-curriculum/

# Create Fuseki configuration
RUN mkdir -p /fuseki-base/configuration && \
    cat > /fuseki-base/configuration/uk-curriculum.ttl <<'EOF'
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ja: <http://jena.hpl.hp.com/2005/11/Assembler#> .

<#service> a fuseki:Service ;
    fuseki:name "uk-curriculum" ;
    fuseki:endpoint [ 
        fuseki:operation fuseki:query ; 
        fuseki:name "query" 
    ] ;
    fuseki:endpoint [ 
        fuseki:operation fuseki:query ; 
        fuseki:name "sparql" 
    ] ;
    fuseki:dataset <#dataset> .

<#dataset> a ja:RDFDataset ;
    ja:defaultGraph <#graph> .

<#graph> a ja:MemoryModel ;
    ja:content <file:///fuseki-base/databases/uk-curriculum/core.ttl> ;
    ja:content <file:///fuseki-base/databases/uk-curriculum/subjects.ttl> ;
    ja:content <file:///fuseki-base/databases/uk-curriculum/keystages.ttl> ;
    ja:content <file:///fuseki-base/databases/uk-curriculum/threads.ttl> .
EOF

# Expose Fuseki port
EXPOSE 3030

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3030/$/ping || exit 1

# Start Fuseki with configuration
CMD ["/jena-fuseki/fuseki-server", "--config=/fuseki-base/configuration/uk-curriculum.ttl"]