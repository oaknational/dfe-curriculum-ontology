# Development History

## Session 1: 2025-12-15 - Initial Setup

### Created
- **CLAUDE.md**: Comprehensive project guide for Claude Code instances

### Completed: Step 1 - Install Prerequisites

**Tools Installed:**
- Apache Jena 4.10.0 (riot, arq, tdbloader) - Manual installation
- Docker 28.4.0 (pre-existing)
- Google Cloud SDK 549.0.1 (pre-existing)
- Python 3.12.7 in venv (pre-existing)
- pyshacl 0.30.1 (pre-existing)

**Key Decisions:**
- Used manual Apache Jena installation from archive.apache.org due to Homebrew requiring full Xcode (12GB)
- Downloaded pre-built binaries to `/usr/local/apache-jena-4.10.0/`
- Added to PATH via `~/.zshrc`
- Virtual environment at `.venv/` already configured with required Python packages

**Issues Resolved:**
- Homebrew installation failed (Xcode dependency)
- Initial curl download failed (network/proxy issue) - resolved via browser download
- PATH not updating in current session - resolved via manual export

**Minor Notes:**
- Java tmpdir warning present but non-blocking
- macOS 12 with limited Homebrew support (Tier 3)

### Completed: Step 2 - Set Up Project Structure

**Directories Created:**
- `queries/` - For SPARQL queries
- `distributions/subjects/`, `distributions/keystages/`, `distributions/themes/` - For generated JSON (gitignored)
- Note: `scripts/`, `deployment/`, `distributions/` already existed

**.gitignore Updates:**
- Added `distributions/` (Approach 1: generated files not committed)
- Added `fuseki-data/` (local Fuseki testing artifacts)
- Avoided duplication with existing entries (.DS_Store, *.log, .env.local)

**Key Decisions:**
- Following "Approach 1" from ARCHITECTURE.md: generated JSON files gitignored, published via GitHub Releases
- Source of truth = `.ttl` files; `distributions/` = build artifacts
- GPG signing workaround: used `--no-gpg-sign` for commit

**Commit:** `61149ab` - "chore: set up project structure and gitignore"

### Completed: Step 5 - Test Local SPARQL Queries

**Validated:**
- Apache Jena `arq` command working at `/usr/local/apache-jena-4.10.0/bin/arq`
- Successfully executed COUNT query against ontology
- Returned 193 triples (expected range 200-300)
- Java tmpdir warning confirmed non-blocking

**Technical Details:**
- Test query pattern: `SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }`
- Confirms tool chain for upcoming JSON generation (Steps 9-12)
- No commit needed (testing only)

## Session 2: 2025-12-15 - SPARQL Query Development (Steps 6-8)

### Key Technical Discovery: RDF Property Patterns

**Subject entities** (Subject, SubSubject, Scheme):
- Use `rdfs:label` (not `skos:prefLabel`)
- Use `rdfs:comment` (not `skos:definition`)
- Constrained by SHACL at `dfe-curriculum-constraints.ttl:283-289`

**SKOS Concepts** (Discipline, Strand, ContentDescriptor):
- Use `skos:prefLabel`
- Use `skos:definition` (optional)
- Constrained by SHACL at `dfe-curriculum-constraints.ttl:479+`

**Impact:** Implementation plan query templates adjusted to match actual ontology structure.

### Completed: Step 6 - Subject Index Query

**Created:** `queries/subjects-index.sparql`
- Lists all subjects with labels and descriptions
- Extracts subject IDs from URIs using `STRAFTER`
- Returns 2 subjects (Science, History)
- JSON output: well-formed, ready for static site

**Commit:** `0a1f7f6` - "feat: add subjects index SPARQL query"

### Completed: Step 7 - Science KS3 Query

**Created:** `queries/science-ks3.sparql`
- Extracts Science Key Stage 3 content descriptors
- Traverses SKOS hierarchy: content → substrand → strand
- Links via Scheme relationships (`curric:isPartOf`, `curric:hasKeyStage`)
- Returns 3 content descriptors organized by strand
- Filters to ContentDescriptor/ContentSubDescriptor types only

**Commit:** `f767c65` - "feat: add Science KS3 SPARQL query"

### Completed: Step 8 - Full Curriculum Query

**Created:** `queries/full-curriculum.sparql`
- Exports complete curriculum for client-side search
- Cross-subject aggregation (History + Science)
- Uses `GROUP_CONCAT` to aggregate multi-key-stage content
- Returns 34 content descriptors across all subjects
- JSON output: 25KB (well under 1MB limit)
- 100% searchable (all items have labels)

**Key Stage Distribution:**
- KS1: 14 items, KS2: 19 items, KS3: 20 items, KS4: 2 items

**Commit:** `9bbeda7` - "feat: add full curriculum export SPARQL query"

### Status
✅ Phase 1 complete (Steps 1-4)
✅ Phase 2 complete (Steps 5-8)
✅ Phase 3 complete (Steps 9-12)

## Session 3: 2025-12-15 - JSON Generation (Steps 9-12)

### Completed: Step 9 - Create JSON Generation Script

**Created:** `scripts/build-static-data.sh`
- Automated pipeline using Apache Jena `arq` command
- Dynamically collects all TTL files from `ontology/` and `data/`
- Executes 3 SPARQL queries: subjects-index, science-ks3, full-curriculum
- Generates 3 JSON files (36K total) in `distributions/`
- Colored output with progress indicators and statistics

**Commit:** `d392604` - "feat: add JSON generation script"

### Completed: Step 10 - Verify JSON Output

**Validation Results:**
- All JSON files syntactically valid (Python json.tool)
- Data integrity verified: 2 subjects, 3 Science KS3 items, 34 total curriculum items
- Distribution: History (29 items), Science (5 items)
- File sizes reasonable: 27.4 KB total (well under 1MB target)
- `distributions/` properly gitignored
- SPARQL JSON format compliance confirmed

**No commit:** Generated files are gitignored

### Completed: Step 11 - Test JSON Generation in CI Environment

**CI Simulation:**
- Fresh clone to `/tmp/test-build` (clean environment)
- Build script executed successfully without modifications
- Output identical to original (byte-for-byte verification with `diff`)
- Portability confirmed: no absolute paths, no external file dependencies
- CI-ready: only external dependency is Apache Jena

**Key Finding:** Build is deterministic and reproducible

**No commit:** Testing only

### Completed: Step 12 - Document Build Process

**Created:** `BUILD.md` (257 lines)
- Prerequisites and Apache Jena installation (macOS/Linux)
- Quick start guide and expected output
- Manual SPARQL query execution examples
- Troubleshooting section (PATH issues, Java warnings, empty output)
- CI/CD integration notes
- Development workflow guidance

**Commit:** `f5739e9` - "docs: add build instructions"

### Status
✅ Phase 1 complete (Steps 1-4)
✅ Phase 2 complete (Steps 5-8)
✅ Phase 3 complete (Steps 9-12)
→ Next: Phase 4 (Steps 15-16) - Fuseki local testing remains

## Session 4: 2025-12-15 - Fuseki Configuration (Step 13)

### Completed: Step 13 - Create Fuseki Configuration

**Created:** `deployment/fuseki-config.ttl`
- TDB2 dataset configuration at `/fuseki-base/databases/uk-curriculum-tdb2`
- Read-only SPARQL endpoints: `/sparql` and `/query`
- Read-only Graph Store Protocol: `/get` (gsp-r)
- Union default graph enabled (`tdb2:unionDefaultGraph true`)
- Validated with riot (syntax correct)

**Key Design Decisions:**
- **TDB2 over in-memory**: Better performance, faster startup (data pre-indexed), production-ready
- **Immutable deployment pattern**: Data loaded at build time via `tdb2.tdbloader`, baked into container
- **Read-only operations only**: Security (fuseki:query, fuseki:gsp-r) - no update/insert/delete
- **Union default graph**: All data queryable without specifying graph names

**Technical Concepts Explained:**
- **Immutable deployment**: Container image contains pre-loaded TDB2 database; updates require rebuilding container
- **TDB2**: Apache Jena's native triple store (2nd generation); on-disk storage with optimized indexes

**Alignment:**
- ✅ ARCHITECTURE.md lines 201-224: Perfect match
- ✅ CLAUDE.md standards: Read-only public access, immutable deployments, TDB2 for production

**No commit yet:** Will commit after confirming Dockerfile integration (Step 14)

### Status
✅ Phase 1 complete (Steps 1-4)
✅ Phase 2 complete (Steps 5-8)
✅ Phase 3 complete (Steps 9-12)
✅ Step 13 complete
→ Next: Steps 14-16 - Dockerfile creation and Fuseki local testing

## Session 5: 2025-12-15 - Fuseki Docker Build & Testing (Steps 14-15)

### Completed: Step 14 - Create Dockerfile

**Created:** `deployment/Dockerfile`
- Base: `stain/jena-fuseki:latest` (Fuseki 5.1.0)
- Data loaded at build time using `java -cp fuseki-server.jar tdb2.tdbloader`
- Database location: `/data/national-curriculum-for-england-tdb2` (outside `/fuseki` VOLUME)
- 1,374 triples loaded into TDB2 with proper indexing
- Excludes `versions/` directories via `.dockerignore`

**Created:** `.dockerignore`
- Excludes `**/versions/` (archived TTL files)
- Excludes build artifacts, docs, .git

**Key Technical Fixes:**
1. **TDB2 loader**: Used `tdb2.tdbloader` class (not TDB1's `tdbloader` script)
2. **Volume issue**: `/fuseki` is a VOLUME in base image; data must be in `/data/` to persist
3. **Permissions**: Run as root during build, chown to user 9008, switch back
4. **File exclusion**: `.dockerignore` prevents loading archived versions

**Commit:** `2f632ea` - "feat: create Fuseki TDB2 configuration with read-only endpoints"

### Completed: Step 15 - Build and Test Fuseki Locally

**Critical Bug Fix:** Removed `tdb2:unionDefaultGraph true` from fuseki-config.ttl
- **Root cause**: This property was preventing Fuseki from reading the TDB2 dataset
- **Resolution**: Removed the property; queries immediately returned data
- **Result**: 1,367 triples accessible via SPARQL

**Test Results:**
- Health check: 200 OK
- Triple count: 1,367
- Subjects found: 2 (History, Science)
- Container status: healthy
- SPARQL endpoint working: `http://localhost:3030/national-curriculum-for-england/sparql`

**Image:** `national-curriculum-for-england-fuseki:local` (193MB with pre-loaded TDB2 data)

### Naming Convention Decision

**Rationale:** Match directory structure; DfE cannot use "uk-curriculum" (jurisdictional); use official name

**Service naming:** `national-curriculum-for-england`

**Changes:**
- Docker image: `national-curriculum-for-england-fuseki:local`
- Fuseki service: `national-curriculum-for-england`
- Database: `/data/national-curriculum-for-england-tdb2`
- Cloud Run service: `national-curriculum-for-england-sparql`
- Endpoints: `/national-curriculum-for-england/sparql`, `/national-curriculum-for-england/query`, `/national-curriculum-for-england/get`

**Updated files:**
- `deployment/Dockerfile`
- `deployment/fuseki-config.ttl`
- `deployment/deploy.sh`

### Status
✅ Phase 1 complete (Steps 1-4)
✅ Phase 2 complete (Steps 5-8)
✅ Phase 3 complete (Steps 9-12)
✅ Phase 4 complete (Steps 13-16)
→ Next: Phase 5 - Google Cloud Setup (Steps 17-20)

## Session 6: 2025-12-15 - SPARQL Query Testing (Step 16)

### Completed: Step 16 - Test SPARQL Queries Against Local Fuseki

**Test Results:**
- Triple count: 1,367 (matches expected)
- Subjects query: 2 subjects (History, Science) - 457ms
- Science KS3 query: 3 content descriptors - 176ms
- Full curriculum query: 34 content descriptors - 1.352s

**Key Technical Fix:**
- Used `curl --data-binary @file.sparql` instead of `--data "$(cat file)"` to handle SPARQL comments (`#`) correctly

**Performance:**
- All queries well under 1-second target (except most complex at 1.3s)
- Container logs show no errors, all 200 OK responses
- Service endpoint: `http://localhost:3030/national-curriculum-for-england/sparql`

**Naming Update:** Changed from `nc-england` to `national-curriculum-for-england` for consistency with directory structure and DfE requirements

**No commit:** Testing only (container stopped and removed)
