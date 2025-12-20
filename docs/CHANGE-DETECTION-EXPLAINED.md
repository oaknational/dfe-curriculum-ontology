# How Change Detection Works: Incremental Updates Explained

## Overview

The incremental update mechanism uses **timestamps** to detect what changed since the last run. This is simple but powerful.

## The Mechanism: Timestamp Comparison

### Step 1: Save Timestamp After Successful Run

```python
# scripts/sanity_to_ttl.py

def save_run_timestamp():
    """Save current time as 'last successful run'"""
    timestamp = datetime.now(timezone.utc).isoformat()

    with open('scripts/.last-run-timestamp', 'w') as f:
        f.write(timestamp)

    # File now contains: "2025-12-20T14:30:00Z"
```

**File content after run:**
```
scripts/.last-run-timestamp
───────────────────────────
2025-12-20T14:30:00Z
```

### Step 2: Read Timestamp on Next Run

```python
def get_last_run_timestamp():
    """Get when we last ran successfully"""
    with open('scripts/.last-run-timestamp', 'r') as f:
        return f.read().strip()

    # Returns: "2025-12-20T14:30:00Z"
```

### Step 3: Query Sanity for Changes

**Without incremental (fetches everything):**
```javascript
// GROQ query
*[_type == "contentDescriptor"]
// Returns: All 500 content descriptors
```

**With incremental (fetches only recent changes):**
```javascript
// GROQ query with time filter
*[_type == "contentDescriptor" && _updatedAt > "2025-12-20T14:30:00Z"]
// Returns: Only descriptors modified after 14:30
```

### Step 4: Sanity Returns Only Changed Documents

**Example scenario:**

```
Time: 14:30 - Last run completed
Time: 15:00 - Author edits "Biomechanics" descriptor
Time: 15:15 - Author edits "Seasonal changes" descriptor
Time: 16:00 - Script runs again (incremental)
```

**Query:**
```javascript
*[_type == "contentDescriptor" && _updatedAt > "2025-12-20T14:30:00Z"]
```

**Result:**
```json
[
  {
    "_id": "content-descriptor-biomechanics",
    "_updatedAt": "2025-12-20T15:00:00Z",  ← Modified at 15:00
    "prefLabel": "Biomechanics (UPDATED)",
    ...
  },
  {
    "_id": "content-descriptor-observe-seasonal-changes",
    "_updatedAt": "2025-12-20T15:15:00Z",  ← Modified at 15:15
    "prefLabel": "Observe changes across the 4 seasons (UPDATED)",
    ...
  }
]
// Only 2 documents returned (not all 500)
```

### Step 5: Regenerate Only Affected Files

The script identifies which subject these belong to and regenerates only those files:

```python
# Both descriptors are in Science
# So regenerate: science-knowledge-taxonomy.ttl
# Leave unchanged: history-knowledge-taxonomy.ttl, maths-knowledge-taxonomy.ttl
```

### Step 6: Save New Timestamp

```python
# After successful completion
save_run_timestamp()
# Now saves: "2025-12-20T16:00:00Z"
```

## Complete Example Timeline

```
┌─────────────────────────────────────────────────────────────┐
│ Monday 10:00 AM - First Run                                 │
├─────────────────────────────────────────────────────────────┤
│ 1. No .last-run-timestamp file exists                       │
│ 2. Script fetches ALL documents (full sync)                 │
│ 3. Generates all TTL files                                  │
│ 4. Saves timestamp: "2025-12-16T10:00:00Z"                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Monday 11:30 AM - Author Edits Content                      │
├─────────────────────────────────────────────────────────────┤
│ 1. Author updates "Biomechanics" descriptor in Sanity       │
│ 2. Sanity automatically sets:                               │
│    _updatedAt = "2025-12-16T11:30:00Z"                      │
│ 3. No script run yet - change sits in Sanity               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Monday 2:00 PM - Second Run (Incremental)                   │
├─────────────────────────────────────────────────────────────┤
│ 1. Reads .last-run-timestamp: "2025-12-16T10:00:00Z"        │
│ 2. Queries Sanity:                                          │
│    *[_updatedAt > "2025-12-16T10:00:00Z"]                   │
│ 3. Sanity returns: 1 document (Biomechanics)                │
│ 4. Script regenerates: science-knowledge-taxonomy.ttl       │
│ 5. Saves new timestamp: "2025-12-16T14:00:00Z"              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Monday 2:30 PM - Third Run (Incremental)                    │
├─────────────────────────────────────────────────────────────┤
│ 1. Reads .last-run-timestamp: "2025-12-16T14:00:00Z"        │
│ 2. Queries Sanity:                                          │
│    *[_updatedAt > "2025-12-16T14:00:00Z"]                   │
│ 3. Sanity returns: 0 documents (nothing changed)            │
│ 4. Script: "No changes detected, nothing to do"             │
│ 5. Still saves timestamp: "2025-12-16T14:30:00Z"            │
└─────────────────────────────────────────────────────────────┘
```

## How Sanity Knows What Changed

### Sanity's Built-in Change Tracking

Every document operation updates `_updatedAt`:

```javascript
// Author opens Sanity Studio
// Edits content descriptor
// Clicks "Save"

// Sanity automatically:
{
  "_id": "content-descriptor-biomechanics",
  "_updatedAt": "2025-12-20T11:30:00Z",  // ← OLD
  "_rev": "v5-abc123"                     // ← OLD
}

// After save:
{
  "_id": "content-descriptor-biomechanics",
  "_updatedAt": "2025-12-20T15:00:00Z",  // ← UPDATED
  "_rev": "v6-def456"                     // ← NEW REVISION
}
```

**Sanity tracks:**
- ✅ Field edits
- ✅ Reference changes
- ✅ Array modifications
- ✅ Document publishing (draft → published)
- ✅ Document unpublishing

**Sanity does NOT update timestamp for:**
- ❌ Just viewing the document
- ❌ Creating a draft (until published)
- ❌ Deleting (document disappears entirely)

## Complete Code Flow

```python
def fetch_incremental_changes():
    """Fetch only documents changed since last run"""

    # 1. Get last run time
    last_run = get_last_run_timestamp()
    # Returns: "2025-12-20T10:00:00Z"

    if not last_run:
        # First run - no timestamp file
        print("First run - fetching all documents")
        return fetch_all_documents()

    # 2. Build time-filtered queries
    queries = {
        'contentDescriptors': f'''
            *[_type == "contentDescriptor"
              && _updatedAt > "{last_run}"]
        ''',
        'schemes': f'''
            *[_type == "scheme"
              && _updatedAt > "{last_run}"]
        ''',
        # ... etc for all types
    }

    # 3. Execute queries
    changed_data = {}
    for key, query in queries.items():
        response = sanity_client.fetch(query)
        changed_data[key] = response

        print(f"Found {len(response)} changed {key}")

    # Example output:
    # Found 2 changed contentDescriptors
    # Found 0 changed schemes
    # Found 1 changed substrands

    return changed_data


def main():
    # Fetch changes
    data = fetch_incremental_changes()

    # Determine which subjects are affected
    affected_subjects = determine_affected_subjects(data)
    # Returns: ['science'] (based on document IDs)

    # Regenerate only affected subject files
    for subject in affected_subjects:
        regenerate_subject_files(subject, data)
        # Only regenerates science files

    # Save timestamp for next run
    save_run_timestamp()
    # Saves: "2025-12-20T16:00:00Z"
```

## GROQ Query Examples

### Basic Time Filter

```javascript
// Fetch content descriptors changed after specific time
*[_type == "contentDescriptor" && _updatedAt > "2025-12-20T10:00:00Z"]
```

### Multiple Document Types

```javascript
// Fetch any curriculum document type changed recently
*[_type in ["contentDescriptor", "scheme", "substrand"]
  && _updatedAt > "2025-12-20T10:00:00Z"]
```

### With Subject Filter

```javascript
// Only science documents changed recently
*[_type == "contentDescriptor"
  && _id match "**science**"
  && _updatedAt > "2025-12-20T10:00:00Z"]
```

### Include References

```javascript
// Fetch changed descriptors with their substrand info
*[_type == "contentDescriptor"
  && _updatedAt > "2025-12-20T10:00:00Z"]{
  ...,
  substrand->{
    _id,
    prefLabel
  }
}
```

## Edge Cases and Solutions

### 1. First Run (No Timestamp File)

**Problem:** No `.last-run-timestamp` file exists

**Solution:**
```python
last_run = get_last_run_timestamp()

if not last_run:
    # Fetch everything (same as full replacement)
    return fetch_all_documents()
else:
    # Incremental update
    return fetch_changes_since(last_run)
```

### 2. Failed Run (Script Crashes)

**Problem:** Script crashes before saving new timestamp

**Timeline:**
```
10:00 AM - Last successful run (timestamp saved)
11:00 AM - Author edits document
12:00 PM - Script runs, fetches changes, crashes before saving timestamp
01:00 PM - Script runs again
```

**What happens:**
```python
# 01:00 PM run
last_run = "2025-12-20T10:00:00Z"  # Still the 10:00 AM timestamp

# Query includes document from 11:00 AM again
# This is SAFE - document gets regenerated twice but no data loss
```

**Solution:** This is handled automatically - changes are re-fetched safely.

### 3. Clock Skew

**Problem:** Server clocks slightly different

**Sanity server:** 10:00:00.000Z
**Your server:** 10:00:01.500Z (1.5 seconds ahead)

**Risk:** Missing changes in that 1.5 second window

**Solution:** Add small buffer
```python
import timedelta

def save_run_timestamp():
    # Subtract 5 seconds as safety buffer
    timestamp = (datetime.now(timezone.utc) - timedelta(seconds=5)).isoformat()

    # Ensures we don't miss changes due to clock differences
```

### 4. Long-Running Script

**Problem:** Script takes 10 minutes to run

```
Start: 10:00 AM (reads last timestamp: 09:00 AM)
During run: Author edits document at 10:05 AM
End: 10:10 AM (saves timestamp: 10:10 AM)
```

**Risk:** Edit at 10:05 AM wasn't in the query results but timestamp moved past it

**Solution:** Capture start time
```python
def main():
    # Capture start time BEFORE querying
    run_start = datetime.now(timezone.utc)

    # Fetch changes
    last_run = get_last_run_timestamp()  # 09:00 AM
    data = fetch_changes_since(last_run)

    # ... process data (takes 10 minutes) ...

    # Save the start time, not end time
    save_timestamp(run_start)  # 10:00 AM

    # Next run will catch the 10:05 AM edit
```

### 5. Deletions Not Detected

**Problem:** Deleted documents don't have `_updatedAt` (they're gone)

```javascript
// Query for changes
*[_type == "contentDescriptor" && _updatedAt > "2025-12-20T10:00:00Z"]

// Returns: [] (deleted documents don't exist to be returned)
```

**Solution:** Periodic full sync
```bash
# Daily: Incremental
0 */6 * * * python sanity_to_ttl.py --incremental

# Weekly: Full sync (catches deletions)
0 0 * * 0 python sanity_to_ttl.py --subjects all
```

## Performance Comparison

### Full Sync (No Change Detection)

```
Query: *[_type == "contentDescriptor"]
Returns: 500 documents
Network: ~2 MB
Time: 5 seconds
Regenerates: ALL files
```

### Incremental (2 changes in last hour)

```
Query: *[_type == "contentDescriptor" && _updatedAt > "2025-12-20T10:00:00Z"]
Returns: 2 documents
Network: ~8 KB
Time: 0.5 seconds
Regenerates: Only affected files
```

**Speedup: 10x faster**

## Monitoring Changes

### See What Changed Recently

```bash
# Query Sanity directly to see recent changes
curl "https://PROJECT.api.sanity.io/v2021-10-21/data/query/production?query=*[_updatedAt > '2025-12-20T10:00:00Z']{_id, _type, _updatedAt}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check Last Run Time

```bash
cat scripts/.last-run-timestamp
# Output: 2025-12-20T14:30:00Z
```

### Dry Run to Preview

```bash
# See what would be updated without making changes
python scripts/sanity_to_ttl.py --api --incremental --dry-run
```

Output:
```
Last run: 2025-12-20T10:00:00Z
Changes found:
  - contentDescriptors: 2 documents
  - schemes: 0 documents

Would regenerate:
  - data/.../subjects/science/science-knowledge-taxonomy.ttl

DRY RUN - No files modified
```

## Summary

**Change detection uses:**
1. ✅ Sanity's automatic `_updatedAt` field
2. ✅ Local `.last-run-timestamp` file
3. ✅ GROQ time-filtered queries
4. ✅ Timestamp comparison logic

**The script knows what changed because:**
- Sanity tells it (via `_updatedAt` field)
- We ask for "documents newer than X"
- Sanity returns only matching documents

**No complex change tracking needed** - Sanity does all the work!

**Trade-off:**
- ✅ Simple and reliable
- ✅ Built into Sanity
- ⚠️ Deletions need periodic full sync
- ⚠️ Clock skew needs buffering
