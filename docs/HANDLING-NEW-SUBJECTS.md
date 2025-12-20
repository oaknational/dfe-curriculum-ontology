# Handling New Subjects: Automatic File Creation

## The Scenario

DfE authors add a NEW subject to Sanity that doesn't exist in your repository:

```
Existing in Repository:
├─ subjects/science/
└─ subjects/history/

New in Sanity:
└─ Mathematics (NEW!)

Question: What happens when the script runs?
```

## Current Script Behavior (Hardcoded)

**Problem:** The current script is hardcoded to "science"

```python
# scripts/sanity_to_ttl.py (current)

# Line 475: Hardcoded
print("\n   Converting science subject...")

# Line 491: Hardcoded directory
science_dir = f"{SUBJECTS_DIR}/science"
write_ttl_file(subject_graph, f"{science_dir}/science-subject.ttl")
```

**What happens if Mathematics data appears:**

```
Sanity Data:
├─ subject-science (exists)
├─ subject-history (exists)
└─ subject-mathematics (NEW!)

Current Script Result:
✗ Mathematics data gets mixed into science files
✗ No mathematics/ directory created
✗ No mathematics-*.ttl files created
✗ Data ends up in science-subject.ttl (WRONG!)
```

## Solution: Dynamic Subject Processing

### Step 1: Discover Subjects in Data

```python
def discover_subjects(data: Dict) -> Set[str]:
    """
    Scan data to find all subjects present.

    Returns: {'science', 'history', 'mathematics'}
    """
    subjects = set()

    # Method 1: From explicit subject documents
    for subject in data.get('subjects', []):
        subject_id = subject['_id'].replace('subject-', '')
        subjects.add(subject_id)  # 'science', 'mathematics', etc.

    # Method 2: From subsubject references
    for subsubject in data.get('subsubjects', []):
        subject_ref = subsubject['subject']['_ref']
        subject_id = subject_ref.replace('subject-', '')
        subjects.add(subject_id)

    # Method 3: From document ID patterns (backup)
    # Look for common subject names in IDs
    for doc in all_documents:
        doc_id = doc['_id']
        if 'mathematics' in doc_id:
            subjects.add('mathematics')

    return subjects

# Example result:
# {'science', 'history', 'mathematics'}
```

### Step 2: Filter Data by Subject

```python
def get_subject_data(all_data: Dict, subject: str) -> Dict:
    """
    Extract only the documents for one subject.

    Example: subject='mathematics'
    Returns: Only mathematics-related documents
    """

    # Get the subject document
    subjects = [s for s in all_data['subjects']
                if s['_id'] == f'subject-{subject}']

    # Get subsubjects for this subject
    subsubjects = [ss for ss in all_data['subsubjects']
                   if ss['subject']['_ref'] == f'subject-{subject}']

    # Follow the reference chain to get related data:
    # Subjects → Disciplines → Strands → SubStrands → Descriptors

    # Get disciplines used by this subject
    discipline_ids = set()
    for subj in subjects:
        for disc in subj['disciplines']:
            discipline_ids.add(disc['_ref'])

    disciplines = [d for d in all_data['disciplines']
                   if d['_id'] in discipline_ids]

    # Get strands for these disciplines
    strands = [s for s in all_data['strands']
               if s['discipline']['_ref'] in discipline_ids]

    # ... continue down the hierarchy

    return {
        'subjects': subjects,
        'subsubjects': subsubjects,
        'disciplines': disciplines,
        'strands': strands,
        # ... etc
    }
```

### Step 3: Generate Files for Each Subject

```python
def process_all_subjects(data: Dict):
    """
    Automatically handle all subjects in the data.
    Creates new directories and files as needed.
    """

    # Discover subjects
    subjects = discover_subjects(data)
    # Returns: {'science', 'history', 'mathematics'}

    # Process each subject
    for subject in subjects:
        print(f"Processing: {subject}")

        # Get data for this subject only
        subject_data = get_subject_data(data, subject)

        # Create directory if it doesn't exist
        subject_dir = f"subjects/{subject}"
        os.makedirs(subject_dir, exist_ok=True)  # ← Creates NEW directory

        # Generate files
        generate_subject_file(subject, subject_data)
        generate_taxonomy_file(subject, subject_data)
        generate_schemes_file(subject, subject_data)

# Result:
# subjects/
# ├─ science/
# │  ├─ science-subject.ttl
# │  ├─ science-knowledge-taxonomy.ttl
# │  └─ science-schemes.ttl
# ├─ history/
# │  └─ ...
# └─ mathematics/      ← NEW!
#    ├─ mathematics-subject.ttl      ← NEW!
#    ├─ mathematics-knowledge-taxonomy.ttl  ← NEW!
#    └─ mathematics-schemes.ttl      ← NEW!
```

## Complete Example

### Scenario: Mathematics Added to Sanity

**Monday: Initial State**

```
Repository:
└─ subjects/
   ├─ science/
   └─ history/

Sanity:
├─ Science (50 docs)
└─ History (40 docs)
```

**Tuesday: DfE Authors Add Mathematics**

```
Sanity Studio:
1. Create subject-mathematics
2. Create subsubject-mathematics
3. Create discipline-mathematics
4. Create strands: Number, Algebra, Geometry
5. Create 100+ content descriptors
6. Publish all

Result in Sanity:
├─ Science (50 docs)
├─ History (40 docs)
└─ Mathematics (150 docs) ← NEW!
```

**Wednesday: Script Runs**

```
Step 1: Fetch data from Sanity
─────────────────────────────
Receives: Science (50), History (40), Mathematics (150)

Step 2: Discover subjects
──────────────────────────
discover_subjects() returns: {'science', 'history', 'mathematics'}
                                                     ↑
                                                   NEW!

Step 3: Process each subject
─────────────────────────────
For subject in ['science', 'history', 'mathematics']:

  Mathematics:
    ├─ Get mathematics data (150 docs)
    ├─ Create directory: subjects/mathematics/  ← NEW!
    ├─ Generate: mathematics-subject.ttl        ← NEW!
    ├─ Generate: mathematics-knowledge-taxonomy.ttl  ← NEW!
    └─ Generate: mathematics-schemes.ttl        ← NEW!

Step 4: Git Status
──────────────────
New files:
  subjects/mathematics/mathematics-subject.ttl
  subjects/mathematics/mathematics-knowledge-taxonomy.ttl
  subjects/mathematics/mathematics-schemes.ttl

Changed files:
  subjects/science/science-*.ttl (updated timestamps)
  subjects/history/history-*.ttl (updated timestamps)
```

## Handling Different Types of New Entities

### 1. New Subject (Major)

```
New: subject-mathematics

Creates:
  ✓ subjects/mathematics/ (new directory)
  ✓ mathematics-subject.ttl (new file)
  ✓ mathematics-knowledge-taxonomy.ttl (new file)
  ✓ mathematics-schemes.ttl (new file)

Git:
  Added: 3 new files
```

### 2. New Discipline (within existing subject)

```
New: discipline-engineering (within Science subject)

Updates:
  ✓ subjects/science/science-knowledge-taxonomy.ttl (modified)
  ✗ No new files needed

Git:
  Modified: 1 file
```

### 3. New Content Descriptor (within existing substrand)

```
New: content-descriptor-photosynthesis (within Science)

Updates:
  ✓ subjects/science/science-knowledge-taxonomy.ttl (modified)
  ✓ subjects/science/science-schemes.ttl (if schemes reference it)
  ✗ No new files needed

Git:
  Modified: 1-2 files
```

### 4. New Key Stage (programme structure)

```
New: key-stage-5 (A-levels)

Updates:
  ✓ programme-structure.ttl (modified)
  ✓ ALL scheme files (if schemes reference the new KS)
  ✗ No new files needed

Git:
  Modified: 1 + N files (N = number of subjects)
```

## Directory Creation: How It Works

```python
# Python's os.makedirs with exist_ok=True

subject_dir = f"subjects/{subject}"
os.makedirs(subject_dir, exist_ok=True)
```

**What this does:**

```
If directory exists:
  → Do nothing (safe, no error)

If directory doesn't exist:
  → Create it (and any parent directories)

Examples:
  subjects/mathematics/        ← Creates both 'subjects' and 'mathematics'
  subjects/geography/          ← Creates 'geography' (subjects already exists)
```

**This is SAFE because:**
- ✅ Won't error if directory already exists
- ✅ Won't overwrite existing files
- ✅ Creates parent directories automatically
- ✅ Works across platforms (Windows, Mac, Linux)

## Validation Considerations

### New Subject Files Still Validate

```bash
# After Mathematics is added

./scripts/validate.sh

# Merges ALL TTL files:
✓ subjects/science/*.ttl
✓ subjects/history/*.ttl
✓ subjects/mathematics/*.ttl  ← NEW files included

# Validates against SHACL:
✓ All constraints pass
```

**Why validation still works:**
- New files follow same ontology structure
- Same property patterns (rdfs:label, skos:prefLabel)
- Same SHACL constraints apply
- No changes to validation logic needed

### Potential Issues

**Issue 1: ID collisions**

```
Problem:
  subject-mathematics (Mathematics)
  subject-mathematics (Maths - UK abbreviation)

Solution: Ensure unique IDs in Sanity
```

**Issue 2: Missing references**

```
Problem:
  New scheme references key-stage-5 (doesn't exist yet)

Result: Validation fails (reference constraint)

Solution: Create referenced entities first
```

## Git Workflow with New Subjects

### When Mathematics is Added

```bash
# After script runs
git status

# Output:
Untracked files:
  subjects/mathematics/

# View new files
git add subjects/mathematics/

# Review
git diff --cached

# Commit
git commit -m "Add Mathematics curriculum

- Added mathematics subject definition
- Added mathematics knowledge taxonomy (150 descriptors)
- Added mathematics schemes for KS1-4

Generated from Sanity CMS data."

git push
```

### Git Shows Clearly

```
New Subject → New Directory → Easy to Review

vs.

New Descriptor → Modified file → Mixed with other changes
```

## Best Practices

### 1. Add Subjects One at a Time

```
Good:
  Week 1: Add Science
  Week 2: Add History
  Week 3: Add Mathematics

Easier to:
  ✓ Review changes
  ✓ Validate each subject
  ✓ Rollback if issues
```

### 2. Create Complete Subject Hierarchy

```
Don't:
  ✗ Create subject only
  ✗ Run script (generates empty files)
  ✗ Add content later

Do:
  ✓ Create subject
  ✓ Add disciplines, strands, descriptors
  ✓ Add schemes
  ✓ Then run script (generates complete files)
```

### 3. Test with Sample Data First

```bash
# Before adding to production Sanity:

# 1. Add Mathematics to sample-data.json
# 2. Run script with sample data
python scripts/sanity_to_ttl.py --sample

# 3. Review generated files
# 4. Validate
./scripts/validate.sh

# 5. If good, add to Sanity
```

## Automatic vs. Manual File Creation

### Automatic (Recommended)

```
Script discovers subjects and creates files automatically.

Pros:
✓ No manual work
✓ Always consistent
✓ Can't forget files
✓ Handles any number of subjects

Cons:
✗ Need dynamic script logic
```

### Manual

```
You manually create directory and files first.

Pros:
✓ Full control
✓ Can customize per subject

Cons:
✗ Easy to forget files
✗ Error-prone
✗ Doesn't scale
```

**Recommendation:** Use automatic (dynamic script)

## Migration Path

### Phase 1: Current (Hardcoded Science)

```python
# Works for: Science only
science_dir = f"{SUBJECTS_DIR}/science"
```

### Phase 2: Add History (Hardcoded Both)

```python
# Works for: Science and History
for subject in ['science', 'history']:
    generate_subject_files(subject, data)
```

### Phase 3: Dynamic (Any Subject)

```python
# Works for: Any subjects in data
subjects = discover_subjects(data)
for subject in subjects:
    generate_subject_files(subject, data)
```

## Summary

**Question:** What if new subject appears in Sanity?

**Current Script:** ❌ Won't handle it (hardcoded to science)

**Solution:** ✅ Make script discover subjects dynamically

**Result:**
- New directory created automatically
- New TTL files generated automatically
- Validation still works
- Git clearly shows what's new

**Key Code Pattern:**

```python
# Discover subjects in data
subjects = discover_subjects(data)

# Process each one
for subject in subjects:
    # Create directory
    os.makedirs(f"subjects/{subject}", exist_ok=True)

    # Generate files
    generate_files(subject)
```

**See:** `scripts/sanity_to_ttl_dynamic_subjects.py` for complete implementation
