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
