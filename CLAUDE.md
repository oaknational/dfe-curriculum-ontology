# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a semantic web ontology for the UK Curriculum, specifically providing comprehensive coverage of the National Curriculum for England. It uses RDF/OWL standards with SHACL validation and provides both TTL files for semantic web usage and a deployable Fuseki SPARQL endpoint.

**Core Technologies:**
- RDF 1.1 / OWL 2 / SKOS for ontology structure
- Turtle (.ttl) format for all data files
- SHACL for validation constraints
- Apache Jena Fuseki 5.1.0 for SPARQL endpoints
- Apache Jena TDB2 for persistent RDF storage
- Python (rdflib, pyshacl) for validation tooling
- Docker for containerization
- Google Cloud Run for deployment

## Naming Convention

**Service:** `national-curriculum-for-england`
- **Why:** Matches directory structure; DfE requirement to be specific; aligns with official name
- **Applied to:** Docker images, Fuseki service name, database paths, Cloud Run service
- **Production Deployment:**
  - GCP Project: `oak-ai-playground`
  - Region: `europe-west1` (Belgium - cost-optimized over europe-west2)
  - Image: `gcr.io/oak-ai-playground/national-curriculum-for-england-fuseki:latest`
  - Service: `national-curriculum-for-england-sparql`
  - URL: `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app`
  - SPARQL Endpoint: `/national-curriculum-for-england/sparql`
  - Database: `/data/national-curriculum-for-england-tdb2`

## Repository Structure

```
uk-curriculum-ontology/
├── ontology/                              # Core ontology definitions
│   ├── dfe-curriculum-ontology.ttl       # Classes and properties
│   ├── dfe-curriculum-constraints.ttl    # SHACL validation shapes
│   └── versions/                          # Versioned releases
├── data/national-curriculum-for-england/  # Curriculum data
│   ├── programme-structure.ttl            # Phases, Key Stages, Year Groups
│   └── subjects/                          # Subject-specific content
│       ├── science/
│       ├── history/
│       └── ...
├── scripts/
│   ├── validate.sh                        # Local validation (matches CI)
│   └── merge_ttls.py                      # Merge TTL files for validation
├── deployment/
│   ├── Dockerfile                         # Fuseki container
│   ├── fuseki-config.ttl                  # Fuseki configuration
│   └── deploy.sh                          # Deployment script
├── .github/workflows/
│   ├── validate-ontology.yml              # CI validation
│   └── deploy-fuseki.yml                  # CD to Cloud Run
└── docs/                                   # Documentation
```

## Data Architecture

The ontology is organized into three main hierarchies:

1. **Temporal Hierarchy**: Phase → KeyStage → YearGroup (age-based progression)
2. **Programme Hierarchy**: Subject → SubSubject → Scheme (how subjects are organized)
3. **Knowledge Taxonomy**: Subject → Strand → SubStrand → ContentDescriptor → ContentSubDescriptor

A **Scheme** connects temporal and knowledge hierarchies by specifying which content descriptors are taught at which key stage.

## Environment Setup

### Apache Jena Installation

**macOS (Manual Installation Recommended):**
```bash
# Download pre-built binaries
cd ~/Downloads
# Download from: https://archive.apache.org/dist/jena/binaries/apache-jena-4.10.0.tar.gz
tar -xzf apache-jena-4.10.0.tar.gz
sudo mv apache-jena-4.10.0 /usr/local/
echo 'export PATH="/usr/local/apache-jena-4.10.0/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Why manual installation?**
- Homebrew requires full Xcode installation (~12GB)
- Manual installation avoids this dependency
- Pre-built binaries work identically

### Python Environment

Project uses Python 3.12+ with virtual environment at `.venv/`:
```bash
# Virtual environment already configured with:
# - pyshacl 0.30.1
# - rdflib 7.5.0
.venv/bin/python --version
.venv/bin/pyshacl --version
```

## Common Commands

### Validation

**Local validation (matches CI exactly):**
```bash
./scripts/validate.sh
```

This command:
1. Runs `python3 scripts/merge_ttls.py` to merge all TTL files from `ontology/` and `data/`
2. Runs SHACL validation using pyshacl
3. Outputs human-readable validation results

### Testing SPARQL Queries

**Test queries against local Fuseki:**
```bash
# Use --data-binary with file references to handle comments in SPARQL
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/json" \
  --data-binary @queries/your-query.sparql \
  http://localhost:3030/national-curriculum-for-england/sparql | jq .
```

### Working with TTL Files

**Important file naming conventions:**
- Ontology files use hyphenated names: `dfe-curriculum-ontology.ttl`, `dfe-curriculum-constraints.ttl`
- But the validation script references: `curriculum-ontology.ttl`, `curriculum-constraints.ttl`
- The actual files in the repo use the `dfe-` prefix

**RDF Property Patterns (CRITICAL for SPARQL queries):**

**Subject entities** use RDFS properties:
- `curric:Subject`, `curric:SubSubject`, `curric:Scheme`
- Label: `rdfs:label` (required, SHACL constrained)
- Description: `rdfs:comment`
- Example: `eng:subject-science rdfs:label "Science"@en`

**SKOS Concepts** use SKOS properties:
- `curric:Discipline`, `curric:Strand`, `curric:ContentDescriptor`
- Label: `skos:prefLabel` (required, SHACL constrained)
- Description: `skos:definition` (optional)
- Example: `eng:content-descriptor-cells skos:prefLabel "Cells..."@en`

See SHACL constraints at:
- Subject entities: `dfe-curriculum-constraints.ttl:283-289`
- SKOS Concepts: `dfe-curriculum-constraints.ttl:479+`

**Check TTL syntax:**
```python
python3 -c "from rdflib import Graph; g = Graph(); g.parse('path/to/file.ttl', format='turtle')"
```

### Deployment

**Build and run Fuseki locally:**
```bash
docker build -t fuseki-local -f deployment/Dockerfile .
docker run -p 3030:3030 fuseki-local
# Access at: http://localhost:3030/national-curriculum-for-england/sparql
```

**Deploy to Cloud Run:**
```bash
./deployment/deploy.sh
# Automatically builds, pushes to GCR, deploys, and tests
```

**Manual deployment steps (see deployment/DEPLOY.md for full guide):**
```bash
export PROJECT_ID="oak-ai-playground"
export REGION="europe-west1"
export IMAGE="gcr.io/${PROJECT_ID}/national-curriculum-for-england-fuseki"

# Build, push, deploy
docker build -t ${IMAGE}:latest -f deployment/Dockerfile .
docker push ${IMAGE}:latest
gcloud run deploy national-curriculum-for-england-sparql \
  --image=${IMAGE}:latest \
  --region=${REGION} \
  --memory=2Gi --cpu=2 --port=3030
```

**Production endpoint:** `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql`

## Validation Details

### SHACL Validation Process

The validation happens in two stages:

1. **Syntax Check** (`validate-ontology.yml` job 1):
   - Uses rdflib to parse all .ttl files
   - Ensures Turtle syntax is valid
   - Fast feedback on syntax errors

2. **SHACL Validation** (`validate-ontology.yml` job 2):
   - Merges all TTL files into single graph (`/tmp/combined-data.ttl`)
   - Validates against SHACL shapes in `ontology/dfe-curriculum-constraints.ttl`
   - Uses ontology graph from `ontology/dfe-curriculum-ontology.ttl`
   - Runs with RDFS inference enabled
   - Uses `--abort` flag to fail on first violation

### Expected Validation Behavior

The merge script (`scripts/merge_ttls.py`):
- Auto-discovers all .ttl files in `ontology/` and `data/` directories
- Skips files in `versions/` subdirectories
- Checks for `owl:imports` declarations and warns about external imports
- Creates combined graph at `/tmp/combined-data.ttl`

**Note on file references:** The validation script in `.github/workflows/validate-ontology.yml` uses these paths:
- `--shacl ontology/dfe-curriculum-constraints.ttl`
- `--ont-graph ontology/dfe-curriculum-ontology.ttl`

However, the local `scripts/validate.sh` references:
- `--shacl ontology/curriculum-constraints.ttl`
- `--ont-graph ontology/curriculum-ontology.ttl`

**This is a known inconsistency** - the actual files use the `dfe-` prefix.

## Working with Subjects

When adding a new subject (e.g., Mathematics):

1. Create directory: `data/national-curriculum-for-england/subjects/mathematics/`
2. Create these files:
   - `mathematics-subject.ttl` - Subject definitions
   - `mathematics-knowledge-taxonomy.ttl` - Strands, SubStrands, ContentDescriptors
   - `mathematics-schemes.ttl` - Scheme definitions linking content to key stages

3. Follow the existing pattern from Science or History subjects

4. Validate:
```bash
./scripts/validate.sh
```

## Namespace Strategy

**Current (temporary):**
- Core ontology: `https://w3id.org/uk/curriculum/core/`
- England data: `https://w3id.org/uk/curriculum/england/`

**Future vision:**
- Core ontology will move to: `curriculum.education.gov.uk`
- Maintained by Department for Education with URI persistence

## CI/CD Pipeline

### Validation Workflow (`.github/workflows/validate-ontology.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual dispatch
- Only when TTL files or workflow files change

**Jobs:**
1. `syntax-check`: Validates Turtle syntax with rdflib
2. `shacl-validation`: Runs SHACL validation with pyshacl

### Deployment Workflow (`.github/workflows/deploy-fuseki.yml`)

**Triggers:**
- GitHub releases (published)
- Manual dispatch

**Process:**
1. Builds Docker container with all TTL files
2. Pushes to Google Container Registry
3. Deploys to Cloud Run in europe-west2
4. Service runs on port 3030

**Required Secrets:**
- `GCP_SA_KEY`: Service account key JSON
- `GCP_PROJECT_ID`: GCP project ID

## Important Architectural Decisions

### Generated Files Are NOT Committed

The repository follows "Approach 1" from the implementation plan:
- Static JSON files are generated at build time
- `distributions/` directory is gitignored
- Generated files are published via GitHub Releases
- This keeps the repository focused on source data

### Fuseki Container Configuration

The Dockerfile uses **TDB2 storage** (`tdb2:DatasetTDB2`) with data pre-loaded at build time:
- **Data location**: `/data/national-curriculum-for-england-tdb2` (outside `/fuseki` VOLUME, baked into container)
- **Loader**: `java -cp fuseki-server.jar tdb2.tdbloader` (TDB2, not TDB1)
- **Read-only endpoints**: SPARQL query (`/sparql`, `/query`) and Graph Store Protocol (`/get`)
- **Fast startup**: TDB2 indexes pre-built (no loading phase)
- **Immutable deployments**: To update data, rebuild and redeploy the container

**Configuration file**: `deployment/fuseki-config.ttl`

**Critical Notes:**
- Do NOT use `tdb2:unionDefaultGraph true` - prevents dataset from being readable
- Data must be in `/data/` not `/fuseki-base/` (which is a VOLUME and won't persist)
- Use `.dockerignore` to exclude `**/versions/` (archived TTL files)

### File Name Inconsistencies

There are inconsistencies between:
- Actual file names: `dfe-curriculum-ontology.ttl`, `dfe-curriculum-constraints.ttl`
- Script references in `validate.sh`: `curriculum-ontology.ttl`, `curriculum-constraints.ttl`

When editing scripts or workflows, verify the actual filenames in the `ontology/` directory.

## Development Workflow

### Adding New Content

1. Edit or create TTL files in appropriate location
2. Validate locally: `./scripts/validate.sh`
3. Commit changes
4. CI will run validation automatically
5. If validation passes, merge to main
6. Create a release to trigger deployment

### Testing SPARQL Queries

Against local Fuseki:
```bash
docker run -p 3030:3030 fuseki-local
curl -X POST http://localhost:3030/uk-curriculum/sparql \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/json" \
  --data "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
```

### Versioning

Follows Semantic Versioning:
- **Major (1.x.x)**: Breaking changes to ontology structure
- **Minor (x.1.x)**: New subjects, properties, or data (backward compatible)
- **Patch (x.x.1)**: Bug fixes, corrections (backward compatible)

Current version: **0.1.0**

## Troubleshooting

### Apache Jena Commands Not Found

If `riot`, `arq`, or `tdbloader` are not found:
1. Check installation: `ls /usr/local/apache-jena-4.10.0/bin/`
2. Check PATH: `echo $PATH | grep jena`
3. Export manually: `export PATH="/usr/local/apache-jena-4.10.0/bin:$PATH"`
4. Open new terminal (PATH in `~/.zshrc` applies to new sessions only)

### Validation Fails Locally But Not in CI (or vice versa)

Check:
1. File names match between script and actual files
2. Python version (CI uses 3.11)
3. Package versions (pyshacl, rdflib)
4. Run merge script separately: `python3 scripts/merge_ttls.py`

### Docker Build Fails

Check:
1. Dockerfile references correct TTL filenames
2. All referenced files exist in the ontology directory
3. Fuseki config references correct file paths

### SHACL Validation Errors

Check:
1. All required properties are present (check constraints.ttl)
2. URIs are properly formed and consistent
3. Data types match expected types
4. Cardinality constraints are satisfied

Use `--format human` in pyshacl for readable error messages (already default in validation script).

## Key Files Reference

- `ontology/dfe-curriculum-ontology.ttl` - Core class and property definitions
- `ontology/dfe-curriculum-constraints.ttl` - SHACL validation shapes
- `scripts/validate.sh` - Local validation script
- `scripts/merge_ttls.py` - TTL file merger with import checking
- `deployment/Dockerfile` - Fuseki container definition
- `ARCHITECTURE.md` - Complete architecture documentation
- `IMPLEMENTATION-PLAN.md` - Detailed implementation steps
- `README.md` - User-facing documentation

## Additional Documentation

- See `ARCHITECTURE.md` for complete system architecture
- See `IMPLEMENTATION-PLAN.md` for 28-step implementation guide
- See `docs/` directory for:
  - `model.md` - Conceptual model details
  - `examples.md` - SPARQL query examples
  - `validation.md` - Validation guide
  - `extending.md` - How to extend the ontology
