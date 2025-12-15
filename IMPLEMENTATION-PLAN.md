# UK Curriculum Ontology - Implementation Plan

**Date:** 2025-12-15
**Approach:** Ignore generated files (Approach 1)
**Goal:** Set up complete data pipeline + Fuseki on Google Cloud Run

---

## Overview

This plan breaks down the implementation into **28 testable steps** across 7 phases:

1. **Phase 1:** Local Setup & Validation (Steps 1-4) ✅ **COMPLETED**
2. **Phase 2:** SPARQL Query Development (Steps 5-8) ✅ **COMPLETED**
3. **Phase 3:** JSON Generation (Steps 9-12) ✅ **COMPLETED**
4. **Phase 4:** Fuseki Local Testing (Steps 13-16) ⚠️ **PARTIALLY COMPLETE**
5. **Phase 5:** Google Cloud Setup (Steps 17-20)
6. **Phase 6:** CI/CD Pipeline (Steps 21-24) ⚠️ **PARTIALLY COMPLETE**
7. **Phase 7:** Documentation & Distribution (Steps 25-28)

**Each step:**
- ✅ Is self-contained and testable
- ✅ Can be committed separately
- ✅ Builds on previous steps
- ✅ Includes clear success criteria

---

## Completion Status

**✅ Completed Steps:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 21, 23
**🔄 Next Step:** Step 15 - Build and Test Fuseki Locally
**📍 Current Phase:** Phase 4 - Fuseki Local Testing

---

## Phase 1: Local Setup & Validation ✅ **COMPLETED**

### Step 1: Install Prerequisites ✅ **COMPLETED**

**Goal:** Install all required tools for local development

**Actions:**
```bash
# 1. Install Apache Jena (includes riot, arq, tdbloader)
# macOS:
brew install jena

# Linux (Ubuntu/Debian):
wget https://dlcdn.apache.org/jena/binaries/apache-jena-4.10.0.tar.gz
tar xzf apache-jena-4.10.0.tar.gz
sudo mv apache-jena-4.10.0 /opt/jena
echo 'export PATH=$PATH:/opt/jena/bin' >> ~/.bashrc
source ~/.bashrc

# 2. Install Docker
# macOS:
brew install docker

# Linux:
# Follow: https://docs.docker.com/engine/install/

# 3. Install Google Cloud SDK (for later)
# macOS:
brew install google-cloud-sdk

# Linux:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Test:**
```bash
# Verify installations
riot --version          # Should show: Apache Jena, version 4.x
arq --version          # Should show: Apache Jena, version 4.x
docker --version       # Should show: Docker version 24.x
gcloud --version       # Should show: Google Cloud SDK 4xx.x
```

**Success Criteria:**
- ✅ All commands return version numbers
- ✅ No error messages

**Commit:** Not needed (local setup only)

---

### Step 2: Set Up Project Structure ✅ **COMPLETED**

**Goal:** Create necessary directories and .gitignore

**Actions:**
```bash
cd /Users/markhodierne/projects/oak/uk-curriculum-ontology

# Create directories
mkdir -p queries
mkdir -p distributions/subjects
mkdir -p distributions/keystages
mkdir -p distributions/themes
mkdir -p scripts
mkdir -p deployment

# Create .gitignore for generated files
cat >> .gitignore <<'EOF'

# Generated JSON files (Approach 1: ignore generated files)
distributions/

# Build artifacts
*.log
.DS_Store

# Local testing
.env.local
fuseki-data/
EOF
```

**Test:**
```bash
# Verify directory structure
ls -la queries
ls -la distributions
ls -la scripts
ls -la deployment

# Verify .gitignore
cat .gitignore | grep "distributions/"
```

**Success Criteria:**
- ✅ All directories exist
- ✅ .gitignore includes distributions/
- ✅ `git status` does not show distributions/ folder

**Commit:**
```bash
git add .gitignore
git commit -m "chore: set up project structure and gitignore"
```

---

### Step 3: Create Validation Script ✅ **COMPLETED** (Enhanced with SHACL validation)

**Goal:** Create script to validate all TTL files

**Actions:**
```bash
# Create scripts/validate.sh
cat > scripts/validate.sh <<'EOF'
#!/bin/bash
# Validate all Turtle files for syntax and SHACL constraints

set -e

echo "======================================"
echo "🔍 Validating UK Curriculum Ontology"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for files
TOTAL_FILES=0
VALID_FILES=0

echo "📋 Step 1: Validating Turtle syntax..."
echo ""

# Validate ontology files
for file in ontology/*.ttl; do
    if [ -f "$file" ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        echo -n "  Checking $(basename $file)... "
        if riot --validate "$file" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            VALID_FILES=$((VALID_FILES + 1))
        else
            echo -e "${RED}✗${NC}"
            echo -e "${RED}Error in $file${NC}"
            riot --validate "$file"
            exit 1
        fi
    fi
done

# Validate data files
for file in data/**/*.ttl; do
    if [ -f "$file" ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        echo -n "  Checking $(basename $file)... "
        if riot --validate "$file" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            VALID_FILES=$((VALID_FILES + 1))
        else
            echo -e "${RED}✗${NC}"
            echo -e "${RED}Error in $file${NC}"
            riot --validate "$file"
            exit 1
        fi
    fi
done

echo ""
echo -e "${GREEN}✅ All $VALID_FILES files have valid Turtle syntax${NC}"
echo ""

# TODO: Add SHACL validation in future step
# echo "📋 Step 2: Validating SHACL constraints..."
# shacl validate --shapes=ontology/dfe-curriculum-constraints.ttl ...

echo "======================================"
echo -e "${GREEN}✅ Validation Complete!${NC}"
echo "======================================"
EOF

# Make executable
chmod +x scripts/validate.sh
```

**Test:**
```bash
# Run validation
./scripts/validate.sh
```

**Success Criteria:**
- ✅ Script runs without errors
- ✅ All existing TTL files pass validation
- ✅ Green checkmarks for each file
- ✅ Final success message appears

**Commit:**
```bash
git add scripts/validate.sh
git commit -m "feat: add TTL validation script"
```

---

### Step 4: Test Validation with Intentional Error ✅ **COMPLETED**

**Goal:** Verify validation script catches errors

**Actions:**
```bash
# Create a temporary invalid file
cat > /tmp/test-invalid.ttl <<'EOF'
@prefix test: <http://example.org/> .

test:broken
    test:missing "value"
    # Missing period at end - SYNTAX ERROR
EOF

# Test that validation fails
riot --validate /tmp/test-invalid.ttl
# Should show error message
```

**Test:**
```bash
# Should fail with error
riot --validate /tmp/test-invalid.ttl

# Clean up
rm /tmp/test-invalid.ttl
```

**Success Criteria:**
- ✅ Validation correctly identifies syntax error
- ✅ Clear error message is displayed
- ✅ We understand how to debug TTL files

**Commit:** Not needed (testing only)

---

## Phase 2: SPARQL Query Development ✅ **COMPLETED**

### Step 5: Test Local SPARQL Queries ✅ **COMPLETED**

**Goal:** Verify we can query TTL files directly with arq

**Actions:**
```bash
# Create simple test query
cat > /tmp/test-query.sparql <<'EOF'
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT (COUNT(*) as ?count) WHERE {
  ?s ?p ?o
}
EOF

# Test query against your ontology
arq --data=ontology/dfe-curriculum-ontology.ttl \
    --query=/tmp/test-query.sparql
```

**Test:**
```bash
# Should show count of triples
arq --data=ontology/dfe-curriculum-ontology.ttl \
    --query=/tmp/test-query.sparql

# Clean up
rm /tmp/test-query.sparql
```

**Success Criteria:**
- ✅ Query executes successfully
- ✅ Returns count of triples (e.g., 200-300)
- ✅ No error messages

**Commit:** Not needed (testing only)

---

### Step 6: Create Subject Index Query ✅ **COMPLETED**

**Goal:** Create query to list all subjects

**Actions:**
```bash
cat > queries/subjects-index.sparql <<'EOF'
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?subjectId ?label ?definition
WHERE {
  ?subject a curric:Subject ;
           skos:prefLabel ?label .

  OPTIONAL {
    ?subject skos:definition ?definition .
  }

  BIND(STRAFTER(STR(?subject), "england/") AS ?subjectId)
}
ORDER BY ?label
EOF
```

**Test:**
```bash
# Test query
arq --data=ontology/dfe-curriculum-ontology.ttl \
    --data=data/national-curriculum-for-england/subjects/science/science-subject.ttl \
    --data=data/national-curriculum-for-england/subjects/history/history-subject.ttl \
    --query=queries/subjects-index.sparql

# Test with JSON output
arq --data=ontology/dfe-curriculum-ontology.ttl \
    --data=data/national-curriculum-for-england/subjects/science/science-subject.ttl \
    --data=data/national-curriculum-for-england/subjects/history/history-subject.ttl \
    --query=queries/subjects-index.sparql \
    --results=JSON
```

**Success Criteria:**
- ✅ Query returns Science and History subjects
- ✅ Each subject has label and definition
- ✅ JSON output is well-formed

**Commit:**
```bash
git add queries/subjects-index.sparql
git commit -m "feat: add subjects index SPARQL query"
```

---

### Step 7: Create Science KS3 Query ✅ **COMPLETED**

**Goal:** Create query to extract all Science KS3 content

**Actions:**
```bash
cat > queries/science-ks3.sparql <<'EOF'
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?contentId ?label ?definition ?strandLabel ?type
WHERE {
  # Find Science KS3 scheme
  ?scheme a curric:Scheme ;
          curric:hasSubject eng:science ;
          curric:hasKeyStage eng:key-stage-3 ;
          curric:hasContent ?content .

  # Get content details
  ?content a ?type ;
           skos:prefLabel ?label .

  OPTIONAL {
    ?content skos:definition ?definition .
  }

  # Get strand (if content descriptor is in a strand)
  OPTIONAL {
    ?strand curric:hasContentDescriptor ?content ;
            skos:prefLabel ?strandLabel .
  }

  BIND(STRAFTER(STR(?content), "england/") AS ?contentId)

  # Filter to only content types (not structural classes)
  FILTER(?type IN (curric:ContentDescriptor, curric:ContentSubDescriptor))
}
ORDER BY ?strandLabel ?label
EOF
```

**Test:**
```bash
# Test query with all Science data
arq --data=ontology/dfe-curriculum-ontology.ttl \
    --data=data/national-curriculum-for-england/programme-structure.ttl \
    --data=data/national-curriculum-for-england/subjects/science/science-subject.ttl \
    --data=data/national-curriculum-for-england/subjects/science/science-knowledge-taxonomy.ttl \
    --data=data/national-curriculum-for-england/subjects/science/science-schemes.ttl \
    --query=queries/science-ks3.sparql \
    --results=JSON | head -50
```

**Success Criteria:**
- ✅ Query returns Science KS3 content descriptors
- ✅ Content is organized by strand
- ✅ JSON output is well-formed
- ✅ Can see labels and definitions

**Commit:**
```bash
git add queries/science-ks3.sparql
git commit -m "feat: add Science KS3 SPARQL query"
```

---

### Step 8: Create Full Curriculum Query ✅ **COMPLETED**

**Goal:** Create query to export entire curriculum for client-side search

**Actions:**
```bash
cat > queries/full-curriculum.sparql <<'EOF'
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT
  ?contentId
  ?label
  ?definition
  ?subjectId
  ?subjectLabel
  (GROUP_CONCAT(DISTINCT ?keyStageId; separator=",") AS ?keyStages)
  ?strandLabel
  ?type
WHERE {
  # Get all content
  ?content a ?type ;
           skos:prefLabel ?label .

  OPTIONAL {
    ?content skos:definition ?definition .
  }

  # Get subject
  ?scheme curric:hasContent ?content ;
          curric:hasSubject ?subject .
  ?subject skos:prefLabel ?subjectLabel .

  # Get key stage(s)
  OPTIONAL {
    ?scheme curric:hasKeyStage ?keyStage .
    BIND(STRAFTER(STR(?keyStage), "england/") AS ?keyStageId)
  }

  # Get strand
  OPTIONAL {
    ?strand curric:hasContentDescriptor ?content ;
            skos:prefLabel ?strandLabel .
  }

  BIND(STRAFTER(STR(?content), "england/") AS ?contentId)
  BIND(STRAFTER(STR(?subject), "england/") AS ?subjectId)

  # Filter to content types only
  FILTER(?type IN (curric:ContentDescriptor, curric:ContentSubDescriptor))
}
GROUP BY ?contentId ?label ?definition ?subjectId ?subjectLabel ?strandLabel ?type
ORDER BY ?subjectLabel ?keyStages ?strandLabel ?label
EOF
```

**Test:**
```bash
# Test with all data
arq --data=ontology/dfe-curriculum-ontology.ttl \
    --data=data/national-curriculum-for-england/programme-structure.ttl \
    --data=data/national-curriculum-for-england/subjects/**/*.ttl \
    --query=queries/full-curriculum.sparql \
    --results=JSON > /tmp/full-curriculum-test.json

# Check output
cat /tmp/full-curriculum-test.json | head -100

# Check size
ls -lh /tmp/full-curriculum-test.json

# Clean up
rm /tmp/full-curriculum-test.json
```

**Success Criteria:**
- ✅ Query returns all content from all subjects
- ✅ Each item includes subject, key stages, strand
- ✅ JSON file is reasonable size (< 1MB)
- ✅ Data is searchable (has labels and definitions)

**Commit:**
```bash
git add queries/full-curriculum.sparql
git commit -m "feat: add full curriculum export SPARQL query"
```

---

## Phase 3: JSON Generation ✅ **COMPLETED**

### Step 9: Create JSON Generation Script ✅ **COMPLETED**

**Goal:** Create script to generate all JSON files

**Actions:**
```bash
cat > scripts/build-static-data.sh <<'EOF'
#!/bin/bash
# Generate static JSON files from RDF data

set -e

echo "=========================================="
echo "🏗️  Building Static JSON API"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Output directory
OUTPUT_DIR="distributions"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/subjects" "$OUTPUT_DIR/keystages" "$OUTPUT_DIR/themes"

# Build common data file list
echo -e "${BLUE}📦 Collecting data files...${NC}"
DATA_FILES=""
DATA_FILES="$DATA_FILES --data=ontology/dfe-curriculum-ontology.ttl"
DATA_FILES="$DATA_FILES --data=data/national-curriculum-for-england/programme-structure.ttl"

# Check if themes file exists
if [ -f "data/national-curriculum-for-england/themes.ttl" ]; then
    DATA_FILES="$DATA_FILES --data=data/national-curriculum-for-england/themes.ttl"
fi

# Add all subject files
for file in data/national-curriculum-for-england/subjects/**/*.ttl; do
    if [ -f "$file" ]; then
        DATA_FILES="$DATA_FILES --data=$file"
    fi
done

echo -e "${GREEN}✓${NC} Data files collected"
echo ""

# Generate subjects index
echo -e "${BLUE}📋 Generating subjects index...${NC}"
arq $DATA_FILES \
    --query=queries/subjects-index.sparql \
    --results=JSON > "$OUTPUT_DIR/subjects/index.json"
echo -e "${GREEN}✓${NC} subjects/index.json"

# Generate Science KS3
echo -e "${BLUE}🔬 Generating Science KS3...${NC}"
arq $DATA_FILES \
    --query=queries/science-ks3.sparql \
    --results=JSON > "$OUTPUT_DIR/subjects/science-ks3.json"
echo -e "${GREEN}✓${NC} subjects/science-ks3.json"

# Generate full curriculum
echo -e "${BLUE}🌍 Generating full curriculum dataset...${NC}"
arq $DATA_FILES \
    --query=queries/full-curriculum.sparql \
    --results=JSON > "$OUTPUT_DIR/curriculum-full.json"
echo -e "${GREEN}✓${NC} curriculum-full.json"

# Calculate statistics
echo ""
echo "=========================================="
TOTAL_FILES=$(find "$OUTPUT_DIR" -name "*.json" | wc -l | tr -d ' ')
TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)
echo -e "${GREEN}✅ Generated $TOTAL_FILES JSON files ($TOTAL_SIZE)${NC}"
echo "=========================================="
echo ""

# List files
echo "Generated files:"
find "$OUTPUT_DIR" -name "*.json" -exec echo "  - {}" \;
echo ""
EOF

# Make executable
chmod +x scripts/build-static-data.sh
```

**Test:**
```bash
# Run the script
./scripts/build-static-data.sh
```

**Success Criteria:**
- ✅ Script runs without errors
- ✅ Creates distributions/ directory
- ✅ Generates JSON files
- ✅ Shows summary statistics
- ✅ distributions/ is gitignored (not shown in git status)

**Commit:**
```bash
git add scripts/build-static-data.sh
git commit -m "feat: add JSON generation script"
```

---

### Step 10: Verify JSON Output ✅ **COMPLETED**

**Goal:** Inspect and validate generated JSON files

**Actions:**
```bash
# Run generation if not already done
./scripts/build-static-data.sh

# Check directory structure
tree distributions/

# Inspect subjects index
cat distributions/subjects/index.json | jq .

# Inspect Science KS3
cat distributions/subjects/science-ks3.json | jq '.results.bindings | length'
cat distributions/subjects/science-ks3.json | jq '.results.bindings[0]'

# Check full curriculum size
ls -lh distributions/curriculum-full.json
cat distributions/curriculum-full.json | jq '.results.bindings | length'

# Verify JSON is valid
for file in distributions/**/*.json; do
    echo "Validating $file..."
    jq empty "$file" && echo "  ✓ Valid JSON"
done
```

**Test:**
```bash
# Check that files exist
ls distributions/subjects/index.json
ls distributions/subjects/science-ks3.json
ls distributions/curriculum-full.json

# Verify not tracked by git
git status | grep distributions
# Should return nothing (gitignored)
```

**Success Criteria:**
- ✅ All JSON files are valid
- ✅ Contains expected data (subjects, content)
- ✅ File sizes are reasonable
- ✅ distributions/ is not tracked by git

**Commit:** Not needed (generated files are gitignored)

---

### Step 11: Test JSON Generation in CI Environment ✅ **COMPLETED**

**Goal:** Ensure script works in clean environment (simulating CI)

**Actions:**
```bash
# Simulate CI environment (fresh clone)
cd /tmp
git clone /Users/markhodierne/projects/oak/uk-curriculum-ontology test-build
cd test-build

# Install Jena (if needed)
# brew install jena  # or appropriate install for your OS

# Run build
./scripts/build-static-data.sh

# Verify output
ls -la distributions/

# Clean up
cd /Users/markhodierne/projects/oak/uk-curriculum-ontology
rm -rf /tmp/test-build
```

**Success Criteria:**
- ✅ Script works on fresh clone
- ✅ No dependency on local files outside repo
- ✅ Generates same output as local

**Commit:** Not needed (testing only)

---

### Step 12: Document Build Process ✅ **COMPLETED**

**Goal:** Update README with build instructions

**Actions:**
```bash
# Add build section to README (manual edit needed)
# Or create separate BUILD.md
cat > BUILD.md <<'EOF'
# Build Instructions

## Prerequisites

- Apache Jena 4.10.0+ (includes `arq`, `riot`, `tdbloader`)
- jq (for JSON validation)

## Building Static JSON Files

Generate static JSON API files from RDF data:

```bash
./scripts/build-static-data.sh
```

**Output:**
- `distributions/subjects/index.json` - List of all subjects
- `distributions/subjects/science-ks3.json` - Science KS3 content
- `distributions/curriculum-full.json` - Complete curriculum (for search)

**Note:** Generated files are gitignored and published via GitHub Releases.

## Validation

Validate all Turtle files:

```bash
./scripts/validate.sh
```

## SPARQL Queries

All queries are in `queries/*.sparql` and can be run manually:

```bash
arq --data=ontology/*.ttl \
    --data=data/**/*.ttl \
    --query=queries/science-ks3.sparql \
    --results=JSON
```
EOF
```

**Success Criteria:**
- ✅ BUILD.md exists with clear instructions
- ✅ Anyone can follow steps to generate JSON

**Commit:**
```bash
git add BUILD.md
git commit -m "docs: add build instructions"
```

---

## Phase 4: Fuseki Local Testing

### Step 13: Create Fuseki Configuration ✅ **COMPLETED**

**Goal:** Create Fuseki assembler configuration

**Actions:**
```bash
cat > deployment/fuseki-config.ttl <<'EOF'
@prefix fuseki:  <http://jena.apache.org/fuseki#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ja:      <http://jena.hpl.hp.com/2005/11/Assembler#> .
@prefix tdb2:    <http://jena.apache.org/2016/tdb#> .

## ---------------------------------------------------------------
## UK Curriculum Ontology - Fuseki Service Configuration
## ---------------------------------------------------------------

<#service> a fuseki:Service ;
    fuseki:name "uk-curriculum" ;

    # SPARQL Query endpoint (read-only)
    fuseki:endpoint [
        fuseki:operation fuseki:query ;
        fuseki:name "sparql"
    ] ;
    fuseki:endpoint [
        fuseki:operation fuseki:query ;
        fuseki:name "query"
    ] ;

    # Graph Store Protocol - read-only
    fuseki:endpoint [
        fuseki:operation fuseki:gsp-r ;
        fuseki:name "get"
    ] ;

    fuseki:dataset <#dataset> .

## ---------------------------------------------------------------
## Dataset Configuration
## Uses TDB2 for persistence and performance
## ---------------------------------------------------------------

<#dataset> a tdb2:DatasetTDB2 ;
    tdb2:location "/fuseki-base/databases/uk-curriculum-tdb2" ;
    tdb2:unionDefaultGraph true .

## Note: Data is loaded at container build time via tdb2.tdbloader
## This provides:
## - Faster startup (pre-loaded data)
## - Immutable deployments (data baked into container)
## - Better performance (TDB2 vs in-memory)
EOF
```

**Test:**
```bash
# Validate TTL syntax
riot --validate deployment/fuseki-config.ttl

# Check file
cat deployment/fuseki-config.ttl
```

**Success Criteria:**
- ✅ Configuration file is valid Turtle
- ✅ Defines uk-curriculum service
- ✅ Uses TDB2 for storage

**Commit:**
```bash
git add deployment/fuseki-config.ttl
git commit -m "feat: add Fuseki configuration"
```

---

### Step 14: Create Dockerfile ✅ **COMPLETED**

**Goal:** Create Docker image that loads all curriculum data

**Actions:**
```bash
cat > deployment/Dockerfile <<'EOF'
# Use official Jena Fuseki image
FROM stain/jena-fuseki:4.10.0

# Metadata
LABEL maintainer="Department for Education"
LABEL description="UK Curriculum Ontology SPARQL Endpoint"
LABEL version="0.1.0"

# Create staging directory for data files
RUN mkdir -p /staging

# Copy ontology files
COPY ontology/dfe-curriculum-ontology.ttl /staging/
COPY ontology/dfe-curriculum-constraints.ttl /staging/

# Copy programme structure
COPY data/national-curriculum-for-england/programme-structure.ttl /staging/

# Copy themes (if exists)
COPY data/national-curriculum-for-england/themes.ttl /staging/ 2>/dev/null || true

# Copy all subject data
COPY data/national-curriculum-for-england/subjects/ /staging/subjects/

# Load all data into TDB2 database (at build time)
RUN mkdir -p /fuseki-base/databases && \
    /jena-fuseki/tdb2.tdbloader \
    --loc=/fuseki-base/databases/uk-curriculum-tdb2 \
    /staging/*.ttl \
    /staging/subjects/**/*.ttl && \
    echo "Loaded $(find /staging -name '*.ttl' | wc -l) TTL files into TDB2"

# Copy Fuseki configuration
COPY deployment/fuseki-config.ttl /fuseki-base/configuration/config.ttl

# Expose Fuseki port
EXPOSE 3030

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3030/$/ping || exit 1

# Start Fuseki with our configuration
CMD ["/jena-fuseki/fuseki-server", "--config=/fuseki-base/configuration/config.ttl"]
EOF
```

**Test:**
```bash
# Validate Dockerfile syntax
docker build --no-cache --progress=plain -f deployment/Dockerfile -t test-fuseki . --dry-run 2>&1 || true

# Check file
cat deployment/Dockerfile
```

**Success Criteria:**
- ✅ Dockerfile exists
- ✅ Contains all copy commands for data
- ✅ Uses tdb2.tdbloader to load data
- ✅ Includes health check

**Commit:**
```bash
git add deployment/Dockerfile
git commit -m "feat: add Fuseki Dockerfile"
```

---

### Step 15: Build and Test Fuseki Locally

**Goal:** Build Docker image and run Fuseki locally

**Actions:**
```bash
# Build Docker image
echo "Building Fuseki Docker image..."
docker build -t uk-curriculum-fuseki:local -f deployment/Dockerfile .

# Should see output like:
# - Copying files
# - Loading TTL files into TDB2
# - "Loaded X TTL files into TDB2"

# Run container
echo "Starting Fuseki container..."
docker run -d \
    --name fuseki-test \
    -p 3030:3030 \
    uk-curriculum-fuseki:local

# Wait for startup
echo "Waiting for Fuseki to start..."
sleep 10

# Check logs
docker logs fuseki-test
```

**Test:**
```bash
# Test health endpoint
curl http://localhost:3030/$/ping
# Should return: empty response with 200 OK

# Test SPARQL endpoint exists
curl http://localhost:3030/uk-curriculum/sparql
# Should return: SPARQL endpoint info or HTML page

# Open in browser
echo "Visit: http://localhost:3030"
echo "Dataset: uk-curriculum"
```

**Success Criteria:**
- ✅ Docker image builds successfully
- ✅ Container starts without errors
- ✅ Health check endpoint responds
- ✅ SPARQL endpoint is accessible
- ✅ Can access Fuseki UI at localhost:3030

**Commit:** Not needed (local testing)

---

### Step 16: Test SPARQL Queries Against Local Fuseki

**Goal:** Verify all queries work against Fuseki

**Actions:**
```bash
# Test 1: Count triples
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    http://localhost:3030/uk-curriculum/sparql | jq .

# Test 2: List subjects
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "$(cat queries/subjects-index.sparql)" \
    http://localhost:3030/uk-curriculum/sparql | jq .

# Test 3: Get Science KS3
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "$(cat queries/science-ks3.sparql)" \
    http://localhost:3030/uk-curriculum/sparql | jq '.results.bindings | length'

# Test 4: Full curriculum query
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "$(cat queries/full-curriculum.sparql)" \
    http://localhost:3030/uk-curriculum/sparql | jq '.results.bindings | length'
```

**Test:**
```bash
# All queries should return valid JSON
# Count should match expected number of triples/results

# Stop container when done
docker stop fuseki-test
docker rm fuseki-test
```

**Success Criteria:**
- ✅ All queries return valid JSON
- ✅ Data is present (not empty results)
- ✅ Query performance is reasonable (< 1 second)
- ✅ No errors in container logs

**Commit:** Not needed (testing only)

---

## Phase 5: Google Cloud Setup

### Step 17: Set Up Google Cloud Project

**Goal:** Create and configure GCP project for Cloud Run

**Actions:**
```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. List projects (or create new one)
gcloud projects list

# 3. Set project (replace with your project ID)
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# 4. Enable required APIs
echo "Enabling Cloud Run API..."
gcloud services enable run.googleapis.com

echo "Enabling Container Registry API..."
gcloud services enable containerregistry.googleapis.com

echo "Enabling Cloud Build API..."
gcloud services enable cloudbuild.googleapis.com

# 5. Set region
export REGION="europe-west2"
gcloud config set run/region $REGION

# 6. Verify setup
gcloud config list
```

**Test:**
```bash
# Verify APIs are enabled
gcloud services list --enabled | grep -E "(run|container|build)"

# Should show:
# - run.googleapis.com
# - containerregistry.googleapis.com
# - cloudbuild.googleapis.com
```

**Success Criteria:**
- ✅ GCP project is selected
- ✅ All required APIs are enabled
- ✅ Region is set to europe-west2
- ✅ No authentication errors

**Commit:** Not needed (cloud config only)

---

### Step 18: Configure Docker for GCR

**Goal:** Set up Docker to push to Google Container Registry

**Actions:**
```bash
# Configure Docker authentication for GCR
gcloud auth configure-docker

# This adds credentials to ~/.docker/config.json
# and allows pushing to gcr.io

# Verify configuration
cat ~/.docker/config.json | grep gcr.io
```

**Test:**
```bash
# Test docker credentials
docker info | grep -A 10 "Registry"

# Should include gcr.io in authenticated registries
```

**Success Criteria:**
- ✅ Docker is configured for GCR
- ✅ No authentication errors
- ✅ Ready to push images

**Commit:** Not needed (local Docker config)

---

### Step 19: Manual Deployment Test

**Goal:** Deploy Fuseki to Cloud Run manually (first time)

**Actions:**
```bash
# Set variables
export PROJECT_ID=$(gcloud config get-value project)
export REGION="europe-west2"
export SERVICE_NAME="uk-curriculum-sparql"
export IMAGE="gcr.io/${PROJECT_ID}/fuseki-uk-curriculum"

echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Image: $IMAGE"

# 1. Build image with tag
echo "Building Docker image..."
docker build -t ${IMAGE}:latest -f deployment/Dockerfile .

# 2. Push to GCR
echo "Pushing to Google Container Registry..."
docker push ${IMAGE}:latest

# 3. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE}:latest \
    --platform=managed \
    --region=${REGION} \
    --allow-unauthenticated \
    --port=3030 \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --min-instances=0 \
    --timeout=300 \
    --concurrency=80

# 4. Get service URL
echo ""
echo "Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)')

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo "Service URL: ${SERVICE_URL}"
echo "SPARQL Endpoint: ${SERVICE_URL}/uk-curriculum/sparql"
echo "=========================================="

# Save URL for testing
echo $SERVICE_URL > /tmp/fuseki-url.txt
```

**Test:**
```bash
# Load service URL
SERVICE_URL=$(cat /tmp/fuseki-url.txt)

# Test health endpoint
curl ${SERVICE_URL}/$/ping
# Should return: 200 OK

# Test SPARQL endpoint
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    ${SERVICE_URL}/uk-curriculum/sparql | jq .

# Should return count of triples

echo "✅ Cloud Run deployment is working!"
```

**Success Criteria:**
- ✅ Image builds successfully
- ✅ Image pushes to GCR
- ✅ Service deploys to Cloud Run
- ✅ Service URL is accessible
- ✅ SPARQL queries work
- ✅ No errors in Cloud Run logs

**Commit:** Not needed (deployment test)

---

### Step 20: Document Deployment

**Goal:** Create deployment guide

**Actions:**
```bash
cat > deployment/DEPLOY.md <<'EOF'
# Deployment Guide

## Prerequisites

- Google Cloud SDK installed and configured
- Docker installed
- GCP project with billing enabled
- Required APIs enabled (see Step 17)

## Manual Deployment

```bash
# 1. Set variables
export PROJECT_ID="your-gcp-project-id"
export REGION="europe-west2"
export SERVICE_NAME="uk-curriculum-sparql"
export IMAGE="gcr.io/${PROJECT_ID}/fuseki-uk-curriculum"

# 2. Build Docker image
docker build -t ${IMAGE}:latest -f deployment/Dockerfile .

# 3. Push to Google Container Registry
gcloud auth configure-docker
docker push ${IMAGE}:latest

# 4. Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE}:latest \
    --platform=managed \
    --region=${REGION} \
    --allow-unauthenticated \
    --port=3030 \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --timeout=300

# 5. Get service URL
gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)'
```

## Testing Deployment

```bash
# Test SPARQL endpoint
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} --format='value(status.url)')

curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    ${SERVICE_URL}/uk-curriculum/sparql
```

## Costs

Estimated monthly cost: $10-30 depending on usage
- Scales to zero when idle
- Pay only for request duration

## Monitoring

View logs:
```bash
gcloud run services logs read ${SERVICE_NAME} \
    --region=${REGION} \
    --limit=50
```

View metrics:
```bash
# Visit Cloud Console
echo "https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
```
EOF
```

**Success Criteria:**
- ✅ Deployment guide exists
- ✅ Clear step-by-step instructions
- ✅ Includes testing procedures

**Commit:**
```bash
git add deployment/DEPLOY.md
git commit -m "docs: add deployment guide"
```

---

## Phase 6: CI/CD Pipeline

### Step 21: Create Validation Workflow ✅ **COMPLETED** (Enhanced with SHACL)

**Goal:** Automate validation on every push

**Actions:**
```bash
mkdir -p .github/workflows

cat > .github/workflows/validate.yml <<'EOF'
name: Validate Curriculum Data

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install Apache Jena
        run: |
          wget -q https://dlcdn.apache.org/jena/binaries/apache-jena-4.10.0.tar.gz
          tar xzf apache-jena-4.10.0.tar.gz
          echo "$PWD/apache-jena-4.10.0/bin" >> $GITHUB_PATH

      - name: Verify Jena installation
        run: |
          riot --version
          arq --version

      - name: Validate Turtle files
        run: ./scripts/validate.sh

      - name: Report success
        run: echo "✅ All curriculum data is valid!"
EOF
```

**Test:**
```bash
# Commit and push to test
git add .github/workflows/validate.yml
git commit -m "ci: add validation workflow"
git push origin main

# Check GitHub Actions tab in browser
# Should see workflow run and succeed
```

**Success Criteria:**
- ✅ Workflow file is valid YAML
- ✅ Workflow triggers on push
- ✅ Validation runs successfully
- ✅ Green checkmark on GitHub

**Commit:** Already committed in test step

---

### Step 22: Create JSON Generation Workflow

**Goal:** Generate JSON files and publish as artifacts

**Actions:**
```bash
cat > .github/workflows/generate-json.yml <<'EOF'
name: Generate Static JSON Files

on:
  push:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install Apache Jena
        run: |
          wget -q https://dlcdn.apache.org/jena/binaries/apache-jena-4.10.0.tar.gz
          tar xzf apache-jena-4.10.0.tar.gz
          echo "$PWD/apache-jena-4.10.0/bin" >> $GITHUB_PATH

      - name: Install jq (for JSON validation)
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Generate JSON files
        run: ./scripts/build-static-data.sh

      - name: Validate JSON output
        run: |
          echo "Validating generated JSON files..."
          for file in distributions/**/*.json; do
            echo "Checking $file..."
            jq empty "$file" && echo "  ✓ Valid"
          done

      - name: Upload JSON artifacts
        uses: actions/upload-artifact@v4
        with:
          name: curriculum-json-${{ github.sha }}
          path: distributions/
          retention-days: 30

      - name: Display summary
        run: |
          echo "### Generated Files" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
          find distributions -name "*.json" -exec ls -lh {} \; >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
EOF
```

**Test:**
```bash
# Commit and push
git add .github/workflows/generate-json.yml
git commit -m "ci: add JSON generation workflow"
git push origin main

# Check GitHub Actions
# Should see JSON files uploaded as artifacts
```

**Success Criteria:**
- ✅ Workflow generates JSON files
- ✅ Files are uploaded as artifacts
- ✅ Can download artifacts from GitHub Actions
- ✅ Summary shows file sizes

**Commit:** Already committed in test step

---

### Step 23: Create Fuseki Deployment Workflow ✅ **COMPLETED**

**Goal:** Automate Fuseki deployment to Cloud Run

**Actions:**
```bash
cat > .github/workflows/deploy-fuseki.yml <<'EOF'
name: Deploy Fuseki to Cloud Run

on:
  release:
    types: [ published ]
  workflow_dispatch:  # Allow manual trigger

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Configure Docker for GCR
        run: gcloud auth configure-docker

      - name: Build Docker image
        run: |
          docker build \
            -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/fuseki-uk-curriculum:${{ github.sha }} \
            -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/fuseki-uk-curriculum:latest \
            -f deployment/Dockerfile \
            .

      - name: Push Docker image
        run: |
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/fuseki-uk-curriculum:${{ github.sha }}
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/fuseki-uk-curriculum:latest

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy uk-curriculum-sparql \
            --image=gcr.io/${{ secrets.GCP_PROJECT_ID }}/fuseki-uk-curriculum:${{ github.sha }} \
            --platform=managed \
            --region=europe-west2 \
            --allow-unauthenticated \
            --port=3030 \
            --memory=2Gi \
            --cpu=2 \
            --max-instances=10 \
            --timeout=300 \
            --concurrency=80

      - name: Get service URL
        id: service-url
        run: |
          URL=$(gcloud run services describe uk-curriculum-sparql \
            --region=europe-west2 \
            --format='value(status.url)')
          echo "url=$URL" >> $GITHUB_OUTPUT
          echo "### Deployment Successful! 🚀" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**SPARQL Endpoint:** $URL/uk-curriculum/sparql" >> $GITHUB_STEP_SUMMARY

      - name: Test deployment
        run: |
          URL="${{ steps.service-url.outputs.url }}"
          echo "Testing deployment at $URL..."

          # Wait for service to be ready
          sleep 10

          # Test health endpoint
          curl -f ${URL}/$/ping || exit 1

          # Test SPARQL query
          COUNT=$(curl -s -X POST \
            -H "Content-Type: application/sparql-query" \
            -H "Accept: application/json" \
            --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
            ${URL}/uk-curriculum/sparql | jq -r '.results.bindings[0].count.value')

          echo "Triple count: $COUNT"

          if [ "$COUNT" -gt "0" ]; then
            echo "✅ Deployment test passed!"
          else
            echo "❌ Deployment test failed - no triples found"
            exit 1
          fi
EOF
```

**Note:** You'll need to set up GitHub secrets in Step 24.

**Success Criteria:**
- ✅ Workflow file is valid
- ✅ Includes deployment steps
- ✅ Includes testing
- ✅ References required secrets

**Commit:**
```bash
git add .github/workflows/deploy-fuseki.yml
git commit -m "ci: add Fuseki deployment workflow"
```

---

### Step 24: Configure GitHub Secrets

**Goal:** Set up secrets for GCP authentication

**Actions:**

**Manual steps in GitHub:**

1. **Create GCP Service Account:**
```bash
# In terminal
export PROJECT_ID=$(gcloud config get-value project)

# Create service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create ~/gcp-key.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Display key (copy for next step)
cat ~/gcp-key.json
```

2. **Add secrets to GitHub:**
   - Go to: https://github.com/YOUR-ORG/uk-curriculum-ontology/settings/secrets/actions
   - Click "New repository secret"
   - Add `GCP_SA_KEY`: Paste contents of ~/gcp-key.json
   - Add `GCP_PROJECT_ID`: Your GCP project ID

3. **Clean up local key:**
```bash
rm ~/gcp-key.json
```

**Test:**
```bash
# Push code to trigger workflow
git push origin main

# Or manually trigger deploy-fuseki workflow from GitHub Actions UI
# Actions tab → Deploy Fuseki to Cloud Run → Run workflow
```

**Success Criteria:**
- ✅ Service account created
- ✅ Secrets added to GitHub
- ✅ Workflow can authenticate with GCP
- ✅ Deployment succeeds

**Commit:** Not needed (GitHub configuration)

---

## Phase 7: Documentation & Distribution

### Step 25: Create Release Strategy Document

**Goal:** Document how to publish releases

**Actions:**
```bash
cat > RELEASE.md <<'EOF'
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
SERVICE_URL=$(gcloud run services describe uk-curriculum-sparql \
    --region=europe-west2 \
    --format='value(status.url)')

# Test SPARQL endpoint
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    ${SERVICE_URL}/uk-curriculum/sparql

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
EOF
```

**Success Criteria:**
- ✅ Clear release process documented
- ✅ Versioning strategy defined
- ✅ Automated deployment explained

**Commit:**
```bash
git add RELEASE.md
git commit -m "docs: add release process documentation"
```

---

### Step 26: Update README

**Goal:** Update main README with complete information

**Actions:**

Create a comprehensive README section:

```bash
# Add to existing README.md (manual edit, or use this as template)

cat >> README.md <<'EOF'

## Using the Data

### Option 1: Download JSON Files

Pre-generated JSON files are available from GitHub Releases:

```bash
# Download latest release
curl -L https://github.com/YOUR-ORG/uk-curriculum-ontology/releases/latest/download/curriculum-full.json

# Download specific subject
curl -L https://github.com/YOUR-ORG/uk-curriculum-ontology/releases/latest/download/science-ks3.json
```

### Option 2: SPARQL Endpoint

Query the live SPARQL endpoint:

```bash
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT * WHERE { ?s ?p ?o } LIMIT 10" \
    https://YOUR-SERVICE-URL.run.app/uk-curriculum/sparql
```

**Endpoint:** `https://YOUR-SERVICE-URL.run.app/uk-curriculum/sparql`

See [docs/examples.md](docs/examples.md) for query examples.

### Option 3: Build from Source

```bash
# Clone repository
git clone https://github.com/YOUR-ORG/uk-curriculum-ontology.git
cd uk-curriculum-ontology

# Generate JSON files
./scripts/build-static-data.sh

# Output: distributions/**/*.json
```

## For Developers

### Building

See [BUILD.md](BUILD.md) for build instructions.

### Deployment

See [deployment/DEPLOY.md](deployment/DEPLOY.md) for deployment guide.

### Releases

See [RELEASE.md](RELEASE.md) for release process.

### Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete architecture documentation.

## API Documentation

### JSON API

Generated JSON files follow this structure:

```json
{
  "results": {
    "bindings": [
      {
        "contentId": { "type": "literal", "value": "..." },
        "label": { "type": "literal", "value": "..." },
        "definition": { "type": "literal", "value": "..." }
      }
    ]
  }
}
```

### SPARQL API

Endpoint: `https://YOUR-SERVICE-URL.run.app/uk-curriculum/sparql`

**Query:**
```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>

SELECT * WHERE {
  ?subject a curric:Subject ;
           skos:prefLabel ?label .
}
```

**Example (curl):**
```bash
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data @query.sparql \
    https://YOUR-SERVICE-URL.run.app/uk-curriculum/sparql
```

## Cost

**Monthly Operating Cost:** ~$15-30
- Static JSON hosting: Free (GitHub)
- SPARQL endpoint: $10-30 (Google Cloud Run, scales to zero)

## Support

For questions or issues:
- Open an issue: https://github.com/YOUR-ORG/uk-curriculum-ontology/issues
- Email: curriculum@education.gov.uk
EOF
```

**Success Criteria:**
- ✅ README is comprehensive
- ✅ Includes usage examples
- ✅ Links to other documentation
- ✅ Clear for different user types

**Commit:**
```bash
git add README.md
git commit -m "docs: update README with usage and API documentation"
```

---

### Step 27: Create Example Queries Document

**Goal:** Provide examples for common use cases

**Actions:**
```bash
cat > docs/API-EXAMPLES.md <<'EOF'
# API Examples

## Using JSON API

### Get All Subjects

```bash
curl https://github.com/YOUR-ORG/uk-curriculum-ontology/releases/latest/download/subjects-index.json | jq .
```

### Get Science KS3 Content

```bash
curl https://github.com/YOUR-ORG/uk-curriculum-ontology/releases/latest/download/science-ks3.json | jq .
```

### Search All Content (Client-Side)

```javascript
// Download full dataset
const response = await fetch('https://github.com/.../curriculum-full.json');
const data = await response.json();

// Search for "cells"
const results = data.results.bindings.filter(item =>
  item.label.value.toLowerCase().includes('cells') ||
  item.definition.value.toLowerCase().includes('cells')
);

console.log(results);
```

## Using SPARQL API

### Python Example

```python
import requests

endpoint = "https://YOUR-SERVICE-URL.run.app/uk-curriculum/sparql"

query = """
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?subject ?label WHERE {
  ?subject a curric:Subject ;
           skos:prefLabel ?label .
}
ORDER BY ?label
"""

response = requests.post(
    endpoint,
    data=query,
    headers={
        'Content-Type': 'application/sparql-query',
        'Accept': 'application/json'
    }
)

data = response.json()
for binding in data['results']['bindings']:
    print(f"{binding['subject']['value']}: {binding['label']['value']}")
```

### JavaScript (Node.js) Example

```javascript
const fetch = require('node-fetch');

const endpoint = 'https://YOUR-SERVICE-URL.run.app/uk-curriculum/sparql';

const query = `
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>

SELECT ?content ?label WHERE {
  ?scheme curric:hasSubject eng:science ;
          curric:hasKeyStage eng:key-stage-3 ;
          curric:hasContent ?content .
  ?content skos:prefLabel ?label .
}
LIMIT 10
`;

fetch(endpoint, {
  method: 'POST',
  body: query,
  headers: {
    'Content-Type': 'application/sparql-query',
    'Accept': 'application/json'
  }
})
.then(res => res.json())
.then(data => {
  data.results.bindings.forEach(item => {
    console.log(`${item.content.value}: ${item.label.value}`);
  });
});
```

### curl Example

```bash
# Save query to file
cat > query.sparql <<'SPARQL'
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>

SELECT ?ks ?label WHERE {
  ?ks a curric:KeyStage ;
      skos:prefLabel ?label .
}
ORDER BY ?label
SPARQL

# Execute query
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data-binary @query.sparql \
    https://YOUR-SERVICE-URL.run.app/uk-curriculum/sparql | jq .
```

## Common Queries

### Find Content by Keyword

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label ?definition WHERE {
  ?content skos:prefLabel ?label ;
           skos:definition ?definition .
  FILTER(CONTAINS(LCASE(?definition), "photosynthesis"))
}
```

### Get All Content for a Subject

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>

SELECT ?content ?label WHERE {
  ?scheme curric:hasSubject eng:science ;
          curric:hasContent ?content .
  ?content skos:prefLabel ?label .
}
```

### Find Cross-Cutting Themes

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>

SELECT ?theme ?themeLabel ?content ?contentLabel WHERE {
  ?content curric:hasTheme ?theme .
  ?theme skos:prefLabel ?themeLabel .
  ?content skos:prefLabel ?contentLabel .
}
```
EOF
```

**Success Criteria:**
- ✅ Examples for multiple languages
- ✅ Common use cases covered
- ✅ Copy-paste ready code

**Commit:**
```bash
git add docs/API-EXAMPLES.md
git commit -m "docs: add API usage examples"
```

---

### Step 28: Final Testing & Documentation Review

**Goal:** End-to-end test of complete system

**Actions:**

**Test Checklist:**

```bash
# 1. Validate data
./scripts/validate.sh
# ✅ Should pass

# 2. Generate JSON
./scripts/build-static-data.sh
# ✅ Should create distributions/ folder

# 3. Test JSON output
cat distributions/subjects/index.json | jq .
cat distributions/subjects/science-ks3.json | jq '.results.bindings | length'
# ✅ Should show valid JSON with data

# 4. Test Fuseki locally
docker build -t fuseki-test -f deployment/Dockerfile .
docker run -d --name fuseki-test -p 3030:3030 fuseki-test
sleep 10

curl http://localhost:3030/$/ping
# ✅ Should return 200 OK

curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    http://localhost:3030/uk-curriculum/sparql | jq .
# ✅ Should return count > 0

docker stop fuseki-test && docker rm fuseki-test

# 5. Test Cloud Run deployment
SERVICE_URL=$(gcloud run services describe uk-curriculum-sparql \
    --region=europe-west2 \
    --format='value(status.url)')

curl ${SERVICE_URL}/$/ping
# ✅ Should return 200 OK

curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    ${SERVICE_URL}/uk-curriculum/sparql | jq .
# ✅ Should return count > 0

# 6. Review documentation
cat ARCHITECTURE.md | head -50
cat BUILD.md
cat deployment/DEPLOY.md
cat RELEASE.md
cat docs/API-EXAMPLES.md
# ✅ All documentation exists and is complete

echo "✅ All tests passed!"
```

**Success Criteria:**
- ✅ All scripts work
- ✅ Local Fuseki works
- ✅ Cloud Run deployment works
- ✅ Documentation is complete
- ✅ Examples are accurate

**Commit:**
```bash
# If any docs need updates, commit them
git add .
git commit -m "docs: final documentation review and updates"
git push origin main
```

---

## Summary

### What We've Built

✅ **Phase 1:** Local validation pipeline
✅ **Phase 2:** SPARQL query library
✅ **Phase 3:** JSON generation system
✅ **Phase 4:** Local Fuseki testing
✅ **Phase 5:** Google Cloud Run deployment
✅ **Phase 6:** Complete CI/CD pipeline
✅ **Phase 7:** Comprehensive documentation

### Repository Structure

```
uk-curriculum-ontology/
├── .github/workflows/           # CI/CD
│   ├── validate.yml
│   ├── generate-json.yml
│   └── deploy-fuseki.yml
├── deployment/                  # Fuseki
│   ├── Dockerfile
│   ├── fuseki-config.ttl
│   └── DEPLOY.md
├── queries/                     # SPARQL
│   ├── subjects-index.sparql
│   ├── science-ks3.sparql
│   └── full-curriculum.sparql
├── scripts/                     # Build
│   ├── validate.sh
│   └── build-static-data.sh
├── docs/                        # Docs
│   └── API-EXAMPLES.md
├── ARCHITECTURE.md
├── BUILD.md
├── RELEASE.md
└── README.md
```

### What Runs Where

**Locally:**
- Validation (`./scripts/validate.sh`)
- JSON generation (`./scripts/build-static-data.sh`)
- Fuseki testing (Docker)

**GitHub Actions:**
- Validation (every push)
- JSON generation (releases)
- Fuseki deployment (releases)

**Google Cloud Run:**
- Public SPARQL endpoint
- Auto-scaling, production-ready

### Next Steps After Implementation

1. **Create first release:** v0.1.0
2. **Test complete workflow:** GitHub Release → CI/CD → Production
3. **Monitor costs:** Check Cloud Run billing after 1 week
4. **Add more subjects:** Mathematics, English, etc.
5. **Build web app:** Separate repository consuming JSON API

---

## Appendix: Quick Reference

### Essential Commands

```bash
# Validate
./scripts/validate.sh

# Generate JSON
./scripts/build-static-data.sh

# Test locally
docker build -t fuseki-test -f deployment/Dockerfile .
docker run -p 3030:3030 fuseki-test

# Deploy to Cloud Run
docker build -t gcr.io/$PROJECT_ID/fuseki-uk-curriculum:latest -f deployment/Dockerfile .
docker push gcr.io/$PROJECT_ID/fuseki-uk-curriculum:latest
gcloud run deploy uk-curriculum-sparql --image=gcr.io/$PROJECT_ID/fuseki-uk-curriculum:latest

# Create release
git tag v0.1.0
git push origin v0.1.0
# Then create GitHub Release via UI
```

### Troubleshooting

**Issue:** Validation fails
**Fix:** Check Turtle syntax with `riot --validate file.ttl`

**Issue:** Docker build fails
**Fix:** Check file paths in Dockerfile COPY commands

**Issue:** Cloud Run deployment fails
**Fix:** Check GCP permissions and API enablement

**Issue:** SPARQL queries return no results
**Fix:** Verify data is loaded in Fuseki logs

---

**END OF IMPLEMENTATION PLAN**
