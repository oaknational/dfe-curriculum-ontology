# Sanity Update Strategies: Controlling Scope and Handling Changes

## Overview

The `sanity_to_ttl.py` script can operate in different modes to control what gets updated and how. This guide explains the trade-offs and shows you how to use each approach.

## Current Script Behavior

**The current script (`sanity_to_ttl.py`) does FULL REPLACEMENT:**

```bash
python scripts/sanity_to_ttl.py --sample
```

**What happens:**
1. Fetches ALL documents from Sanity (all subjects, all content)
2. Regenerates ALL TTL files completely
3. Overwrites existing files entirely
4. Creates large Git commits even for small changes

**This is fine for:**
- ✅ Initial setup and testing
- ✅ Ensuring consistency (no stale data)
- ✅ Simple, reliable operation

**But has drawbacks:**
- ❌ Inefficient (rewrites everything)
- ❌ Large Git diffs (hard to review)
- ❌ Can't target specific subjects
- ❌ Slower as dataset grows

## Update Strategy Options

### Strategy 1: Full Replacement (Current - Simplest)

**How it works:**
- Fetches all data
- Regenerates all files
- Replaces everything

**Use when:**
- Setting up initially
- Major restructuring
- You want guaranteed consistency
- Dataset is small (<10 subjects)

**Example:**
```bash
python scripts/sanity_to_ttl.py --sample
```

**Git result:**
```
Modified: data/national-curriculum-for-england/programme-structure.ttl
Modified: data/national-curriculum-for-england/themes.ttl
Modified: data/national-curriculum-for-england/subjects/science/science-subject.ttl
Modified: data/national-curriculum-for-england/subjects/science/science-knowledge-taxonomy.ttl
Modified: data/national-curriculum-for-england/subjects/science/science-schemes.ttl
Modified: data/national-curriculum-for-england/subjects/history/history-subject.ttl
# ... etc (many files)
```

---

### Strategy 2: Subject-Level Scoping (Recommended Next Step)

**How it works:**
- You specify which subjects to update
- Only those subject files are regenerated
- Programme structure updated separately

**Use when:**
- Working on one subject at a time
- DfE authors are domain-specialists (science team, history team)
- You want smaller, focused commits
- Multiple teams working in parallel

**Example:**
```bash
# Update only science
python scripts/sanity_to_ttl.py --api --subjects science

# Update science and history
python scripts/sanity_to_ttl.py --api --subjects science,history

# Update everything (same as no filter)
python scripts/sanity_to_ttl.py --api --subjects all

# Update programme structure only
python scripts/sanity_to_ttl.py --api --subjects _programme_structure
```

**Git result:**
```bash
# Only science files changed
Modified: data/national-curriculum-for-england/subjects/science/science-subject.ttl
Modified: data/national-curriculum-for-england/subjects/science/science-knowledge-taxonomy.ttl
Modified: data/national-curriculum-for-england/subjects/science/science-schemes.ttl
```

**Implementation:**
See `scripts/sanity_to_ttl_enhanced.py` for a working example.

---

### Strategy 3: Incremental Updates (Most Efficient)

**How it works:**
- Tracks last successful run timestamp
- Queries Sanity for documents with `_updatedAt > last_run_time`
- Only fetches and processes changed documents
- Regenerates only affected files

**Use when:**
- Dataset is large (10+ subjects)
- Running on schedule (daily/hourly)
- You want minimal Git noise
- API call limits are a concern

**Example:**
```bash
# First run - fetches everything
python scripts/sanity_to_ttl.py --api --incremental

# Subsequent runs - only changed documents
python scripts/sanity_to_ttl.py --api --incremental
```

**How it tracks changes:**
```
scripts/.last-run-timestamp
---
# Last successful run
2025-12-20T13:30:00Z
```

**Sanity query example:**
```javascript
// Fetch only documents changed since last run
*[_type == "contentDescriptor" && _updatedAt > "2025-12-20T13:30:00Z"]
```

**Git result:**
```bash
# Only files with actual changes
Modified: data/national-curriculum-for-england/subjects/science/science-knowledge-taxonomy.ttl
# (Only science-knowledge-taxonomy changed because a content descriptor was edited)
```

---

### Strategy 4: Hybrid Approach (Best for Production)

**Combine subject-level + incremental:**

```bash
# Update only science, but only what changed
python scripts/sanity_to_ttl.py --api --subjects science --incremental
```

**Benefits:**
- ✅ Efficient (only changed documents)
- ✅ Targeted (specific subject)
- ✅ Clean Git history
- ✅ Fast execution

**Use when:**
- In production with multiple subjects
- Multiple author teams working simultaneously
- You want maximum control and efficiency

---

## Handling Dependencies

### Problem: Cross-Document Changes

When you change one document, related documents may need updating:

**Example scenario:**
1. You update a `strand` document
2. All `substrands` that reference it should be regenerated
3. All `contentDescriptors` in those substrands should be regenerated
4. All `schemes` that include those descriptors should be regenerated

**Current approach (simple):**
- Update at the **subject level** (all of science together)
- This catches all dependencies within a subject

**Future enhancement (complex):**
- Build dependency graph
- Track which documents reference which
- Regenerate entire dependency chain

### Dependency Relationships

```
Subject (science)
  ├─→ Disciplines
  │     ├─→ Strands
  │     │     ├─→ SubStrands
  │     │     │     ├─→ ContentDescriptors
  │     │     │     │     └─→ ContentSubDescriptors
  │     │     │     └─→ Schemes (references descriptors)
  │
  └─→ SubSubjects
        ├─→ Strands (references)
        └─→ Schemes
              └─→ KeyStages (references)
```

**If you change a Strand:**
- Must regenerate: SubStrands, ContentDescriptors, Schemes
- Safe approach: Regenerate entire subject

---

## Handling Deletions

### Problem: Detecting Deleted Content

When someone deletes a document in Sanity, how do you remove it from TTL?

**Strategy 1: Full Replacement (Current)**
- ✅ Deletions handled automatically
- Document not in Sanity → Not in generated TTL
- Simple and reliable

**Strategy 2: Incremental Updates**
- ❌ Deletion not detected (document just stops appearing in queries)
- Need explicit deletion tracking

**Solutions for incremental:**

**Option A: Periodic full sync**
```bash
# Daily: incremental
python scripts/sanity_to_ttl.py --api --incremental

# Weekly: full replacement (catches deletions)
python scripts/sanity_to_ttl.py --api --subjects all
```

**Option B: Sanity webhooks for deletions**
```javascript
// Sanity webhook config
{
  on: ['delete'],
  filter: '_type in ["contentDescriptor", "scheme", ...]',
  // Sends notification when document deleted
}
```

**Option C: Compare document IDs**
```python
# Pseudocode
existing_ids = extract_ids_from_ttl_files()
sanity_ids = fetch_all_ids_from_sanity()
deleted_ids = existing_ids - sanity_ids
# Remove entities with deleted_ids from TTL
```

**Recommendation:** Use **Option A** (periodic full sync) - simplest and most reliable.

---

## Practical Workflows

### Workflow 1: Small Team, Few Subjects (Current)

```bash
# Authors publish content in Sanity
# Run manually or on schedule
python scripts/sanity_to_ttl.py --api

# Review and commit
git diff
git add data/
git commit -m "Update curriculum content"
git push
```

**Frequency:** Weekly or when major changes made

---

### Workflow 2: Large Team, Many Subjects

```bash
# Science team publishes
python scripts/sanity_to_ttl.py --api --subjects science

# History team publishes
python scripts/sanity_to_ttl.py --api --subjects history

# Each creates separate commit
git add data/national-curriculum-for-england/subjects/science/
git commit -m "Update science curriculum"

git add data/national-curriculum-for-england/subjects/history/
git commit -m "Update history curriculum"
```

**Frequency:** Daily or per-team schedule

---

### Workflow 3: Continuous Integration (Automated)

**GitHub Actions runs on schedule:**

```yaml
# .github/workflows/sanity-to-ttl.yml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  update:
    steps:
      - name: Incremental update
        run: python scripts/sanity_to_ttl.py --api --incremental

      - name: Full sync weekly
        if: github.event.schedule == '0 0 * * 0'  # Sunday midnight
        run: python scripts/sanity_to_ttl.py --api --subjects all
```

**Benefits:**
- Automatic updates
- Incremental saves API calls
- Weekly full sync catches deletions
- Always up to date

---

## Testing Different Strategies

### Dry Run Mode

See what would be updated without making changes:

```bash
# Check what would be updated
python scripts/sanity_to_ttl_enhanced.py --api --subjects science --dry-run
```

Output:
```
============================================================
UPDATE SCOPE
============================================================

📊 Mode: Full update
📚 Subjects: science

📄 Documents to process:
   - disciplines: 1
   - strands: 2
   - substrands: 3
   - contentDescriptors: 5
   - schemes: 2

============================================================
🔍 DRY RUN - No files will be modified
```

---

## Performance Comparison

### Small dataset (1-2 subjects)

| Strategy | API Calls | Time | Git Diff Size |
|----------|-----------|------|---------------|
| Full replacement | ~10 | 5s | ~1000 lines |
| Subject-level | ~5 | 3s | ~500 lines |
| Incremental | ~2 | 1s | ~100 lines |

### Large dataset (10+ subjects)

| Strategy | API Calls | Time | Git Diff Size |
|----------|-----------|------|---------------|
| Full replacement | ~100 | 60s | ~10,000 lines |
| Subject-level | ~10 | 8s | ~1,000 lines |
| Incremental | ~3 | 2s | ~200 lines |

**Conclusion:** Incremental + subject-level is 20-30x faster for large datasets.

---

## Recommendations by Use Case

### Starting Out (You are here)
**Use:** Full replacement (current script)
```bash
python scripts/sanity_to_ttl.py --sample  # Testing
python scripts/sanity_to_ttl.py --api     # Production
```

**Why:** Simple, reliable, good for initial setup

---

### Growing (2-5 subjects)
**Use:** Subject-level scoping
```bash
python scripts/sanity_to_ttl.py --api --subjects science
```

**Why:** Smaller commits, team-based workflow

---

### Mature (5+ subjects, daily updates)
**Use:** Incremental + subject-level
```bash
# Daily automated
python scripts/sanity_to_ttl.py --api --incremental

# Weekly full sync
python scripts/sanity_to_ttl.py --api --subjects all
```

**Why:** Efficient, scales well, clean Git history

---

## Migration Path

**Phase 1 (Now):** Use current script with full replacement
- Get Sanity integration working
- Validate data quality
- Establish workflow

**Phase 2 (1-2 months):** Add subject-level scoping
- Implement filtering in queries
- Test with science and history
- Train teams on focused updates

**Phase 3 (3-6 months):** Enable incremental updates
- Add timestamp tracking
- Configure scheduled runs
- Monitor for deletion edge cases
- Add weekly full sync as safety net

---

## Summary

| Strategy | Complexity | Efficiency | Use Case |
|----------|------------|------------|----------|
| **Full Replacement** | ⭐ Simple | ⭐ Slow | Initial setup, small datasets |
| **Subject-Level** | ⭐⭐ Medium | ⭐⭐ Medium | Team-based, parallel work |
| **Incremental** | ⭐⭐⭐ Complex | ⭐⭐⭐ Fast | Production, large datasets |
| **Hybrid** | ⭐⭐⭐ Complex | ⭐⭐⭐ Very Fast | Best for production |

**Start simple, add complexity as needed.**

The current script gives you full replacement out of the box. When you're ready for more control, use the enhanced version with `--subjects` and `--incremental` flags.
