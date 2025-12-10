# SHACL Validation

This document explains how the UK Curriculum Ontology validates its data quality using SHACL (Shapes Constraint Language) in its automated CI/CD pipeline.

## Overview

All curriculum data in this repository is automatically validated against SHACL constraints to ensure:
- Data consistency and completeness
- Correct relationships between resources
- Compliance with curriculum structure rules
- Prevention of invalid or orphaned data

**Validation runs automatically** on every push and pull request via GitHub Actions.

## SHACL Constraints

SHACL constraints are defined in `ontology/curriculum-constraints.ttl`. These constraints specify rules that curriculum data must follow.

### Key Validation Rules

#### Phase Constraints:
- Every phase must have at least one `rdfs:label`
- Every phase must specify exactly one lower age boundary (non-negative integer)
- Every phase must specify exactly one upper age boundary (positive integer)
- Lower age boundary must be less than upper age boundary
- Age boundaries must be in reasonable range (0-25 years)

#### Key Stage Constraints:
- Every key stage must have at least one `rdfs:label`
- Every key stage must be part of exactly one phase (`curric:isPartOf`)
- Every key stage must specify exactly one lower and upper age boundary
- Lower age boundary must be less than upper age boundary
- Key stage age boundaries must fall within parent phase boundaries

#### Year Group Constraints:
- Every year group must have at least one `rdfs:label`
- Every year group must be part of exactly one key stage
- Every year group must specify exactly one lower and upper age boundary
- Lower age boundary must be less than upper age boundary
- Year group age boundaries must fall within parent key stage boundaries

#### Subject Constraints:
- Every subject must have at least one `rdfs:label`
- Every subject must have at least one `skos:prefLabel` for SKOS taxonomy
- Every subject must be part of at least one concept scheme (`skos:inScheme`)
- Subjects may have zero or more strands and aims
- Subjects must not be orphaned (must have at least one sub-subject)

#### Sub-Subject Constraints:
- Every sub-subject must have at least one `rdfs:label`
- Every sub-subject must be part of exactly one subject
- Sub-subjects may include zero or more strands
- When a sub-subject includes a strand, the strand must have a corresponding `applicableToSubSubject` link
- Sub-subjects must not be orphaned (must be used in at least one scheme)

#### Scheme Constraints:
- Every scheme must have at least one `rdfs:label`
- Every scheme must be part of at least one sub-subject
- Every scheme must specify exactly one key stage (`curric:hasKeyStage`)
- Schemes may have zero or more content descriptors

#### Strand Constraints:
- Every strand must have at least one `skos:prefLabel`
- Every strand must be part of exactly one concept scheme
- Every strand must belong to exactly one subject (`skos:broader`)
- Every strand must be applicable to at least one sub-subject
- Every strand must have at least one sub-strand (`skos:narrower`)
- When a strand is applicable to a sub-subject, the sub-subject must include that strand
- Strands must not be orphaned (must be referenced by at least one subject or sub-subject)

#### Sub-Strand Constraints:
- Every sub-strand must have at least one `skos:prefLabel`
- Every sub-strand must be part of exactly one concept scheme
- Every sub-strand must belong to exactly one strand (`skos:broader`)
- Every sub-strand must have at least one content descriptor (`skos:narrower`)
- Sub-strands must not be orphaned (must be referenced by at least one strand)

#### Content Descriptor Constraints:
- Every content descriptor must have at least one `skos:prefLabel`
- Every content descriptor must be part of exactly one concept scheme
- Every content descriptor must belong to exactly one sub-strand (`skos:broader`)
- Content descriptors may have zero or more content sub-descriptors (`skos:narrower`)
- Content descriptors must not be orphaned (must be used in at least one scheme or referenced by a sub-strand)

#### Content Sub-Descriptor Constraints:
- Every content sub-descriptor must have at least one `skos:prefLabel`
- Every content sub-descriptor must be part of exactly one concept scheme
- Every content sub-descriptor must belong to exactly one content descriptor (`skos:broader`)
- Content sub-descriptors may have zero or more text examples and URL examples
- Content sub-descriptors must not be orphaned (must be referenced by at least one content descriptor)

#### Theme Constraints:
- Every theme must have at least one `skos:prefLabel`
- Every theme must have at least one `skos:definition`
- Every theme must be part of exactly one concept scheme
- Themes must not be orphaned (must be related to at least one content item via `skos:related`)

See `ontology/curriculum-constraints.ttl` for the complete constraint definitions.

## How Validation Works

Validation occurs in two stages:

### Stage 1: Syntax Check

**Purpose:** Verify that all TTL files have valid Turtle syntax before attempting SHACL validation.

**Tool:** rdflib

The workflow discovers and checks **every** `.ttl` file in the repository:

```python
for ttl_file in sorted(Path('.').rglob('*.ttl')):
    g = Graph()
    g.parse(ttl_file, format='turtle')
```

This catches:
- Syntax errors
- Malformed URIs
- Invalid prefixes
- Structural issues
- Missing closing brackets or quotes

**If any file has syntax errors, the workflow fails** before proceeding to SHACL validation.

### Stage 2: SHACL Validation

**Purpose:** Validate merged data against SHACL business rules and constraints.

**Tools:** rdflib, pyshacl

This stage has two steps:

#### Step 2.1: Merge TTL Files with Auto-Discovery

**Script:** `scripts/merge_ttls.py`

This script automatically:

1. **Discovers all `.ttl` files** in `ontology/` and `data/` directories
2. **Excludes versioned files** from `versions/` directories
3. **Parses and combines** all files into a single RDF graph
4. **Validates owl:imports** declarations (reports all import URIs found)
5. **Outputs** merged graph to `/tmp/combined-data.ttl`

**Example output:**
```
======================================================================
MERGING TTL FILES FOR VALIDATION
======================================================================
📄 Parsing: ontology/curriculum-ontology.ttl
📄 Parsing: ontology/curriculum-constraints.ttl
📄 Parsing: data/england/programme-structure.ttl
📄 Parsing: data/england/subjects/science/science-subject.ttl
⏭  Skipping versioned file: ontology/versions/curriculum-ontology-0.0.9.ttl

📋 Local curriculum imports found:
   ✓ https://w3id.org/uk/curriculum/core/
   ✓ https://w3id.org/uk/curriculum/england/programme-structure

======================================================================
✅ Successfully merged 7 files into /tmp/combined-data.ttl
======================================================================
```

**Key benefits:**
- ✅ **Zero maintenance** - New files are automatically discovered
- ✅ **Version exclusion** - Historical snapshots don't interfere with validation
- ✅ **Import visibility** - See all dependencies between files
- ✅ **Early error detection** - Parsing errors caught during merge

#### Step 2.2: Run SHACL Validation

The merged data graph is validated against SHACL constraints with RDFS inference:

```bash
pyshacl \
  --shacl ontology/curriculum-constraints.ttl \
  --ont-graph ontology/curriculum-ontology.ttl \
  --inference rdfs \
  --abort \
  --format human \
  /tmp/combined-data.ttl
```

**Parameters:**
- `--shacl`: SHACL shapes file defining validation rules
- `--ont-graph`: Ontology file defining classes and properties
- `--inference rdfs`: Enable RDFS inference (automatic class membership)
- `--abort`: Fail immediately on first violation
- `--format human`: Output human-readable validation reports

**Success:** `Validation Report - Conforms: True`

**Failure:** Pipeline stops and reports violations with:
- Focus node (resource that failed validation)
- Constraint violated
- Property path
- Human-readable message

## CI/CD Workflow

**File:** `.github/workflows/validate-ontology.yml`

### Workflow Triggers

The validation runs on:
- **Pushes** to `main` or `develop` branches when:
  - Any `.ttl` file changes
  - Workflow file changes
  - `scripts/merge_ttls.py` changes
- **Pull requests** to `main` when files change
- **Manual dispatch** via GitHub Actions UI

### Workflow Jobs

```yaml
jobs:
  syntax-check:          # Stage 1
    ↓
  shacl-validation:      # Stage 2 (only runs if syntax-check passes)
```

### Complete Workflow Steps

```
Stage 1: Syntax Check
├─ 1. Checkout repository
├─ 2. Set up Python 3.11 (with pip dependency caching)
├─ 3. Install rdflib
└─ 4. Check all .ttl files for valid Turtle syntax
      - Discovers files with Path('.').rglob('*.ttl')
      - Parses each file with rdflib
      - Reports errors with file path and line number
   ↓
   [If syntax errors found → FAIL]
   ↓
Stage 2: SHACL Validation (depends on Stage 1 passing)
├─ 1. Checkout repository
├─ 2. Set up Python 3.11 (with pip dependency caching)
├─ 3. Install rdflib + pyshacl
├─ 4. Merge TTL files with auto-discovery
│     - Runs: scripts/merge_ttls.py
│     - Auto-discovers all .ttl files in ontology/ and data/
│     - Excludes versions/ directories
│     - Checks owl:imports declarations
│     - Outputs: /tmp/combined-data.ttl
└─ 5. Run SHACL validation
      - Validates merged data against constraints
      - Uses RDFS inference
      - Outputs human-readable report
   ↓
   [If violations found → FAIL]
   [If conforms → PASS]
```

### Performance Optimizations

**Dependency Caching:**

Both jobs use pip caching to speed up workflow runs:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'  # ← Caches installed packages between runs
```

**Benefits:**
- ✅ Faster workflow execution (30-60% faster on average)
- ✅ Reduced network usage
- ✅ More reliable (less dependent on PyPI availability)

**Two-Stage Validation:**

Syntax checking runs first as a separate job:
- ✅ **Fail fast** - Syntax errors caught before expensive SHACL validation
- ✅ **Clear errors** - Syntax errors reported separately from constraint violations
- ✅ **Parallel-ready** - Jobs can run in parallel in the future if needed

## Running Validation Locally

### Using the Validation Script (Recommended)

Run the exact same validation as the CI/CD pipeline with a single command:

```bash
./scripts/validate.sh
```

This script:
- ✅ Merges all TTL files with auto-discovery
- ✅ Runs SHACL validation with RDFS inference
- ✅ Matches CI/CD exactly
- ✅ Auto-detects pyshacl (checks virtual environment first, then system)

**Prerequisites:**

```bash
# Install pyshacl if not already installed
pip install pyshacl

# Or in a virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install pyshacl
```

### Manual Validation (Advanced)

If you need to run the validation steps manually:

```bash
# Step 1: Merge TTL files with auto-discovery
python3 scripts/merge_ttls.py

# Step 2: Run SHACL validation
pyshacl \
  --shacl ontology/curriculum-constraints.ttl \
  --ont-graph ontology/curriculum-ontology.ttl \
  --inference rdfs \
  --abort \
  --format human \
  /tmp/combined-data.ttl
```

### Expected Output

**Success:**
```
======================================================================
MERGING TTL FILES FOR VALIDATION
======================================================================
📄 Parsing: ontology/curriculum-ontology.ttl
...
✅ Successfully merged 7 files into /tmp/combined-data.ttl
======================================================================

Validation Report
Conforms: True
```

**Failure:**
```
Validation Report
Conforms: False
Results (1):
Constraint Violation in MinCountConstraintComponent:
    Severity: sh:Violation
    Focus Node: eng:my-phase
    Result Path: rdfs:label
    Message: Phases must have an rdfs:label.
```

## Adding New Files

When adding new `.ttl` files to the repository, **no configuration changes are needed** in most cases.

### Automatic Discovery

The merge script automatically discovers all `.ttl` files in:
- `ontology/`
- `data/`
- All subdirectories (excluding `versions/`)

New files are automatically included in validation.

### When Configuration IS Needed

You only need to update `scripts/merge_ttls.py` if:

#### 1. Adding New Root Directories

If you create new top-level directories besides `ontology/` and `data/`:

```python
# In scripts/merge_ttls.py
ROOT_DIRS = [
    "ontology",
    "data",
    "examples",  # ← Add your new directory
]
```

#### 2. Adding New Excluded Directories

If you want to exclude directories besides `versions/`:

```python
# In scripts/merge_ttls.py, update the skip logic:
if "versions" in ttl_file.parts or "archive" in ttl_file.parts:
    print(f"⏭  Skipping: {ttl_file}")
    continue
```

### What Doesn't Need Configuration

These changes work automatically:
- ✅ Adding new subjects in `data/england/subjects/<subject>/`
- ✅ Adding new regions in `data/<region>/`
- ✅ Creating new data files in `data/`
- ✅ Updating existing files
- ✅ Adding new SHACL constraints in `ontology/curriculum-constraints.ttl`

## owl:imports Validation

The merge script automatically reports all `owl:imports` declarations:

### Local Imports

```
📋 Local curriculum imports found:
   ✓ https://w3id.org/uk/curriculum/core/
   ✓ https://w3id.org/uk/curriculum/england/programme-structure
   ✓ https://w3id.org/uk/curriculum/england/science-subject
```

These are imports within this repository (or to w3id.org URIs that should resolve).

### External Imports

```
⚠️  External imports found:
   ! http://www.example.org/some-external-vocab
   These should resolve via w3id.org or be standard vocabularies.
```

External imports (non-curriculum URIs) are flagged for visibility.

**What gets skipped:**
Standard W3C vocabularies (OWL, RDFS, SKOS, etc.) are not reported as they're expected.

**Benefits:**
- ✅ **Dependency visibility** - See all file dependencies
- ✅ **Broken imports** - Catch typos in import URIs
- ✅ **Circular imports** - Identify potential circular dependencies
- ✅ **External dependencies** - Track dependencies on external ontologies

## Common Validation Errors

### Class Constraint Violations

**Example:**
```
Constraint Violation in ClassConstraintComponent:
    Focus Node: eng:key-stage-1
    Value Node: eng:my-invalid-phase
    Result Path: curric:isPartOf
    Message: Key stages must belong to a Phase.
```

**Cause:** The referenced resource (`eng:my-invalid-phase`) is not of the required class (`curric:Phase`).

**Fix:** Ensure the referenced resource has the correct `rdf:type`:
```turtle
eng:my-invalid-phase
  a curric:Phase ;  # ← Add this
  rdfs:label "My Phase"@en .
```

### Cardinality Violations

**Example:**
```
Constraint Violation in MinCountConstraintComponent:
    Focus Node: eng:scheme-science-ks3
    Result Path: curric:hasKeyStage
    Message: Schemes must specify exactly which key stage they cover.
```

**Cause:** Missing required property (minCount violation) or too many values (maxCount violation).

**Fix:** Add the required property:
```turtle
eng:scheme-science-ks3
  a curric:Scheme ;
  rdfs:label "Science Key Stage 3" ;
  curric:hasKeyStage eng:key-stage-3 .  # ← Add this
```

### Orphaned Resource Violations

**Example:**
```
Constraint Violation:
    Focus Node: eng:key-stage-orphaned
    Message: Key stage is not used in any scheme (orphaned)
```

**Cause:** A resource exists but nothing references it.

**Fix:** Either:
1. Add a reference to the resource:
```turtle
eng:scheme-something
  curric:hasKeyStage eng:key-stage-orphaned .
```

2. Or remove the unused resource if it's not needed.

### Age Boundary Violations

**Example:**
```
Constraint Violation:
    Focus Node: eng:phase-invalid
    Message: Lower age boundary must be less than upper age boundary
```

**Cause:** Age boundaries are inverted or equal.

**Fix:**
```turtle
eng:phase-invalid
  curric:lowerAgeBoundary 5 ;   # Must be < upper
  curric:upperAgeBoundary 11 .
```

### SKOS Violations

**Example:**
```
Constraint Violation in DatatypeConstraintComponent:
    Focus Node: eng:subject-science
    Value Node: "Science"
    Result Path: skos:prefLabel
    Message: Data type mismatch (expected rdf:langString)
```

**Cause:** `skos:prefLabel` requires a language tag.

**Fix:**
```turtle
# Wrong:
eng:subject-science skos:prefLabel "Science" .

# Correct:
eng:subject-science skos:prefLabel "Science"@en .
```

## Best Practices

1. **Run validation locally** before pushing to catch errors early
2. **Check the CI/CD output** if validation fails to see detailed error reports
3. **Update URI mappings** when adding imports from new external files
4. **Keep constraints synchronized** with data model changes
5. **Use meaningful SHACL messages** to help diagnose validation failures

## Further Reading

- [SHACL Specification (W3C)](https://www.w3.org/TR/shacl/)
- [pyshacl Documentation](https://github.com/RDFLib/pySHACL)
