# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

A semantic web ontology for the National Curriculum for England, providing:
- RDF/OWL ontology with SHACL validation
- SPARQL endpoint for querying curriculum data
- Static JSON files for web applications
- Comprehensive data model for Phases, Key Stages, Subjects, and Content Descriptors

**Technologies:**
- RDF 1.1 / OWL 2 / SKOS
- Turtle (.ttl) format
- SHACL validation
- Apache Jena (4.10.0+) - validation and JSON generation
- Apache Jena Fuseki (5.1.0) - SPARQL endpoint
- TDB2 - persistent RDF storage
- Python (rdflib, pyshacl) - validation
- Docker - containerization
- Google Cloud Run - deployment

**Current Version:** 0.1.0

## Naming Conventions

**Service Name:** `national-curriculum-for-england`
- Matches directory structure
- Specific to England (DfE requirement)
- Used consistently across: Docker images, Fuseki datasets, database paths, Cloud Run services

**Production Deployment:**
- GCP Project: `oak-ai-playground`
- Region: `europe-west1` (Belgium)
- Image: `gcr.io/oak-ai-playground/national-curriculum-for-england-fuseki:latest`
- Service: `national-curriculum-for-england-sparql`
- URL: `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app`
- SPARQL Endpoint: `/national-curriculum-for-england/sparql`
- Database: `/data/national-curriculum-for-england-tdb2`

## Repository Structure

```
uk-curriculum-ontology/
├── README.md                          # Main entry point
├── CHANGELOG.md                       # Version history
├── CLAUDE.md                          # This file
│
├── ontology/
│   ├── dfe-curriculum-ontology.ttl       # Core classes and properties
│   ├── dfe-curriculum-constraints.ttl    # SHACL validation shapes
│   └── versions/                          # Archived versions
│
├── data/national-curriculum-for-england/
│   ├── programme-structure.ttl            # Phases, Key Stages, Year Groups
│   ├── themes.ttl                         # Cross-cutting themes
│   └── subjects/                          # Subject data
│       ├── science/
│       │   ├── science-subject.ttl
│       │   ├── science-knowledge-taxonomy.ttl
│       │   └── science-schemes.ttl
│       └── history/
│
├── queries/
│   ├── subjects-index.sparql              # List all subjects
│   ├── science-ks3.sparql                 # Science KS3 content
│   └── full-curriculum.sparql             # Complete dataset
│
├── scripts/
│   ├── validate.sh                        # SHACL validation
│   ├── merge_ttls.py                      # Merge TTL files
│   └── build-static-data.sh               # Generate JSON files
│
├── deployment/
│   ├── Dockerfile                         # Fuseki container
│   ├── fuseki-config.ttl                  # Fuseki configuration
│   └── deploy.sh                          # Cloud Run deployment
│
├── docs/
│   ├── user-guide/
│   │   ├── README.md
│   │   ├── data-model.md                  # Curriculum structure
│   │   ├── sparql-examples.md             # Query examples
│   │   ├── api-examples.md                # SPARQL endpoint usage
│   │   └── validation.md                  # Validation guide
│   │
│   └── deployment/
│       ├── README.md
│       ├── architecture.md                # System architecture
│       ├── building.md                    # Build process
│       ├── deploying.md                   # Cloud deployment
│       ├── releasing.md                   # Release process
│       ├── extending.md                   # Adding content
│       └── github-actions.md              # CI/CD setup
│
└── distributions/                         # Generated (gitignored)
    ├── subjects/
    │   ├── index.json
    │   └── science-ks3.json
    └── curriculum-full.json
```

## Environment Setup

### Apache Jena Installation (macOS)

```bash
# Download from https://archive.apache.org/dist/jena/binaries/apache-jena-4.10.0.tar.gz
tar -xzf apache-jena-4.10.0.tar.gz
sudo mv apache-jena-4.10.0 /usr/local/

# Add to both zshenv (non-interactive) and zshrc (interactive)
echo 'export PATH="/usr/local/apache-jena-4.10.0/bin:$PATH"' >> ~/.zshenv
echo 'export PATH="/usr/local/apache-jena-4.10.0/bin:$PATH"' >> ~/.zshrc
source ~/.zshenv
```

**Why both files?**
- `~/.zshenv` - Loaded by ALL zsh sessions (scripts, automation)
- `~/.zshrc` - Loaded by interactive sessions (your terminal)

### Python Environment

Virtual environment at `.venv/`:
```bash
.venv/bin/python --version  # Python 3.12+
.venv/bin/pyshacl --version # pyshacl 0.30.1
```

## Common Commands

### Validation

```bash
./scripts/validate.sh
```

This command:
1. Merges all TTL files from `ontology/` and `data/`
2. Runs SHACL validation with pyshacl
3. Outputs human-readable results

**Critical:** Uses correct file paths:
- `ontology/dfe-curriculum-ontology.ttl` (NOT `curriculum-ontology.ttl`)
- `ontology/dfe-curriculum-constraints.ttl` (NOT `curriculum-constraints.ttl`)

### Generate JSON Files

```bash
./scripts/build-static-data.sh
```

Creates `distributions/` with:
- `subjects/index.json` - All subjects
- `subjects/science-ks3.json` - Science KS3 content
- `curriculum-full.json` - Complete curriculum

**Output:** ~36KB in 3 files (gitignored)

### Build and Test Fuseki Locally

```bash
docker build -t fuseki-local -f deployment/Dockerfile .
docker run -p 3030:3030 fuseki-local

# Test
curl http://localhost:3030/$/ping
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/json" \
  --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
  http://localhost:3030/national-curriculum-for-england/sparql | jq .
```

### Deploy to Cloud Run

```bash
./deployment/deploy.sh
```

Automatically builds, pushes to GCR, deploys to Cloud Run, and tests.

## RDF Property Patterns (CRITICAL)

Different entity types use different property patterns:

### Subject Entities
Classes: `curric:Subject`, `curric:SubSubject`, `curric:Scheme`

**Properties:**
- Label: `rdfs:label` (required)
- Description: `rdfs:comment` (optional)

**Example:**
```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?label WHERE {
  ?subject a curric:Subject ;
           rdfs:label ?label .
}
```

### SKOS Concepts
Classes: `curric:Discipline`, `curric:Strand`, `curric:SubStrand`, `curric:ContentDescriptor`, `curric:ContentSubDescriptor`

**Properties:**
- Label: `skos:prefLabel` (required)
- Description: `skos:definition` (optional)

**Example:**
```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?descriptor ?label WHERE {
  ?descriptor a curric:ContentDescriptor ;
              skos:prefLabel ?label .
}
```

**Why this matters:** Using the wrong property pattern will cause queries to fail. SHACL constraints enforce these patterns.

## Data Architecture

The ontology has three main hierarchies:

1. **Temporal Hierarchy**: Phase → KeyStage → YearGroup (age-based progression)
2. **Programme Hierarchy**: Subject → SubSubject → Scheme (how subjects are organized)
3. **Knowledge Taxonomy**: Subject → Strand → SubStrand → ContentDescriptor → ContentSubDescriptor

A **Scheme** connects temporal and knowledge hierarchies by specifying which content descriptors are taught at which key stage.

## Deployment Architecture

### Fuseki Container

- **Storage:** TDB2 (`tdb2:DatasetTDB2`)
- **Data location:** `/data/national-curriculum-for-england-tdb2` (baked into image, outside VOLUME)
- **Loader:** `java -cp fuseki-server.jar tdb2.tdbloader` (TDB2, not TDB1)
- **Endpoints:** Read-only SPARQL (`/sparql`, `/query`) and Graph Store Protocol (`/get`)
- **Updates:** Rebuild and redeploy container (immutable deployments)

**Configuration:** `deployment/fuseki-config.ttl`

**Critical Notes:**
- DO NOT use `tdb2:unionDefaultGraph true` - prevents dataset from being readable
- Data must be in `/data/` not `/fuseki-base/` (which is a VOLUME)
- Use `.dockerignore` to exclude `**/versions/` directories

### GitHub Actions Workflows

**Validation** (`.github/workflows/validate-ontology.yml`):
- Triggers: Push to main/develop, PRs to main, manual
- Jobs: Syntax check + SHACL validation

**JSON Generation** (`.github/workflows/generate-json.yml`):
- Triggers: Push to main, releases
- Output: Artifacts (30-day retention)

**Fuseki Deployment** (`.github/workflows/deploy-fuseki.yml`):
- Triggers: Releases, manual
- Process: Build → Push to GCR → Deploy to Cloud Run → Test
- **Status:** Requires GCP secrets (see `docs/deployment/github-actions.md`)

## Terminology (IMPORTANT)

**Correct terminology:**
- "SPARQL endpoint" (NOT "REST API")
- "Static JSON files" (NOT "JSON API")
- "Pre-generated JSON downloads" (NOT "static API")

**What this project has:**
1. SPARQL HTTP endpoint (SPARQL Protocol)
2. Pre-generated static JSON files (downloads from GitHub Releases)
3. Graph Store Protocol (read-only)

**What this project does NOT have:**
- REST API (no resource-based endpoints like `/api/subjects`)

## File Naming

**Ontology files:**
- `dfe-curriculum-ontology.ttl` (NOT `curriculum-ontology.ttl`)
- `dfe-curriculum-constraints.ttl` (NOT `curriculum-constraints.ttl`)

**Subject files pattern:**
- `{subject}-subject.ttl` - Subject and SubSubject definitions
- `{subject}-knowledge-taxonomy.ttl` - Strands, SubStrands, ContentDescriptors
- `{subject}-schemes.ttl` - Schemes linking content to key stages

## Adding New Subjects

1. Create directory: `data/national-curriculum-for-england/subjects/{subject}/`
2. Create files:
   - `{subject}-subject.ttl`
   - `{subject}-knowledge-taxonomy.ttl`
   - `{subject}-schemes.ttl`
3. Follow patterns from existing subjects (science, history)
4. Validate: `./scripts/validate.sh`

## Troubleshooting

### arq/riot commands not found

Check PATH:
```bash
which arq
# Should return: /usr/local/apache-jena-4.10.0/bin/arq

# If not found, check installation
ls /usr/local/apache-jena-4.10.0/bin/

# Re-export PATH (for current session)
export PATH="/usr/local/apache-jena-4.10.0/bin:$PATH"
```

### Validation fails

1. Check file paths use `dfe-` prefix
2. Check Python version (requires 3.11+)
3. Run merge script separately: `python3 scripts/merge_ttls.py`
4. Check SHACL constraints in `dfe-curriculum-constraints.ttl`

### Docker build fails

1. Check Dockerfile references correct filenames
2. Verify all TTL files parse: `riot --validate file.ttl`
3. Check `.dockerignore` excludes `**/versions/`

### Queries return no results

1. Check property patterns (rdfs:label vs skos:prefLabel)
2. Verify correct URIs (e.g., `eng:subject-science` not `eng:science`)
3. Test with simple COUNT query first

## Key Documentation

- **README.md** - Main entry point, user-facing
- **docs/user-guide/** - For data consumers
  - data-model.md - Curriculum structure
  - sparql-examples.md - Query patterns
  - api-examples.md - SPARQL endpoint usage
- **docs/deployment/** - For DfE staff/operators
  - architecture.md - System architecture
  - building.md - Build process
  - deploying.md - Cloud deployment
  - releasing.md - Release process
  - extending.md - Adding content

## Standards

- **Semantic Versioning** (https://semver.org/)
  - Major: Breaking changes to ontology structure
  - Minor: New subjects, properties, data (backward compatible)
  - Patch: Bug fixes, corrections (backward compatible)
- **RDF 1.1** (https://www.w3.org/TR/rdf11-primer/)
- **OWL 2** (https://www.w3.org/TR/owl2-overview/)
- **SKOS** (https://www.w3.org/TR/skos-reference/)
- **SHACL** (https://www.w3.org/TR/shacl/)

## Development Workflow

1. Make changes to TTL files
2. Validate locally: `./scripts/validate.sh`
3. Test JSON generation: `./scripts/build-static-data.sh`
4. Test Fuseki locally: Docker build and test
5. Commit changes
6. CI validates automatically
7. Create release to trigger deployment

## Namespace URIs

**Current (temporary):**
- Core ontology: `https://w3id.org/uk/curriculum/core/`
- England data: `https://w3id.org/uk/curriculum/england/`

**Future vision:**
- `curriculum.education.gov.uk` - DfE-owned with URI persistence
