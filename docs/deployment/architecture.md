#DfE Curriculum Ontology - Architecture Documentation

**Version:** 1.0
**Date:** 2025-12-15
**Status:** Final Design

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Components](#components)
4. [Data Flow](#data-flow)
5. [Build Process](#build-process)
6. [Deployment Strategy](#deployment-strategy)
7. [User Journeys](#user-journeys)
8. [Technology Stack](#technology-stack)
9. [Development Workflow](#development-workflow)
10. [Cost Estimates](#cost-estimates)
11. [Maintenance & Operations](#maintenance--operations)
12. [Design Decisions & Rationale](#design-decisions--rationale)

---

## Executive Summary

### The Solution

A **two-component architecture** that provides both a user-friendly curriculum website and a powerful SPARQL API for developers:

1. **Static Website** - Fast, accessible curriculum browser with client-side search
2. **SPARQL Endpoint** - Public API for developers and researchers

### Key Principles

- ✅ **Simple** - Minimal infrastructure, maximum reliability
- ✅ **Fast** - Static files, client-side search, instant results
- ✅ **Scalable** - Works from 2 subjects to 100+
- ✅ **Cost-effective** - ~$15-35/month total
- ✅ **Standards-based** - RDF, SPARQL, semantic web best practices
- ✅ **Accessible** - Multiple access patterns for different user types

### Design Decision: No Backend API

**We chose NOT to build a backend API for search** because:
- Dataset is small (~500KB)
- Queries are simple (filter/search)
- Client-side search is faster and more reliable
- Reduces infrastructure complexity and cost

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GITHUB REPOSITORY                           │
│                   (Single Source of Truth)                      │
│                                                                 │
│  ├── ontology/                                                  │
│  │   ├── dfe-curriculum-ontology.ttl        (Classes/Props)    │
│  │   └── dfe-curriculum-constraints.ttl     (SHACL)            │
│  │                                                              │
│  ├── data/                                                      │
│  │   └── national-curriculum-for-england/                      │
│  │       ├── programme-structure.ttl        (KS, Phases)       │
│  │       ├── themes.ttl                     (Themes)           │
│  │       └── subjects/                                         │
│  │           ├── science/*.ttl                                 │
│  │           └── history/*.ttl                                 │
│  │                                                              │
│  ├── queries/                                                   │
│  │   ├── science-ks3.sparql                (Build queries)     │
│  │   ├── history-ks3.sparql                                    │
│  │   └── full-curriculum.sparql                                │
│  │                                                              │
│  └── scripts/                                                   │
│      └── build-static-data.sh              (JSON generator)    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Push / Release
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS (CI/CD)                       │
│                                                                 │
│  On push to main / release:                                     │
│  ├── 1. Validate SHACL constraints                             │
│  ├── 2. Generate static JSON files (queries/*.sparql)          │
│  ├── 3. Build & deploy static website                          │
│  └── 4. Build & deploy Fuseki container                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
┌──────────────────────────────┐  ┌────────────────────────────┐
│   STATIC WEBSITE             │  │   FUSEKI SPARQL ENDPOINT   │
│   curriculum.education.gov.uk│  │   sparql.curriculum.       │
│                              │  │   education.gov.uk         │
│  Hosting: Vercel/Netlify/    │  │                            │
│          Cloud Storage       │  │   Hosting: Cloud Run       │
│  Cost: Free - $5/month       │  │   Cost: $10-30/month       │
│                              │  │                            │
│  Content:                    │  │   Content:                 │
│  ├── HTML pages (SSG)        │  │   ├── SPARQL query endpoint│
│  └── /api/**/*.json          │  │   └── All RDF data loaded  │
│      ├── Pre-generated       │  │                            │
│      │   queries (browsing)  │  │   Users:                   │
│      └── Full dataset        │  │   ├── Developers           │
│          (search)            │  │   ├── Researchers          │
│                              │  │   └── 3rd party services   │
│  Users:                      │  │                            │
│  ├── Teachers                │  │   Access: Server-side only │
│  ├── Students                │  │          (no CORS)         │
│  ├── General public          │  │                            │
│  └── Curriculum developers   │  │                            │
└──────────────────────────────┘  └────────────────────────────┘
```

---

## Components

### Component 1: Static Website

**Purpose:** Primary user interface for browsing and searching the National Curriculum

**Technology:**
- Next.js (with Static Site Generation) OR
- Gatsby OR
- Hugo (static site generator)

**Content Structure:**
```
static-site/
├── pages/
│   ├── index.html                          (Homepage)
│   ├── subjects/
│   │   ├── index.html                      (All subjects)
│   │   ├── science/
│   │   │   ├── index.html                  (Science overview)
│   │   │   ├── ks1.html                    (Science KS1)
│   │   │   ├── ks3.html                    (Science KS3)
│   │   │   └── ks4.html
│   │   └── history/
│   │       ├── index.html
│   │       └── ...
│   ├── keystages/
│   │   ├── ks1.html                        (All KS1 content)
│   │   ├── ks3.html
│   │   └── ...
│   └── search/
│       └── index.html                      (Search interface)
│
└── api/                                     (Static JSON files)
    ├── subjects/
    │   ├── index.json                      (All subjects list)
    │   ├── science/
    │   │   ├── index.json                  (Science metadata)
    │   │   ├── ks1.json                    (Science KS1 data)
    │   │   ├── ks3.json                    (Science KS3 data)
    │   │   └── ks4.json
    │   └── history/
    │       └── ...
    ├── keystages/
    │   ├── ks1.json                        (All KS1 data)
    │   ├── ks3.json
    │   └── ...
    ├── themes/
    │   ├── index.json                      (All themes)
    │   └── climate-change.json             (Theme details)
    └── curriculum-full.json                 (Complete dataset for search)
```

**Key Features:**
- Pre-rendered HTML pages (SEO-friendly)
- Client-side hydration for interactivity
- Static JSON files for dynamic content loading
- Client-side search using full dataset
- Progressive enhancement (works without JavaScript for basic browsing)

**Performance Characteristics:**
- Initial page load: < 1 second
- JSON file loads: 10-100KB per file
- Full dataset load (for search): ~500KB (cached)
- Search latency: 0ms (instant client-side filtering)

---

### Component 2: Apache Jena Fuseki SPARQL Endpoint

**Purpose:** Public SPARQL API for developers, researchers, and 3rd party integrations

**Technology:**
- Apache Jena Fuseki 4.x
- Docker container
- Google Cloud Run (serverless)

**Configuration:**
```turtle
# fuseki-config.ttl
@prefix fuseki:  <http://jena.apache.org/fuseki#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ja:      <http://jena.hpl.hp.com/2005/11/Assembler#> .
@prefix tdb2:    <http://jena.apache.org/2016/tdb#> .

<#service> a fuseki:Service ;
    fuseki:name "uk-curriculum" ;
    fuseki:endpoint [
        fuseki:operation fuseki:query ;
        fuseki:name "sparql"
    ] ;
    fuseki:endpoint [
        fuseki:operation fuseki:gsp-r ;
        fuseki:name "get"
    ] ;
    fuseki:dataset <#dataset> .

<#dataset> a tdb2:DatasetTDB2 ;
    tdb2:location "/fuseki-base/databases/uk-curriculum-tdb2" ;
    tdb2:unionDefaultGraph true .
```

**Endpoints:**
- `GET/POST /uk-curriculum/sparql` - SPARQL query endpoint
- `GET /uk-curriculum/get` - Graph Store Protocol (read-only)
- `GET /$/ping` - Health check

**Data Loading:**
- All TTL files loaded at Docker build time
- Immutable deployments (data baked into container)
- TDB2 storage for performance

**Access:**
- Public read-only access
- No CORS headers (server-side access only)
- No authentication required
- Rate limiting via Cloud Run (future consideration)

**Performance Characteristics:**
- Cold start: 5-15 seconds (Cloud Run)
- Query latency: 50-500ms depending on complexity
- Auto-scales: 0-100 instances
- Memory: 1GB per instance

---

## Data Flow

### Flow 1: Development → Production (Build Time)

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Developer Updates Curriculum                        │
└──────────────────────────────────────────────────────────────┘
Developer edits: data/subjects/science/science-schemes.ttl
Commits and pushes to GitHub
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: GitHub Actions Triggers                             │
└──────────────────────────────────────────────────────────────┘
Workflow: .github/workflows/deploy.yml
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Validation                                           │
└──────────────────────────────────────────────────────────────┘
Run: scripts/validate.sh
- Validates all TTL syntax
- Checks SHACL constraints
- Fails build if errors found
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: Generate Static JSON Files                          │
└──────────────────────────────────────────────────────────────┘
Run: scripts/build-static-data.sh
- Loads all TTL files
- Executes queries from queries/*.sparql
- Generates JSON files for each:
  - Subject × Key Stage combination
  - Theme pages
  - Full curriculum dataset
Output: static/api/**/*.json
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: Build Static Website                                │
└──────────────────────────────────────────────────────────────┘
Run: npm run build (Next.js/Gatsby)
- Generates HTML pages from JSON data
- Optimizes assets
- Creates sitemap
Output: out/ or public/
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 6: Build Fuseki Docker Container                       │
└──────────────────────────────────────────────────────────────┘
Run: docker build -f deployment/Dockerfile
- Copies all TTL files into container
- Loads data into TDB2 database
- Bakes data into immutable container image
Output: gcr.io/PROJECT/fuseki:TAG
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
┌──────────────────────────────┐  ┌────────────────────────┐
│ STEP 7a: Deploy Static Site  │  │ STEP 7b: Deploy Fuseki │
└──────────────────────────────┘  └────────────────────────┘
Deploy to: Vercel/Netlify/         Deploy to: Cloud Run
           Cloud Storage
Result: curriculum.               Result: sparql.curriculum.
        education.gov.uk                  education.gov.uk
```

---

### Flow 2: User Browses Curriculum (Runtime)

```
┌──────────────────────────────────────────────────────────────┐
│ User visits: curriculum.education.gov.uk/subjects/science/ks3│
└──────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ Static HTML Page Loads                                       │
└──────────────────────────────────────────────────────────────┘
Serves: /subjects/science/ks3.html (pre-rendered)
- Fast CDN delivery
- SEO metadata included
- Works without JavaScript
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ JavaScript Enhances Page                                     │
└──────────────────────────────────────────────────────────────┘
Fetches: /api/subjects/science/ks3.json (~50KB)
- Loads detailed content data
- Enables interactive features
- Caches for subsequent views
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ User Sees Curriculum Content                                 │
└──────────────────────────────────────────────────────────────┘
Displays:
- Science strands for KS3
- Content descriptors
- Links to related content
- Cross-cutting themes

Total time: < 1 second
```

---

### Flow 3: User Searches Curriculum (Runtime)

```
┌──────────────────────────────────────────────────────────────┐
│ User types: "photosynthesis" in search box                   │
└──────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ Load Full Dataset (First Search Only)                        │
└──────────────────────────────────────────────────────────────┘
Fetches: /api/curriculum-full.json (~500KB, once)
- Downloads complete curriculum
- Caches in browser memory
- Gzipped to ~100KB on wire
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ Client-Side JavaScript Filters Data                          │
└──────────────────────────────────────────────────────────────┘
Runs filter on local data:
  data.filter(item =>
    item.label.includes('photosynthesis') ||
    item.description.includes('photosynthesis')
  )
Time: < 10ms (instant)
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ Display Search Results                                       │
└──────────────────────────────────────────────────────────────┘
Shows matching content with:
- Subject
- Key Stage
- Content description
- Link to full page

Subsequent searches: Instant (data already in memory)
```

---

### Flow 4: Developer Queries SPARQL Endpoint (Runtime)

```
┌──────────────────────────────────────────────────────────────┐
│ Developer wants: "All Science content mentioning climate"    │
└──────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ Developer Writes SPARQL Query                                │
└──────────────────────────────────────────────────────────────┘
```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label ?description WHERE {
  ?content curric:hasSubject eng:science ;
           skos:prefLabel ?label ;
           skos:definition ?description .
  FILTER(CONTAINS(LCASE(?description), "climate"))
}
```
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ Send Query to SPARQL Endpoint                                │
└──────────────────────────────────────────────────────────────┘
POST https://sparql.curriculum.education.gov.uk/uk-curriculum/sparql
Content-Type: application/sparql-query
Accept: application/json

[SPARQL query body]
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ Fuseki Processes Query                                       │
└──────────────────────────────────────────────────────────────┘
- Parses SPARQL
- Queries TDB2 database
- Returns results as JSON
Time: 50-300ms
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ Developer Receives Results                                   │
└──────────────────────────────────────────────────────────────┘
```json
{
  "results": {
    "bindings": [
      {
        "content": {"type": "uri", "value": "..."},
        "label": {"type": "literal", "value": "..."},
        "description": {"type": "literal", "value": "..."}
      }
    ]
  }
}
```

Developer integrates into their application
```

---

## Build Process

### Overview

The build process transforms RDF/Turtle files into:
1. Static JSON files for the website
2. Docker container for Fuseki

### Prerequisites

**Required Tools:**
- Apache Jena CLI tools (`arq`, `riot`, `tdbloader`)
- Docker
- Node.js (for static site generation)
- Python 3.x (alternative for JSON generation)

**Installation:**
```bash
# Apache Jena
wget https://dlcdn.apache.org/jena/binaries/apache-jena-4.10.0.tar.gz
tar xzf apache-jena-4.10.0.tar.gz
export PATH=$PATH:$PWD/apache-jena-4.10.0/bin

# Or via package manager
brew install jena  # macOS
apt install jena   # Ubuntu
```

---

### Step 1: Validate Data

**Script:** `scripts/validate.sh`

```bash
#!/bin/bash
# Validate all Turtle files for syntax and SHACL constraints

set -e

echo "🔍 Validating Turtle syntax..."

# Check syntax of all TTL files
for file in ontology/*.ttl data/**/*.ttl; do
    echo "  Checking $file..."
    riot --validate "$file" || {
        echo "❌ Syntax error in $file"
        exit 1
    }
done

echo "✅ All files have valid Turtle syntax"

echo ""
echo "🔍 Validating SHACL constraints..."

# Run SHACL validation
shacl validate \
    --shapes=ontology/dfe-curriculum-constraints.ttl \
    --data=ontology/dfe-curriculum-ontology.ttl \
    --data=data/**/*.ttl

echo "✅ All SHACL constraints satisfied"
```

**Run:**
```bash
./scripts/validate.sh
```

---

### Step 2: Generate Static JSON Files

**Script:** `scripts/build-static-data.sh`

```bash
#!/bin/bash
# Generate static JSON files from RDF data

set -e

echo "🏗️  Building static JSON files..."

# Output directory
OUTPUT_DIR="static/api"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/subjects" "$OUTPUT_DIR/keystages" "$OUTPUT_DIR/themes"

# Collect all data files
DATA_FILES="--data=ontology/dfe-curriculum-ontology.ttl"
DATA_FILES="$DATA_FILES --data=ontology/dfe-curriculum-constraints.ttl"
DATA_FILES="$DATA_FILES --data=data/national-curriculum-for-england/programme-structure.ttl"
DATA_FILES="$DATA_FILES --data=data/national-curriculum-for-england/themes.ttl"

# Add all subject files
for file in data/national-curriculum-for-england/subjects/**/*.ttl; do
    DATA_FILES="$DATA_FILES --data=$file"
done

# Generate subject index
echo "📋 Generating subjects index..."
arq $DATA_FILES \
    --query=queries/subjects-index.sparql \
    --results=JSON > "$OUTPUT_DIR/subjects/index.json"

# Generate Science KS3
echo "🔬 Generating Science KS3..."
arq $DATA_FILES \
    --query=queries/science-ks3.sparql \
    --results=JSON > "$OUTPUT_DIR/subjects/science-ks3.json"

# Generate History KS3
echo "📚 Generating History KS3..."
arq $DATA_FILES \
    --query=queries/history-ks3.sparql \
    --results=JSON > "$OUTPUT_DIR/subjects/history-ks3.json"

# Generate full curriculum dataset (for search)
echo "🌍 Generating full curriculum dataset..."
arq $DATA_FILES \
    --query=queries/full-curriculum.sparql \
    --results=JSON > "$OUTPUT_DIR/curriculum-full.json"

# Calculate statistics
TOTAL_FILES=$(find "$OUTPUT_DIR" -name "*.json" | wc -l)
TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)

echo ""
echo "✅ Generated $TOTAL_FILES JSON files ($TOTAL_SIZE)"
```

**Example Query:** `queries/science-ks3.sparql`

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?contentId ?label ?definition ?strandLabel WHERE {
  # Find Science KS3 scheme
  ?scheme a curric:Scheme ;
          curric:hasSubject eng:science ;
          curric:hasKeyStage eng:key-stage-3 ;
          curric:hasContent ?content .

  # Get content details
  ?content skos:prefLabel ?label ;
           skos:definition ?definition .

  # Get strand
  OPTIONAL {
    ?strand curric:hasContentDescriptor ?content ;
            skos:prefLabel ?strandLabel .
  }

  BIND(STRAFTER(STR(?content), "england/") AS ?contentId)
}
ORDER BY ?strandLabel ?label
```

**Run:**
```bash
./scripts/build-static-data.sh
```

---

### Step 3: Build Static Website

**Framework:** Next.js with Static Site Generation

**Configuration:** `next.config.js`

```javascript
module.exports = {
  output: 'export', // Static export
  images: {
    unoptimized: true, // For static hosting
  },
  trailingSlash: true,
}
```

**Build:**
```bash
npm run build

# Output: out/ directory with static HTML/CSS/JS
```

**Pages generated:**
- `/` - Homepage
- `/subjects/` - All subjects
- `/subjects/science/ks3/` - Science KS3
- `/subjects/history/ks3/` - History KS3
- `/search/` - Search interface
- etc.

---

### Step 4: Build Fuseki Docker Container

**Dockerfile:** `deployment/Dockerfile`

```dockerfile
FROM stain/jena-fuseki:4.10.0

# Metadata
LABEL maintainer="Department for Education"
LABEL description="UK Curriculum Ontology SPARQL Endpoint"
LABEL version="0.1.0"

# Create directories
RUN mkdir -p /fuseki-base/databases /fuseki-base/configuration

# Copy ontology and data files
COPY ontology/*.ttl /staging/
COPY data/national-curriculum-for-england/programme-structure.ttl /staging/
COPY data/national-curriculum-for-england/themes.ttl /staging/
COPY data/national-curriculum-for-england/subjects/**/*.ttl /staging/

# Load data into TDB2 (at build time)
RUN /jena-fuseki/tdb2.tdbloader \
    --loc=/fuseki-base/databases/uk-curriculum-tdb2 \
    /staging/*.ttl

# Copy Fuseki configuration
COPY deployment/fuseki-config.ttl /fuseki-base/configuration/

# Expose port
EXPOSE 3030

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3030/$/ping || exit 1

# Start Fuseki
CMD ["/jena-fuseki/fuseki-server", \
     "--config=/fuseki-base/configuration/fuseki-config.ttl"]
```

**Build:**
```bash
cd deployment
docker build -t uk-curriculum-fuseki:latest .

# Test locally
docker run -p 3030:3030 uk-curriculum-fuseki:latest

# Visit: http://localhost:3030/uk-curriculum/sparql
```

---

## Deployment Strategy

### Deployment 1: Static Website

**Option A: Vercel (Recommended)**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd static-site
vercel --prod
```

**Configuration:** `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "headers": {
        "Cache-Control": "public, max-age=3600, s-maxage=86400"
      }
    }
  ]
}
```

**Option B: Google Cloud Storage + Cloud CDN**

```bash
# Create bucket
gsutil mb gs://curriculum-education-gov-uk

# Enable public access
gsutil iam ch allUsers:objectViewer gs://curriculum-education-gov-uk

# Upload files
gsutil -m rsync -r out/ gs://curriculum-education-gov-uk

# Set cache headers
gsutil -m setmeta -h "Cache-Control:public, max-age=3600" \
    gs://curriculum-education-gov-uk/api/**/*.json
```

**Option C: Netlify**

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
cd static-site
netlify deploy --prod --dir=out
```

---

### Deployment 2: Fuseki SPARQL Endpoint

**Platform:** Google Cloud Run

**Steps:**

```bash
# 1. Set variables
export PROJECT_ID="your-gcp-project"
export REGION="europe-west2"
export SERVICE_NAME="uk-curriculum-sparql"
export IMAGE="gcr.io/${PROJECT_ID}/fuseki-uk-curriculum"

# 2. Build and tag Docker image
docker build -t ${IMAGE}:latest deployment/

# 3. Authenticate with GCP
gcloud auth login
gcloud config set project ${PROJECT_ID}

# 4. Configure Docker for GCR
gcloud auth configure-docker

# 5. Push image to Google Container Registry
docker push ${IMAGE}:latest

# 6. Deploy to Cloud Run
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

# 7. Get service URL
gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)'
```

**Result:** Your endpoint will be available at:
```
https://uk-curriculum-sparql-xxxxx-ew.a.run.app/uk-curriculum/sparql
```

**Custom Domain:** Map to `sparql.curriculum.education.gov.uk`

```bash
gcloud run domain-mappings create \
    --service=${SERVICE_NAME} \
    --domain=sparql.curriculum.education.gov.uk \
    --region=${REGION}

# Add DNS record (provided by Cloud Run)
```

---

### CI/CD Pipeline

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy Curriculum Website and SPARQL Endpoint

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Apache Jena
        run: |
          wget https://dlcdn.apache.org/jena/binaries/apache-jena-4.10.0.tar.gz
          tar xzf apache-jena-4.10.0.tar.gz
          echo "$PWD/apache-jena-4.10.0/bin" >> $GITHUB_PATH

      - name: Validate Turtle files
        run: ./scripts/validate.sh

  build-static-data:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Apache Jena
        run: |
          wget https://dlcdn.apache.org/jena/binaries/apache-jena-4.10.0.tar.gz
          tar xzf apache-jena-4.10.0.tar.gz
          echo "$PWD/apache-jena-4.10.0/bin" >> $GITHUB_PATH

      - name: Generate JSON files
        run: ./scripts/build-static-data.sh

      - name: Upload JSON artifacts
        uses: actions/upload-artifact@v4
        with:
          name: static-json
          path: static/api/

  deploy-website:
    needs: build-static-data
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download JSON artifacts
        uses: actions/download-artifact@v4
        with:
          name: static-json
          path: static-site/public/api/

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd static-site
          npm ci

      - name: Build website
        run: |
          cd static-site
          npm run build

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: static-site
          vercel-args: '--prod'

  deploy-fuseki:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Configure Docker
        run: gcloud auth configure-docker

      - name: Build Docker image
        run: |
          docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/fuseki-uk-curriculum:${{ github.sha }} \
                       -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/fuseki-uk-curriculum:latest \
                       deployment/

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
            --timeout=300
```

---

## User Journeys

### Journey 1: Teacher Finding KS3 Science Content

**User:** Secondary school science teacher
**Goal:** Find what needs to be taught in Year 8 (KS3) Science

**Steps:**

1. **Visit website**
   - URL: `https://curriculum.education.gov.uk`
   - Sees homepage with subject list

2. **Navigate to Science**
   - Clicks "Science" button
   - Loads: `/subjects/science/` page
   - Sees overview and key stage options

3. **Select Key Stage 3**
   - Clicks "Key Stage 3" button
   - Loads: `/subjects/science/ks3/` page
   - Downloads: `/api/subjects/science-ks3.json` (~50KB)
   - Time: < 1 second

4. **Browse content**
   - Sees organized list of strands:
     - Structure and function of living organisms
     - Material cycles and energy
   - Expands strand to see content descriptors
   - Reads detailed descriptions

5. **Find specific topic**
   - Uses browser Ctrl+F to search "cells"
   - OR uses site search box
   - Finds "Cells as fundamental unit" content
   - Clicks to see full details

**Total time:** < 30 seconds
**Network requests:** 2-3
**Data downloaded:** ~100KB

---

### Journey 2: Developer Building Ed-Tech App

**User:** Software developer at ed-tech company
**Goal:** Build app showing curriculum progression across key stages

**Steps:**

1. **Discover SPARQL endpoint**
   - Finds documentation at curriculum.education.gov.uk/developers
   - Endpoint: `https://sparql.curriculum.education.gov.uk/uk-curriculum/sparql`

2. **Test query locally**
   ```python
   import requests

   query = """
   PREFIX curric: <https://w3id.org/uk/curriculum/core/>
   PREFIX eng: <https://w3id.org/uk/curriculum/england/>

   SELECT ?ks ?content ?label WHERE {
     ?scheme curric:hasSubject eng:science ;
             curric:hasKeyStage ?ks ;
             curric:hasContent ?content .
     ?content skos:prefLabel ?label .
   }
   ORDER BY ?ks
   """

   response = requests.post(
       'https://sparql.curriculum.education.gov.uk/uk-curriculum/sparql',
       data=query,
       headers={
           'Content-Type': 'application/sparql-query',
           'Accept': 'application/json'
       }
   )

   data = response.json()
   ```

3. **Integrate into app**
   - Writes Python service to query SPARQL endpoint
   - Caches results locally
   - Builds visualization showing progression

4. **Deploy app**
   - App queries SPARQL endpoint on demand
   - No need to duplicate curriculum data
   - Always up-to-date with official curriculum

---

### Journey 3: Researcher Analyzing Curriculum

**User:** Education researcher
**Goal:** Analyze how climate change is covered across subjects

**Steps:**

1. **Access SPARQL endpoint**
   - Uses Apache Jena command-line tools OR
   - Uses Python with SPARQLWrapper library

2. **Write complex query**
   ```sparql
   PREFIX curric: <https://w3id.org/uk/curriculum/core/>
   PREFIX eng: <https://w3id.org/uk/curriculum/england/>
   PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

   SELECT ?subject ?subjectLabel ?ks ?content ?label
   WHERE {
     ?content curric:hasTheme eng:theme-climate-change ;
              skos:prefLabel ?label .

     ?scheme curric:hasContent ?content ;
             curric:hasSubject ?subject ;
             curric:hasKeyStage ?ks .

     ?subject skos:prefLabel ?subjectLabel .
   }
   ORDER BY ?subjectLabel ?ks
   ```

3. **Export results**
   - Saves as CSV
   - Imports into spreadsheet
   - Performs statistical analysis

4. **Publish research**
   - Cites SPARQL endpoint in paper
   - Shares query for reproducibility
   - Other researchers can verify findings

---

## Technology Stack

### Static Website

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Framework** | Next.js 14+ | Static generation, React ecosystem, excellent DX |
| **Alternative 1** | Gatsby | GraphQL integration, rich plugin ecosystem |
| **Alternative 2** | Hugo | Fastest builds, simple, Go-based |
| **Language** | TypeScript | Type safety, better tooling |
| **Styling** | Tailwind CSS | Utility-first, fast development, small bundle |
| **Search UI** | Custom + Fuse.js | Fuzzy search, lightweight (12KB) |
| **Data Fetching** | Static JSON | Simple, cacheable, no runtime deps |
| **Hosting** | Vercel / Netlify | Edge network, automatic HTTPS, git integration |
| **Alternative** | Cloud Storage + CDN | Lower cost, more control |

**Key Dependencies:**
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "fuse.js": "^7.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0",
    "@types/react": "^18.0.0"
  }
}
```

---

### SPARQL Endpoint

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Triple Store** | Apache Jena Fuseki 4.x | Industry standard, reliable, good performance |
| **Storage** | TDB2 | Better performance than TDB1, built-in |
| **Container** | Docker | Portability, reproducibility |
| **Base Image** | `stain/jena-fuseki` | Official, well-maintained |
| **Hosting** | Google Cloud Run | Serverless, auto-scaling, cost-effective |
| **Alternative 1** | AWS Fargate | Similar to Cloud Run |
| **Alternative 2** | Azure Container Instances | Similar to Cloud Run |

**Container Specs:**
- **Memory:** 2GB (scales to 4GB if needed)
- **CPU:** 2 vCPU
- **Max instances:** 10 (adjust based on usage)
- **Min instances:** 0 (scales to zero when idle)
- **Timeout:** 300s (5 minutes for complex queries)

---

### Build Tools

| Tool | Purpose | Installation |
|------|---------|-------------|
| **Apache Jena** | SPARQL queries, validation | `brew install jena` |
| **riot** | Turtle syntax validation | Included with Jena |
| **arq** | Command-line SPARQL | Included with Jena |
| **tdbloader** | Load RDF into TDB2 | Included with Jena |
| **Node.js** | Static site building | `brew install node` |
| **Docker** | Container building | `brew install docker` |
| **gcloud CLI** | Cloud Run deployment | `brew install google-cloud-sdk` |

---

### CI/CD

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Version Control** | GitHub | Industry standard, great actions |
| **CI/CD** | GitHub Actions | Integrated, free for public repos |
| **Secrets** | GitHub Secrets | Secure, easy to manage |
| **Artifacts** | GitHub Artifacts | Share data between jobs |

---

## Development Workflow

### Local Development Setup

**1. Clone repository**
```bash
git clone https://github.com/your-org/uk-curriculum-ontology.git
cd uk-curriculum-ontology
```

**2. Install dependencies**
```bash
# Apache Jena
brew install jena

# Node.js dependencies (for static site)
cd static-site
npm install
cd ..

# Docker (for Fuseki)
brew install docker
```

**3. Run Fuseki locally**
```bash
# Build container
docker build -t fuseki-local deployment/

# Run container
docker run -p 3030:3030 fuseki-local

# Visit: http://localhost:3030
```

**4. Generate static JSON**
```bash
./scripts/build-static-data.sh
```

**5. Run static site locally**
```bash
cd static-site
npm run dev

# Visit: http://localhost:3000
```

---

### Making Changes to Curriculum Data

**Scenario:** Add new content to Science KS3

**Steps:**

1. **Edit data file**
   ```bash
   # Open file
   vim data/national-curriculum-for-england/subjects/science/science-schemes.ttl

   # Add new content descriptor
   eng:content-descriptor-new-topic
     a curric:ContentDescriptor ;
     skos:prefLabel "New Topic"@en ;
     skos:definition "Description of new topic"@en .

   # Link to scheme
   eng:scheme-science-key-stage-3
     curric:hasContent eng:content-descriptor-new-topic .
   ```

2. **Validate changes**
   ```bash
   ./scripts/validate.sh
   ```

3. **Test locally**
   ```bash
   # Regenerate JSON
   ./scripts/build-static-data.sh

   # Check output
   cat static/api/subjects/science-ks3.json | jq '.results.bindings[] | select(.label.value == "New Topic")'

   # Test in static site
   cd static-site
   npm run dev
   # Browse to /subjects/science/ks3 and verify new content appears
   ```

4. **Test SPARQL endpoint**
   ```bash
   # Rebuild Fuseki container
   docker build -t fuseki-local deployment/
   docker run -p 3030:3030 fuseki-local

   # Query for new content
   curl -X POST \
     -H "Content-Type: application/sparql-query" \
     -H "Accept: application/json" \
     --data 'SELECT * WHERE { ?s skos:prefLabel "New Topic"@en }' \
     http://localhost:3030/uk-curriculum/sparql
   ```

5. **Commit and push**
   ```bash
   git add data/national-curriculum-for-england/subjects/science/science-schemes.ttl
   git commit -m "Add new Science KS3 topic"
   git push origin main
   ```

6. **Automatic deployment**
   - GitHub Actions triggers
   - Validates data
   - Generates JSON files
   - Deploys website
   - Deploys Fuseki
   - Takes ~5-10 minutes

---

### Adding a New Subject

**Scenario:** Add Mathematics to the curriculum

**Steps:**

1. **Create subject files**
   ```bash
   mkdir -p data/national-curriculum-for-england/subjects/mathematics

   # Create files
   touch data/national-curriculum-for-england/subjects/mathematics/mathematics-subject.ttl
   touch data/national-curriculum-for-england/subjects/mathematics/mathematics-knowledge-taxonomy.ttl
   touch data/national-curriculum-for-england/subjects/mathematics/mathematics-schemes.ttl
   ```

2. **Define subject**
   ```turtle
   # mathematics-subject.ttl
   @prefix eng: <https://w3id.org/uk/curriculum/england/> .
   @prefix curric: <https://w3id.org/uk/curriculum/core/> .
   @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

   eng:mathematics
     a curric:Subject ;
     skos:prefLabel "Mathematics"@en ;
     skos:definition "The study of numbers, shapes, and patterns"@en .
   ```

3. **Create knowledge taxonomy**
   ```turtle
   # mathematics-knowledge-taxonomy.ttl
   # Define strands, sub-strands, content descriptors...
   ```

4. **Create schemes**
   ```turtle
   # mathematics-schemes.ttl
   eng:scheme-mathematics-key-stage-3
     a curric:Scheme ;
     skos:prefLabel "Mathematics Key Stage 3"@en ;
     curric:hasSubject eng:mathematics ;
     curric:hasKeyStage eng:key-stage-3 ;
     curric:hasContent eng:content-descriptor-algebra .
   ```

5. **Create query**
   ```sparql
   # queries/mathematics-ks3.sparql
   PREFIX curric: <https://w3id.org/uk/curriculum/core/>
   PREFIX eng: <https://w3id.org/uk/curriculum/england/>
   PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

   SELECT ?contentId ?label ?definition WHERE {
     ?scheme curric:hasSubject eng:mathematics ;
             curric:hasKeyStage eng:key-stage-3 ;
             curric:hasContent ?content .
     ?content skos:prefLabel ?label ;
              skos:definition ?definition .
     BIND(STRAFTER(STR(?content), "england/") AS ?contentId)
   }
   ORDER BY ?label
   ```

6. **Update build script**
   ```bash
   # Add to scripts/build-static-data.sh
   echo "📐 Generating Mathematics KS3..."
   arq $DATA_FILES \
       --query=queries/mathematics-ks3.sparql \
       --results=JSON > "$OUTPUT_DIR/subjects/mathematics-ks3.json"
   ```

7. **Add pages to website**
   ```typescript
   // static-site/pages/subjects/mathematics/ks3.tsx
   export default function MathematicsKS3() {
     // Load /api/subjects/mathematics-ks3.json
     // Render content
   }
   ```

8. **Test and deploy**
   ```bash
   ./scripts/validate.sh
   ./scripts/build-static-data.sh
   cd static-site && npm run build
   git add . && git commit -m "Add Mathematics subject"
   git push
   ```

---

## Cost Estimates

### Monthly Costs (Steady State)

| Component | Service | Usage | Cost |
|-----------|---------|-------|------|
| **Static Website** | Vercel Free Tier | < 100GB bandwidth | **$0** |
| **Alternative** | Cloud Storage + CDN | 100GB bandwidth | **$5-10** |
| **SPARQL Endpoint** | Cloud Run | 1M requests, 2GB RAM | **$15-25** |
| **Container Registry** | GCR | < 1GB storage | **$0.026** |
| **Domain** | Google Domains | curriculum.education.gov.uk | **$12/year** |
| **SSL Certificates** | Let's Encrypt / GCP | Automatic | **$0** |
| **GitHub Actions** | Public repo | Unlimited minutes | **$0** |
| **Total** | | | **~$15-35/month** |

### Cost Breakdown: SPARQL Endpoint

**Assumptions:**
- 1,000 queries per day (30k/month)
- Average query: 200ms
- 2GB memory, 2 vCPU

**Cloud Run Pricing:**
```
vCPU-seconds: 30,000 queries × 0.2s × 2 vCPU = 12,000 vCPU-seconds
  = 3.33 vCPU-hours
  Cost: 3.33 × $0.024 = $0.08

Memory (GB-seconds): 30,000 × 0.2s × 2GB = 12,000 GB-seconds
  = 3.33 GB-hours
  Cost: 3.33 × $0.0025 = $0.008

Requests: 30,000 requests
  Cost: 30,000 × $0.0000004 = $0.012

Monthly total: ~$0.10
```

**With realistic load (includes cold starts, overhead):**
- Low traffic (1k queries/day): **$10-15/month**
- Medium traffic (10k queries/day): **$20-30/month**
- High traffic (100k queries/day): **$100-150/month**

**Optimization:** Set `--min-instances=1` to avoid cold starts (adds ~$10/month)

---

### Scaling Costs

| Traffic Level | Queries/Day | Static Site | SPARQL | Total |
|--------------|-------------|-------------|--------|-------|
| **Launch** | 1,000 | $0 | $10 | **$10/mo** |
| **Growth** | 10,000 | $0 | $25 | **$25/mo** |
| **Established** | 100,000 | $5 | $150 | **$155/mo** |
| **High Scale** | 1,000,000 | $50 | $500 | **$550/mo** |

**Note:** Most curriculum websites operate at "Launch" or "Growth" levels.

---

## Maintenance & Operations

### Regular Maintenance Tasks

| Task | Frequency | Effort | Owner |
|------|-----------|--------|-------|
| **Update curriculum data** | Yearly | 2-4 hours | Curriculum team |
| **Review SPARQL queries** | Quarterly | 1 hour | Tech team |
| **Update dependencies** | Monthly | 30 minutes | Tech team |
| **Monitor usage** | Weekly | 15 minutes | Tech team |
| **Review costs** | Monthly | 15 minutes | Tech team |
| **Security updates** | As needed | 1 hour | Tech team |
| **Documentation updates** | Quarterly | 2 hours | Tech team |

---

### Monitoring

**What to Monitor:**

1. **Static Website**
   - Uptime (should be 99.9%+)
   - Page load times (should be < 1s)
   - Broken links
   - 404 errors

2. **SPARQL Endpoint**
   - Uptime (should be 99.5%+)
   - Query latency (P50, P95, P99)
   - Error rate (should be < 1%)
   - Request count
   - CPU and memory usage

**Tools:**

```bash
# Cloud Run metrics (via gcloud)
gcloud monitoring dashboards create \
  --config-from-file=monitoring/dashboard.json

# Uptime checks
gcloud monitoring uptime-checks create \
  --resource-type=url \
  --resource-url=https://sparql.curriculum.education.gov.uk/$/ping \
  --period=60s
```

**Alerts:**
- SPARQL endpoint down for > 5 minutes
- Error rate > 5%
- P95 latency > 2 seconds
- Daily cost > $5

---

### Backup & Disaster Recovery

**Data Backup:**
- Primary: Git repository (GitHub)
- Secondary: Automated daily backups to Cloud Storage
- Retention: 30 days

**Disaster Recovery:**

| Scenario | Recovery Time | Procedure |
|----------|---------------|-----------|
| **Website down** | 5 minutes | Re-deploy from GitHub |
| **SPARQL down** | 5 minutes | Re-deploy Cloud Run service |
| **Data corruption** | 1 hour | Restore from Git history |
| **Complete loss** | 4 hours | Re-deploy entire infrastructure from code |

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 0 (no data loss, everything in Git)

---

### Security

**Threat Model:**

| Threat | Mitigation | Status |
|--------|------------|--------|
| **DDoS attack** | Cloud Run auto-scaling + rate limiting | ✅ Implemented |
| **SQL injection** | Not applicable (SPARQL, read-only) | ✅ N/A |
| **XSS** | React escaping, CSP headers | ✅ Implemented |
| **Data exfiltration** | Data is public | ✅ N/A |
| **Malicious queries** | Query timeout (5 min), resource limits | ✅ Implemented |
| **Container vulnerabilities** | Regular base image updates | ⚠️ Manual |
| **Dependency vulnerabilities** | Dependabot alerts | ✅ Enabled |

**Security Updates:**
- Base Docker image: Update quarterly or when CVEs announced
- npm dependencies: Update monthly via `npm audit fix`
- Apache Jena: Update twice yearly or when security patches released

---

## Design Decisions & Rationale

### Decision 1: No CORS on SPARQL Endpoint

**Decision:** SPARQL endpoint does NOT include CORS headers

**Rationale:**
- Primary users are server-side applications (Python, Node.js, Java)
- Reduces risk of browser-based abuse
- Simpler security model
- Can add CORS later if needed without breaking changes

**Alternative Considered:** Enable CORS
- **Pros:** Browser-based tools work
- **Cons:** More vulnerable to abuse, need rate limiting
- **Conclusion:** Not needed for initial launch

---

### Decision 2: Client-Side Search vs Backend API

**Decision:** Use client-side search with full dataset download

**Rationale:**
- Dataset is small (~500KB compressed)
- Search is instant (0ms) after initial load
- No backend infrastructure needed
- Simpler architecture
- Lower costs
- More reliable (fewer failure points)

**Alternative Considered:** Backend search API
- **Pros:** No large download, can do complex SPARQL
- **Cons:** Network latency, more infrastructure, higher cost
- **Conclusion:** Over-engineered for this use case

---

### Decision 3: Static Site Generation vs Server-Side Rendering

**Decision:** Generate static HTML/JSON at build time

**Rationale:**
- Curriculum changes infrequently (yearly)
- Static files are fastest for users
- Zero runtime compute costs
- Perfect for CDN caching
- Great SEO
- Works without JavaScript

**Alternative Considered:** Server-side rendering (SSR)
- **Pros:** Always up-to-date, dynamic content
- **Cons:** Need server, slower, more expensive
- **Conclusion:** Not needed for stable data

---

### Decision 4: TDB2 in-container vs External Database

**Decision:** Load data into TDB2 database inside Docker container at build time

**Rationale:**
- Data is immutable (baked into container)
- Fast startup (data pre-loaded)
- No external database to manage
- Simpler deployment
- Versioned deployments (rollback = deploy old container)

**Alternative Considered:** External database (Cloud SQL, etc.)
- **Pros:** Can update data without redeployment
- **Cons:** More expensive, more complex, slower queries
- **Conclusion:** Not needed; data changes are infrequent and should be versioned

---

### Decision 5: Vercel vs Cloud Storage for Static Site

**Decision:** Recommend Vercel, but support Cloud Storage as alternative

**Rationale:**
- Vercel: Easiest deployment, great DX, free tier sufficient
- Cloud Storage: Lower cost at scale, more control
- Both are good options depending on needs

**Alternative Considered:** GitHub Pages
- **Pros:** Free, integrated with GitHub
- **Cons:** Limited features, no CDN in UK, slower
- **Conclusion:** Not recommended for production

---

### Decision 6: Apache Jena over GraphDB/Blazegraph

**Decision:** Use Apache Jena Fuseki as SPARQL endpoint

**Rationale:**
- Industry standard, proven reliability
- Excellent documentation
- Active development
- Good performance for this data size
- Free and open source

**Alternatives Considered:**
- **GraphDB:** More features, better for large scale
  - **Cons:** Commercial license, overkill for this use
- **Blazegraph:** Good performance
  - **Cons:** Development less active, community smaller
- **Conclusion:** Jena is best fit for this project

---

## Appendix

### Example SPARQL Queries

See `../user-guide/sparql-examples.md` for comprehensive query examples.

### JSON Schema

See `docs/json-schema.md` for static JSON file format specifications.

### API Documentation

See `docs/api.md` for complete API documentation.

### Glossary

- **SPARQL:** Query language for RDF data (like SQL for relational databases)
- **RDF:** Resource Description Framework (W3C standard for semantic web)
- **Turtle (TTL):** Human-readable format for RDF data
- **SHACL:** Shapes Constraint Language (validation for RDF)
- **TDB2:** Apache Jena's native triple store database
- **SSG:** Static Site Generation
- **CDN:** Content Delivery Network
- **CORS:** Cross-Origin Resource Sharing

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-15 | Claude + Mark | Initial comprehensive architecture |

---

**END OF DOCUMENT**
