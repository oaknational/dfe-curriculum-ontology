# Sanity Update Strategies - Quick Reference

## The Three Main Approaches

### 1️⃣ Full Replacement (Current Default)

```bash
python scripts/sanity_to_ttl.py --sample   # Test mode
python scripts/sanity_to_ttl.py --api      # Production
```

```
Sanity Content Lake          TTL Files
┌─────────────────┐         ┌─────────────────┐
│ ALL subjects    │  ────>  │ ALL files       │
│ ALL content     │  Fetch  │ OVERWRITTEN     │
│ (500 docs)      │  All    │ (complete       │
└─────────────────┘         │  replacement)   │
                            └─────────────────┘

Git Commit:
  Modified: 20 files (large diff)
```

**When to use:**
- ✅ Initial setup
- ✅ Testing
- ✅ Small datasets (< 5 subjects)
- ✅ Weekly/monthly updates
- ✅ You want guaranteed consistency

**Pros:** Simple, reliable, no stale data
**Cons:** Slow, large Git diffs, rewrites unchanged data

---

### 2️⃣ Subject-Level Scoping

```bash
python scripts/sanity_to_ttl.py --api --subjects science
python scripts/sanity_to_ttl.py --api --subjects science,history
```

```
Sanity Content Lake          TTL Files
┌─────────────────┐         ┌─────────────────┐
│ Science only    │  ────>  │ Science files   │
│ (100 docs)      │  Fetch  │ ONLY            │
│                 │  Filter │ (targeted       │
│ [History]       │         │  update)        │
│ [Maths]         │         │                 │
└─────────────────┘         └─────────────────┘

Git Commit:
  Modified: data/.../subjects/science/*.ttl (3 files)
```

**When to use:**
- ✅ Multiple subjects (5-20)
- ✅ Team-based workflow (science team, history team)
- ✅ Daily/weekly updates per subject
- ✅ Parallel development
- ✅ You want cleaner Git history

**Pros:** Targeted updates, smaller commits, team-friendly
**Cons:** Must specify subjects, still rewrites subject data

---

### 3️⃣ Incremental Updates

```bash
# First run - fetches all
python scripts/sanity_to_ttl.py --api --incremental

# Subsequent runs - only changed docs
python scripts/sanity_to_ttl.py --api --incremental
```

```
Sanity Content Lake          Timestamp         TTL Files
┌─────────────────┐         ┌─────────┐       ┌─────────────────┐
│ Changed since   │         │ Last:   │       │ Only affected   │
│ last run        │  ────>  │ 2:00 PM │ ───>  │ files           │
│ (5 docs)        │  Query  │ Today   │ Regen │ (minimal        │
│                 │  Recent └─────────┘       │  changes)       │
│ [499 unchanged] │                           └─────────────────┘
└─────────────────┘
                            Saves new timestamp

Git Commit:
  Modified: data/.../science-knowledge-taxonomy.ttl (1 file)
  (Only the file with changed content descriptors)
```

**When to use:**
- ✅ Large datasets (20+ subjects)
- ✅ Frequent updates (hourly/daily automated)
- ✅ You want minimal Git noise
- ✅ API rate limits are a concern
- ✅ Continuous integration

**Pros:** Very efficient, minimal diffs, fast
**Cons:** More complex, needs deletion handling, requires timestamp tracking

---

## Comparison Table

| Feature | Full Replacement | Subject-Level | Incremental |
|---------|-----------------|---------------|-------------|
| **Complexity** | ⭐ Simple | ⭐⭐ Medium | ⭐⭐⭐ Complex |
| **Speed (large dataset)** | 60s | 10s | 2s |
| **API Calls** | 100+ | 10-20 | 1-5 |
| **Git Diff Size** | ~10,000 lines | ~1,000 lines | ~200 lines |
| **Handles Deletions** | ✅ Automatic | ✅ Automatic | ⚠️ Needs extra work |
| **Setup Required** | None | Minimal | Timestamp tracking |
| **Best For** | < 5 subjects | 5-20 subjects | 20+ subjects |

---

## Hybrid Approach (Best for Production)

```bash
# Daily: Incremental updates for speed
python scripts/sanity_to_ttl.py --api --incremental

# Weekly: Full replacement to catch deletions
python scripts/sanity_to_ttl.py --api --subjects all
```

**Benefits:**
- ✅ 90% of runs are fast (incremental)
- ✅ Weekly full sync ensures consistency
- ✅ Deletions handled automatically
- ✅ Clean Git history most of the time

---

## Handling Deletions

### The Problem

When someone deletes a content descriptor in Sanity:

```
Sanity (Before)              Sanity (After)
┌──────────────┐            ┌──────────────┐
│ Descriptor A │            │ Descriptor A │
│ Descriptor B │ DELETE B   │ [deleted]    │
│ Descriptor C │   ───>     │ Descriptor C │
└──────────────┘            └──────────────┘

Question: How does the script know B was deleted?
```

### Solutions

**Full Replacement:** ✅ Handles automatically
- Regenerates everything from Sanity
- If it's not in Sanity, it's not in TTL

**Incremental:** ⚠️ Needs help
- Query only shows A and C (B not "updated", just gone)
- Script doesn't know B existed
- B remains in TTL file (stale data!)

**Solution: Hybrid schedule**
```bash
# Mon-Sat: Fast incremental
0 8 * * 1-6 python sanity_to_ttl.py --api --incremental

# Sunday: Full sync catches deletions
0 8 * * 0 python sanity_to_ttl.py --api --subjects all
```

---

## Current vs. Enhanced Script

### Current Script: `scripts/sanity_to_ttl.py`

```bash
# Only supports full replacement
python scripts/sanity_to_ttl.py --sample
python scripts/sanity_to_ttl.py --api
```

**What it does:**
- Fetches ALL data
- Generates ALL TTL files
- Simple, proven, ready to use

---

### Enhanced Script: `scripts/sanity_to_ttl_enhanced.py`

```bash
# All the new features
python scripts/sanity_to_ttl_enhanced.py --api --subjects science
python scripts/sanity_to_ttl_enhanced.py --api --incremental
python scripts/sanity_to_ttl_enhanced.py --api --subjects science --incremental
python scripts/sanity_to_ttl_enhanced.py --api --dry-run
```

**Additional features:**
- Subject filtering
- Incremental updates
- Timestamp tracking
- Dry-run mode (preview changes)
- Scope summary reporting

**Status:** Example/template showing the patterns
**To use:** Integrate the scope logic into your main script

---

## Migration Path

### Phase 1: Start Here (Week 1-4)
```bash
python scripts/sanity_to_ttl.py --api
```
- Use current script
- Full replacement mode
- Manual or scheduled weekly
- Get the basics working

### Phase 2: Add Filtering (Month 2-3)
```bash
python scripts/sanity_to_ttl.py --api --subjects science
```
- Add subject-level filtering to current script
- Science team, history team work independently
- Smaller, targeted commits

### Phase 3: Go Incremental (Month 4-6)
```bash
python scripts/sanity_to_ttl.py --api --incremental
```
- Add timestamp tracking
- Hourly/daily automated runs
- Weekly full sync as safety net

---

## Quick Decision Guide

**How many subjects?**
- 1-5 subjects → Full replacement
- 5-20 subjects → Subject-level
- 20+ subjects → Incremental

**How often updating?**
- Weekly/monthly → Full replacement
- Daily → Subject-level
- Hourly/real-time → Incremental

**Team structure?**
- Single team → Full replacement
- Multiple teams (by subject) → Subject-level
- Large org, many authors → Incremental

**Dataset size?**
- Small (< 500 docs) → Full replacement is fine
- Medium (500-2000 docs) → Subject-level
- Large (2000+ docs) → Incremental required

---

## Example Workflows

### Workflow A: Small Curriculum Project
```bash
# Authors publish changes in Sanity throughout week
# Friday afternoon: Generate TTL files
python scripts/sanity_to_ttl.py --api

# Review changes
git diff

# Commit and deploy
git commit -m "Week 50 curriculum updates"
git push
```

---

### Workflow B: Large Multi-Subject Curriculum
```bash
# Science team publishes Monday
python scripts/sanity_to_ttl.py --api --subjects science
git commit -m "Science: Add KS4 biology content"

# History team publishes Wednesday
python scripts/sanity_to_ttl.py --api --subjects history
git commit -m "History: Update Medieval period"

# Programme structure changed (affects all)
python scripts/sanity_to_ttl.py --api --subjects _programme_structure
git commit -m "Add new key stage"
```

---

### Workflow C: Automated CI/CD
```yaml
# .github/workflows/sanity-sync.yml

# Incremental: Every 6 hours
- cron: '0 */6 * * *'
  run: python sanity_to_ttl.py --api --incremental

# Full sync: Sunday midnight
- cron: '0 0 * * 0'
  run: python sanity_to_ttl.py --api --subjects all
```

---

## Summary

**Current script gives you:** Full replacement (simple, reliable)

**Enhanced version adds:** Subject filtering + incremental updates

**Recommended approach:**
1. Start with full replacement
2. Add subject filtering when you have 5+ subjects
3. Add incremental updates when running daily/hourly

**Key insight:** The script always does **FULL REGENERATION** of the files it touches. The scope control determines **WHICH** files get regenerated, not **HOW** they're regenerated.

For more details, see: `docs/SANITY-UPDATE-STRATEGIES.md`
