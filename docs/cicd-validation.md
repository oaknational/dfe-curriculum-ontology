# CI/CD Validation Pipeline

This document explains how the UK Curriculum Ontology validates its data quality using SHACL (Shapes Constraint Language) in its automated CI/CD pipeline.

## Overview

All curriculum data in this repository is automatically validated against SHACL constraints to ensure:
- Data consistency and completeness
- Correct relationships between resources
- Compliance with curriculum structure rules
- Prevention of invalid or orphaned data

**Validation runs automatically** on every push and pull request via GitHub Actions.

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

### Option 1: Full CI/CD Validation (Recommended)

Run the exact same validation as the CI/CD pipeline:

```bash
# Stage 1: Syntax check (built into merge script)
python3 scripts/merge_ttls.py

# Stage 2: SHACL validation
pyshacl \
  --shacl ontology/curriculum-constraints.ttl \
  --ont-graph ontology/curriculum-ontology.ttl \
  --inference rdfs \
  --abort \
  --format human \
  /tmp/combined-data.ttl
```

**This matches CI/CD exactly** and is the authoritative validation method.

### Option 2: Using the Local Validation Script

Use the existing convenience script:

```bash
python3 scripts/validation.py
```

**Note:** This script uses a hardcoded file list and may not match CI/CD exactly. It's useful for quick local checks but Option 1 is recommended for final validation.

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

When adding new `.ttl` files to the repository, **no configuration changes are needed**.

### What Works Automatically

The merge script automatically discovers files in these directories:

✅ **New subjects:**
```
data/england/subjects/english/
├── english-subject.ttl
├── english-knowledge-taxonomy.ttl
└── english-schemes.ttl
```

✅ **New regions:**
```
data/wales/
├── programme-structure.ttl
└── themes.ttl
```

✅ **New data files:**
```
data/england/
├── assessments.ttl
├── qualifications.ttl
└── pedagogical-approaches.ttl
```

✅ **New ontology files:**
```
ontology/
├── curriculum-ontology.ttl
├── curriculum-constraints.ttl
└── extensions.ttl
```

All these files are **automatically discovered and validated** - zero configuration required.

### Version Files Are Automatically Excluded

Files in `versions/` directories are automatically skipped:

```
ontology/versions/
├── curriculum-ontology-0.0.9.ttl    ⏭ Skipped
└── curriculum-constraints-0.0.9.ttl  ⏭ Skipped

data/england/versions/0.0.9/
├── programme-structure-0.0.9.ttl    ⏭ Skipped
└── themes-0.0.9.ttl                  ⏭ Skipped
```

This ensures historical snapshots don't interfere with current validation.

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

#### 3. Complex Import Resolution (Future)

Currently, this repo validates all files as local - no external imports are fetched. If you add external `owl:imports` that need resolution, you'll need to implement a URI mapping system (see oak-curriculum-ontology for an example).

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

### Syntax Errors

**Example:**
```
Checking: data/england/programme-structure.ttl
  ✗ ERROR: Bad syntax at line 42: Unexpected token '.'
```

**Causes:**
- Missing closing brackets
- Incorrect punctuation (`.` `;` `,`)
- Missing prefix declarations
- Unclosed string literals

**Fix:** Check the specific line number and verify Turtle syntax.

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
2. **Check CI/CD logs** if validation fails - they show exactly what's wrong
3. **Keep constraints in sync** with ontology changes
4. **Use meaningful constraint messages** to help debug failures
5. **Version your constraints** separately from your data
6. **Test incrementally** when adding new constraint rules
7. **Validate before and after** major refactoring

## Troubleshooting

### Problem: Merge script doesn't find my new file

**Check:**
- Is the file in `ontology/` or `data/` directories?
- Does the file have a `.ttl` extension?
- Is the file in a `versions/` directory? (These are excluded)

**Solution:** Move the file to `ontology/` or `data/`, or update `ROOT_DIRS` in the merge script.

### Problem: Validation passes locally but fails in CI/CD

**Causes:**
- Different files being validated (local script uses hardcoded list)
- Environment differences

**Solution:** Use `scripts/merge_ttls.py` + `pyshacl` locally (Option 1) to match CI/CD exactly.

### Problem: owl:imports validation shows unexpected URIs

**Check:**
- Review the list of imports reported by merge_ttls.py
- Verify all imports are intentional
- Check for typos in import URIs

**Solution:** Fix or remove unintended `owl:imports` declarations.

### Problem: Workflow runs very slowly

**Check:**
- Is pip caching enabled? (Should see "Cache restored" in logs)
- Are there very large TTL files being parsed?

**Solution:**
- Ensure `cache: 'pip'` is in workflow Python setup steps
- Consider breaking very large files into smaller ones

## Differences from oak-curriculum-ontology

This repository has simpler validation needs:

| Aspect | uk-curriculum-ontology | oak-curriculum-ontology |
|--------|------------------------|-------------------------|
| **External dependencies** | None (all files local) | Multiple (imports from this repo) |
| **Import resolution** | Report only | Complex URI mapping + fetching |
| **File discovery** | Auto-discovery ✅ | Auto-discovery ✅ |
| **Validation approach** | Simple merging | Import resolution + merging |
| **Complexity** | Appropriate for needs | More complex (necessarily) |

Both repositories follow the same validation principles with appropriate complexity for their specific requirements.

## Further Reading

- [SHACL Specification (W3C)](https://www.w3.org/TR/shacl/)
- [pyshacl Documentation](https://github.com/RDFLib/pySHACL)
- [Turtle Syntax](https://www.w3.org/TR/turtle/)
- [RDF 1.1 Primer](https://www.w3.org/TR/rdf11-primer/)
- [GitHub Actions: Caching dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
