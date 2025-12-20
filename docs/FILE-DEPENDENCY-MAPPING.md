# File Dependency Mapping: Which Files to Regenerate

## The Problem

When "Biomechanics" content descriptor changes, which TTL files need updating?

```
Changed Document:
┌────────────────────────────────────────┐
│ _id: content-descriptor-biomechanics   │
│ _type: contentDescriptor               │
│ prefLabel: "Biomechanics (UPDATED)"    │
└────────────────────────────────────────┘
                ↓
        Question: Which files?
                ↓
┌────────────────────────────────────────┐
│ TTL Files in Repository:               │
├────────────────────────────────────────┤
│ ✓ science-knowledge-taxonomy.ttl       │
│ ✓ science-schemes.ttl                  │
│ ✗ science-subject.ttl                  │
│ ✗ history-knowledge-taxonomy.ttl       │
│ ✗ programme-structure.ttl              │
└────────────────────────────────────────┘
```

## Current Script Behavior

**The current script (`sanity_to_ttl.py`) uses a SIMPLE approach:**

```python
# Regenerates ALL files for the subject scope
def convert_to_ttl(data):
    """
    Groups ALL documents by subject and regenerates ALL subject files.
    """

    # Process ALL science data together
    if has_science_data(data):
        generate_science_subject_ttl(data)          # ALL subjects/subsubjects
        generate_science_taxonomy_ttl(data)         # ALL disciplines/strands/descriptors
        generate_science_schemes_ttl(data)          # ALL schemes

    # Process ALL history data together
    if has_history_data(data):
        generate_history_subject_ttl(data)
        generate_history_taxonomy_ttl(data)
        generate_history_schemes_ttl(data)
```

**Even if only "Biomechanics" changed:**
- Regenerates entire `science-knowledge-taxonomy.ttl` (all science descriptors)
- Regenerates entire `science-schemes.ttl` (all science schemes)
- Regenerates entire `science-subject.ttl` (all science subjects)

**Why?**
- ✅ Simple logic
- ✅ Always consistent
- ✅ No dependency tracking needed
- ❌ Inefficient (rewrites unchanged data)
- ❌ Large Git diffs

## Better Approach: Dependency Mapping

### Step 1: Determine Subject from Document

```python
def get_subject_for_document(doc, all_data):
    """
    Determine which subject a document belongs to.

    Uses multiple strategies in order of reliability.
    """

    doc_type = doc['_type']
    doc_id = doc['_id']

    # Strategy 1: Direct subject documents
    if doc_type == 'subject':
        # ID: "subject-science" → "science"
        return doc_id.replace('subject-', '')

    # Strategy 2: Documents with subject reference
    if doc_type == 'subsubject':
        subject_ref = doc.get('subject', {}).get('_ref')
        if subject_ref:
            return subject_ref.replace('subject-', '')

    # Strategy 3: Follow references up hierarchy
    if doc_type in ['contentDescriptor', 'contentSubdescriptor']:
        return trace_to_subject_via_taxonomy(doc, all_data)

    if doc_type == 'scheme':
        # Schemes reference subsubjects
        subsubject_ref = doc.get('subsubject', {}).get('_ref')
        subsubject = find_doc(subsubject_ref, all_data)
        if subsubject:
            return get_subject_for_document(subsubject, all_data)

    # Strategy 4: Pattern matching in ID
    # IDs often contain subject name
    # "content-descriptor-biomechanics" might be in science
    return infer_subject_from_id_patterns(doc_id, all_data)


def trace_to_subject_via_taxonomy(descriptor, all_data):
    """
    ContentDescriptor → SubStrand → Strand → Discipline → Subject
    """

    # Get substrand
    substrand_ref = descriptor.get('substrand', {}).get('_ref')
    if not substrand_ref:
        return None

    substrand = find_doc(substrand_ref, all_data)
    if not substrand:
        return None

    # Get strand
    strand_ref = substrand.get('strand', {}).get('_ref')
    strand = find_doc(strand_ref, all_data)
    if not strand:
        return None

    # Get discipline
    discipline_ref = strand.get('discipline', {}).get('_ref')
    discipline = find_doc(discipline_ref, all_data)
    if not discipline:
        return None

    # Find subject that uses this discipline
    for subject in all_data.get('subjects', []):
        disc_refs = [d.get('_ref') for d in subject.get('disciplines', [])]
        if discipline_ref in disc_refs:
            return subject['_id'].replace('subject-', '')

    return None
```

### Step 2: Map Document Type to File

```python
def get_affected_files(doc, subject):
    """
    Determine which files contain this type of document.

    Returns list of file paths relative to data/ directory.
    """

    doc_type = doc['_type']
    base_path = f"subjects/{subject}"

    # Map document types to files
    file_mapping = {
        # Subject definitions file
        'subject': f"{base_path}/{subject}-subject.ttl",
        'subsubject': f"{base_path}/{subject}-subject.ttl",

        # Knowledge taxonomy file
        'discipline': f"{base_path}/{subject}-knowledge-taxonomy.ttl",
        'strand': f"{base_path}/{subject}-knowledge-taxonomy.ttl",
        'substrand': f"{base_path}/{subject}-knowledge-taxonomy.ttl",
        'contentDescriptor': f"{base_path}/{subject}-knowledge-taxonomy.ttl",
        'contentSubdescriptor': f"{base_path}/{subject}-knowledge-taxonomy.ttl",

        # Schemes file
        'scheme': f"{base_path}/{subject}-schemes.ttl",
        'progression': f"{base_path}/{subject}-schemes.ttl",

        # Programme structure (special case - not subject-specific)
        'phase': "programme-structure.ttl",
        'keyStage': "programme-structure.ttl",
        'yearGroup': "programme-structure.ttl",

        # Themes (special case)
        'theme': "themes.ttl",
    }

    affected_file = file_mapping.get(doc_type)

    if not affected_file:
        return []

    return [affected_file]


def get_dependent_files(doc, subject, affected_files):
    """
    Get additional files that depend on this document.

    Example: If a ContentDescriptor changes, schemes that reference it
    also need updating.
    """

    dependent = []

    # If a descriptor changed, schemes might reference it
    if doc['_type'] == 'contentDescriptor':
        schemes_file = f"subjects/{subject}/{subject}-schemes.ttl"
        if schemes_file not in affected_files:
            dependent.append(schemes_file)

    # If a strand changed, need to regenerate substrands AND descriptors
    if doc['_type'] == 'strand':
        taxonomy_file = f"subjects/{subject}/{subject}-knowledge-taxonomy.ttl"
        if taxonomy_file not in affected_files:
            dependent.append(taxonomy_file)

    # If a key stage changed, all schemes using it need regeneration
    if doc['_type'] == 'keyStage':
        # Need to regenerate ALL subject scheme files (cross-subject dependency)
        # This is expensive but unavoidable
        dependent.extend(get_all_scheme_files())

    return dependent
```

### Step 3: Complete Change Processing

```python
def process_incremental_changes(changed_docs):
    """
    Process changed documents and regenerate only affected files.
    """

    # Group changed documents by affected files
    files_to_regenerate = {}  # {file_path: [docs]}

    for doc in changed_docs:
        # Determine subject
        subject = get_subject_for_document(doc, changed_docs)

        if not subject:
            print(f"⚠️  Could not determine subject for {doc['_id']}, skipping")
            continue

        # Get affected files
        affected = get_affected_files(doc, subject)

        # Get dependent files
        dependent = get_dependent_files(doc, subject, affected)

        # Combine
        all_affected = affected + dependent

        # Group by file
        for file_path in all_affected:
            if file_path not in files_to_regenerate:
                files_to_regenerate[file_path] = []
            files_to_regenerate[file_path].append(doc)

    # Now regenerate only affected files
    for file_path, docs in files_to_regenerate.items():
        print(f"📝 Regenerating: {file_path}")
        print(f"   Reason: {len(docs)} document(s) changed")

        # Fetch full context for this file
        # (may need more than just the changed docs)
        full_context = fetch_context_for_file(file_path, docs)

        # Regenerate the file
        regenerate_file(file_path, full_context)

    print(f"\n✅ Regenerated {len(files_to_regenerate)} files")
```

## Complete Example Walkthrough

### Scenario: "Biomechanics" Descriptor Changed

```
Step 1: Changed Document Detected
──────────────────────────────────
{
  "_id": "content-descriptor-biomechanics",
  "_type": "contentDescriptor",
  "_updatedAt": "2025-12-20T11:30:00Z",
  "prefLabel": "Biomechanics (UPDATED)",
  "substrand": {"_ref": "substrand-skeletal-and-muscular-systems"}
}


Step 2: Determine Subject
──────────────────────────
get_subject_for_document() →
  ├─ Fetch substrand: "substrand-skeletal-and-muscular-systems"
  ├─ Get its strand: "strand-structure-function-living-organisms"
  ├─ Get its discipline: "discipline-science"
  └─ Find subject with this discipline: "science"

Result: subject = "science"


Step 3: Get Affected Files
───────────────────────────
get_affected_files("contentDescriptor", "science") →
  └─ "subjects/science/science-knowledge-taxonomy.ttl"


Step 4: Get Dependent Files
────────────────────────────
get_dependent_files() →
  ├─ ContentDescriptor changed
  ├─ Check: Do any schemes reference this?
  ├─ Query all schemes for references to "content-descriptor-biomechanics"
  └─ Found: "scheme-science-key-stage-3" references it

Result: Also regenerate "subjects/science/science-schemes.ttl"


Step 5: Regenerate Files
─────────────────────────
Files to regenerate:
1. subjects/science/science-knowledge-taxonomy.ttl
   Reason: Contains content-descriptor-biomechanics

2. subjects/science/science-schemes.ttl
   Reason: scheme-science-key-stage-3 references this descriptor


Files NOT regenerated:
✗ subjects/science/science-subject.ttl (unchanged)
✗ subjects/history/*.ttl (different subject)
✗ programme-structure.ttl (unchanged)
```

## Challenge: Cross-File Dependencies

### Problem: One Change Cascades

```
Scenario: Key Stage 3 definition changes
─────────────────────────────────────────

Changed: key-stage-3 (programme structure)

Dependencies:
├─ scheme-science-key-stage-3 (references it)
├─ scheme-history-key-stage-3 (references it)
├─ scheme-mathematics-key-stage-3 (references it)
└─ ... (every scheme for KS3)

Files to regenerate:
├─ programme-structure.ttl
├─ subjects/science/science-schemes.ttl
├─ subjects/history/history-schemes.ttl
├─ subjects/mathematics/mathematics-schemes.ttl
└─ ... (all subject scheme files)
```

**Solution: Accept the cascade**
- Some changes affect many files
- This is correct behavior
- Still more efficient than regenerating everything

## Practical Implementation Strategy

### Strategy A: Current (Simple)

```python
# Regenerate all files for affected subject(s)
if any_science_changes(changed_docs):
    regenerate_all_science_files()

if any_history_changes(changed_docs):
    regenerate_all_history_files()
```

**Pros:** Simple, always consistent
**Cons:** Regenerates unchanged data

### Strategy B: Document-Type Grouping

```python
# Group by document type, regenerate corresponding files
changed_types = group_by_type(changed_docs)

if 'contentDescriptor' in changed_types:
    subjects = get_subjects(changed_types['contentDescriptor'])
    for subject in subjects:
        regenerate_knowledge_taxonomy(subject)

if 'scheme' in changed_types:
    subjects = get_subjects(changed_types['scheme'])
    for subject in subjects:
        regenerate_schemes(subject)
```

**Pros:** Better than full regeneration
**Cons:** Still regenerates all descriptors even if only one changed

### Strategy C: Per-Document Tracking (Complex)

```python
# Track exact dependencies, regenerate minimal set
for doc in changed_docs:
    affected_files = compute_full_dependency_chain(doc)
    for file in affected_files:
        mark_for_regeneration(file, doc)

regenerate_marked_files()
```

**Pros:** Minimal regeneration
**Cons:** Complex dependency tracking, harder to maintain

## Recommendation

**For your project: Use Strategy A initially, move to Strategy B when needed**

**Phase 1 (Now):** Strategy A
- Simple subject-level regeneration
- Good enough for 1-10 subjects
- Easy to understand and maintain

**Phase 2 (Later):** Strategy B
- Document-type grouping
- Better for 10-20 subjects
- Still reasonable complexity

**Phase 3 (If needed):** Strategy C
- Only for very large datasets (50+ subjects)
- Requires significant engineering effort

## Summary

**How the script knows which files to update:**

1. **Identify subject** - Trace references or parse IDs
2. **Map type → file** - ContentDescriptor → knowledge-taxonomy.ttl
3. **Check dependencies** - Does anything else reference this?
4. **Regenerate affected files** - Rebuild only necessary files

**Current script:** Regenerates all files for the subject (simple)
**Enhanced version:** Can target specific files (complex but efficient)

**Trade-off:**
- Simplicity vs. Efficiency
- Start simple, optimize later
