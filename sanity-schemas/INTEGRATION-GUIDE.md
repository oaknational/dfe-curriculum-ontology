# Sanity CMS Integration Guide

## Overview

This guide explains how to integrate Sanity CMS with the UK Curriculum Ontology repository, allowing DfE curriculum authors to use a user-friendly CMS interface while maintaining TTL file compatibility.

## What's Been Created

### 1. Sanity Schema Definitions (`sanity-schemas/`)

13 schema files that map directly to the ontology classes:

**Programme Structure:**
- `phase.js` → `curric:Phase`
- `keyStage.js` → `curric:KeyStage`
- `yearGroup.js` → `curric:YearGroup`

**Programme Hierarchy:**
- `subject.js` → `curric:Subject`
- `subsubject.js` → `curric:SubSubject`
- `scheme.js` → `curric:Scheme`
- `progression.js` → `curric:Progression`

**Knowledge Taxonomy:**
- `discipline.js` → `curric:Discipline`
- `strand.js` → `curric:Strand`
- `substrand.js` → `curric:SubStrand`
- `contentDescriptor.js` → `curric:ContentDescriptor`
- `contentSubdescriptor.js` → `curric:ContentSubDescriptor`
- `theme.js` → `curric:Theme`

**Key Features:**
- Validation rules matching SHACL constraints
- User-friendly labels and descriptions
- References between documents (no manual URI entry)
- Correct property patterns (rdfs:label vs skos:prefLabel)

### 2. Sample Data (`sanity-sample-data/sample-data.json`)

Example JSON showing what Sanity exports:
- 2 phases (Primary, Secondary)
- 2 key stages (KS3, KS4)
- Complete Science subject data
- Demonstrates all document types and relationships

### 3. Conversion Script (`scripts/sanity_to_ttl.py`)

Python script that converts Sanity JSON → TTL files:
- ✅ Handles all 13 document types
- ✅ Correct property patterns
- ✅ Proper URI generation
- ✅ Reference resolution
- ✅ Ontology metadata
- ✅ SHACL validation compliant
- ✅ Currently uses sample data (API calls commented out)

## Architecture

```
┌─────────────────────┐
│   DfE Authors       │
│   (Sanity Studio)   │
└──────────┬──────────┘
           │ Publish content
           ▼
┌─────────────────────┐
│   Sanity CMS        │  ← Content Lake (database)
│   (Content Lake)    │  ← User-friendly interface
└──────────┬──────────┘
           │ JSON export (API or webhook)
           ▼
┌─────────────────────┐
│  GitHub Actions     │  ← Triggered automatically
│  Run:               │
│  sanity_to_ttl.py   │  ← Convert JSON → TTL
│  validate.sh        │  ← SHACL validation
└──────────┬──────────┘
           │ If valid
           ▼
┌─────────────────────┐
│  GitHub Repository  │  ← TTL files committed
│  (Version Control)  │  ← Triggers deployment
└─────────────────────┘
```

## For Sanity Developers: Integration Steps

### 1. Copy Schemas to Sanity Project

```bash
# In your Sanity project directory
cp path/to/uk-curriculum-ontology/sanity-schemas/*.js schemas/
```

### 2. Register Schemas

In your `schema.js` or `schemaTypes/index.js`:

```javascript
// Import all schemas
import phase from './phase'
import keyStage from './keyStage'
import yearGroup from './yearGroup'
import subject from './subject'
import subsubject from './subsubject'
import discipline from './discipline'
import strand from './strand'
import substrand from './substrand'
import contentDescriptor from './contentDescriptor'
import contentSubdescriptor from './contentSubdescriptor'
import scheme from './scheme'
import progression from './progression'
import theme from './theme'

// Register in schema
export default createSchema({
  name: 'uk-curriculum',
  types: schemaTypes.concat([
    // Programme Structure
    phase,
    keyStage,
    yearGroup,

    // Programme Hierarchy
    subject,
    subsubject,
    scheme,
    progression,

    // Knowledge Taxonomy
    discipline,
    strand,
    substrand,
    contentDescriptor,
    contentSubdescriptor,
    theme,
  ])
})
```

### 3. Deploy to Sanity Studio

```bash
sanity deploy
```

### 4. Create API Token

1. Go to sanity.io/manage
2. Select your project
3. Go to Settings → API
4. Create a new token with **Read** permissions
5. Save the token securely

### 5. Configure GitHub Secrets

In your GitHub repository settings, add:
- `SANITY_PROJECT_ID` - Your Sanity project ID
- `SANITY_DATASET` - Usually "production"
- `SANITY_TOKEN` - The read token from step 4

## Testing the Conversion

### Run with Sample Data

```bash
python3 scripts/sanity_to_ttl.py --sample
```

This will:
1. Load `sanity-sample-data/sample-data.json`
2. Convert to TTL files
3. Output to `data/national-curriculum-for-england/`

### Run with Sanity API (once configured)

```bash
# Set environment variables
export SANITY_PROJECT_ID="your-project-id"
export SANITY_DATASET="production"
export SANITY_TOKEN="your-token"

# Run conversion
python3 scripts/sanity_to_ttl.py --api
```

### Validate Generated Files

```bash
./scripts/validate.sh
```

Expected output:
- ✅ TTL files are valid
- ⚠️  Warnings about orphaned themes (acceptable if themes aren't linked yet)

## Property Pattern Reference

**CRITICAL:** Different entity types use different RDF properties:

### Subjects, Schemes, Progressions (Programme entities)
```javascript
// Sanity schema
label: 'Science'
description: 'Science subject...'

// Becomes TTL
rdfs:label "Science"@en
rdfs:comment "Science subject..."@en
```

### Disciplines, Strands, Content (SKOS Concepts)
```javascript
// Sanity schema
prefLabel: 'Science'
definition: 'The systematic study...'
scopeNote: 'Science is essential...'

// Becomes TTL
skos:prefLabel "Science"@en
skos:definition "The systematic study..."@en
skos:scopeNote "Science is essential..."@en
```

## Validation Rules

The Sanity schemas enforce the same rules as SHACL constraints:

| Validation | Purpose |
|------------|---------|
| `Rule.required()` | Field must be filled |
| `Rule.min(1)` | At least one item in array |
| `type: 'reference'` | Must reference valid document |
| `Rule.positive()` | Number must be > 0 |
| `Rule.integer()` | Must be whole number |

## Triggering Conversion

### Option A: Manual (for testing)

Run the script manually when DfE publishes content.

### Option B: Scheduled (batch)

GitHub Actions runs daily:
```yaml
schedule:
  - cron: '0 2 * * *'  # 2am daily
```

### Option C: Webhook (real-time)

Sanity sends webhook on publish → GitHub Actions runs immediately.

**Recommended:** Start with Manual or Scheduled, then add Webhook once stable.

## File Output Structure

The conversion script creates:

```
data/national-curriculum-for-england/
├── programme-structure.ttl     (phases, key stages, year groups)
├── themes.ttl                   (cross-cutting themes)
└── subjects/
    └── science/
        ├── science-subject.ttl              (subject, subsubject)
        ├── science-knowledge-taxonomy.ttl   (disciplines, strands, content)
        └── science-schemes.ttl              (schemes, progressions)
```

## Data Entry Workflow for DfE Authors

1. **Log into Sanity Studio** (familiar CMS interface)
2. **Create/edit content** using forms (no TTL knowledge needed)
3. **Preview changes** in Sanity
4. **Publish** when ready
5. **GitHub Actions runs automatically** (or manually triggered)
6. **Validation** ensures data quality
7. **If valid:** TTL files committed to repository
8. **If invalid:** GitHub Issue created with error details

## Common Issues

### ID/Slug Mismatches

**Problem:** Document ID doesn't match expected pattern
**Solution:** Ensure slugs follow pattern: `{type}-{name}` (e.g., `subject-science`)

### Missing References

**Problem:** Reference to non-existent document
**Solution:** Create referenced documents first (bottom-up approach)

### Property Pattern Errors

**Problem:** Using `label` instead of `prefLabel` for SKOS concepts
**Solution:** Check document type - use correct field names per schema

### Validation Warnings

**Problem:** "Orphaned theme" warnings
**Solution:** These are acceptable if themes aren't linked to content yet

## Next Steps

1. **Share schemas with Sanity developers** - Send `sanity-schemas/` directory
2. **Review sample data** - Confirm JSON structure matches expectations
3. **Set up GitHub Actions** - Create workflow file (see below)
4. **Test with small dataset** - Add 1-2 subjects first
5. **Scale up** - Add remaining subjects once workflow is proven

## GitHub Actions Workflow

Create `.github/workflows/sanity-to-ttl.yml`:

```yaml
name: Convert Sanity JSON to TTL

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2am
  workflow_dispatch:       # Manual trigger

jobs:
  convert:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install rdflib pyshacl requests

      - name: Convert Sanity data to TTL
        env:
          SANITY_PROJECT_ID: ${{ secrets.SANITY_PROJECT_ID }}
          SANITY_DATASET: ${{ secrets.SANITY_DATASET }}
          SANITY_TOKEN: ${{ secrets.SANITY_TOKEN }}
        run: python scripts/sanity_to_ttl.py --api

      - name: Validate TTL
        run: ./scripts/validate.sh

      - name: Commit changes
        if: success()
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/
          git commit -m "Update curriculum data from Sanity" || exit 0
          git push
```

## Support

For questions or issues:
1. Check validation output: `./scripts/validate.sh`
2. Review generated TTL files manually
3. Compare with existing TTL files in `data/`
4. Check SHACL constraints: `ontology/dfe-curriculum-constraints.ttl`

## Summary

✅ Sanity schemas ready to use
✅ Conversion script tested and working
✅ Sample data validates successfully
✅ Ready for Sanity developer integration

No Firebase needed - Sanity Content Lake is your database!
