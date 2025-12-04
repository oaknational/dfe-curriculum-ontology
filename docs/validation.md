# SHACL Validation Guide

This document explains how to validate UK Curriculum Ontology data using SHACL (Shapes Constraint Language).

## Table of Contents

- [Overview](#overview)
- [Running Validation](#running-validation)
- [Constraint Shapes](#constraint-shapes)
- [Common Validation Errors](#common-validation-errors)
- [Extending Constraints](#extending-constraints)

## Overview

[SHACL (Shapes Constraint Language)](https://www.w3.org/TR/shacl/) is a W3C standard for validating RDF graphs against a set of constraints. The UK Curriculum Ontology uses SHACL to ensure:

- **Data quality**: Required properties are present
- **Structural integrity**: Hierarchical relationships are correct
- **Business rules**: Domain-specific constraints are met (e.g., age boundaries)
- **Consistency**: Inverse relationships are properly maintained

### Ontology vs. Constraints

The **ontology** (`curriculum-ontology.ttl`) defines what _can_ be expressed using OWL classes and properties.

The **constraints** (`curriculum-constraints.ttl`) define what _must_ be expressed using SHACL shapes - enforcing policies and best practices that may evolve independently of the core ontology.

## Running Validation

### Using the Validation Script

The simplest way to validate your data:

```bash
./tools/validate.sh data/england/subjects/science/*.ttl
```

### Using Apache Jena SHACL

Install [Apache Jena](https://jena.apache.org/download/):

```bash
# Validate data files against constraints
shacl validate \
  --shapes=constraints/curriculum-constraints.ttl \
  --data=data/england/programme-structure.ttl \
  --data=data/england/subjects/science/science-subject.ttl \
  --data=data/england/subjects/science/science-knowledge-taxonomy.ttl \
  --data=data/england/subjects/science/science-schemes.ttl
```

### Using TopQuadrant SHACL

With [TopQuadrant SHACL](https://github.com/TopQuadrant/shacl):

```bash
# Install
npm install -g shacl

# Validate
shacl -d data/england/*.ttl \
      -s constraints/curriculum-constraints.ttl
```

### Using Python (pySHACL)

Install [pySHACL](https://github.com/RDFLib/pySHACL):

```bash
pip install pyshacl

# Validate
pyshacl -s constraints/curriculum-constraints.ttl \
        -d data/england/programme-structure.ttl \
        -df turtle
```

### Validation Output

Successful validation produces no output or a confirmation message.

Failed validation produces a validation report in RDF format:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .

[ a sh:ValidationReport ;
  sh:conforms false ;
  sh:result [
    a sh:ValidationResult ;
    sh:resultSeverity sh:Violation ;
    sh:focusNode eng:key-stage-3 ;
    sh:resultPath rdfs:label ;
    sh:resultMessage "Key stages must have an rdfs:label." ;
    sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
  ]
] .
```

## Constraint Shapes

The constraints file defines shapes for each major class. Here's what each shape validates:

### Phase Shape

**Target:** All instances of `curric:Phase`

**Constraints:**
- Must have at least one `rdfs:label` (language-tagged string)
- Must have exactly one `curric:lowerAgeBoundary` (non-negative integer)
- Must have exactly one `curric:upperAgeBoundary` (positive integer)
- Lower age must be less than upper age
- Age boundaries must be in reasonable range (0-25 years)

**Example violation:**
```turtle
eng:phase-invalid
  a curric:Phase ;
  # Missing rdfs:label - VIOLATION
  curric:lowerAgeBoundary 5 ;
  curric:upperAgeBoundary 11 .
```

### KeyStage Shape

**Target:** All instances of `curric:KeyStage`

**Constraints:**
- Must have at least one `rdfs:label`
- Must be part of exactly one `curric:Phase` via `curric:isPartOf`
- Must have exactly one `curric:lowerAgeBoundary`
- Must have exactly one `curric:upperAgeBoundary`
- Lower age must be less than upper age
- Age boundaries must fall within parent phase boundaries
- Must be used in at least one scheme (not orphaned)

**Example violation:**
```turtle
eng:key-stage-invalid
  a curric:KeyStage ;
  rdfs:label "Invalid KS" ;
  curric:isPartOf eng:phase-secondary ;
  curric:lowerAgeBoundary 11 ;
  curric:upperAgeBoundary 10 .  # VIOLATION: upper < lower
```

### YearGroup Shape

**Target:** All instances of `curric:YearGroup`

**Constraints:**
- Must have at least one `rdfs:label`
- Must be part of exactly one `curric:KeyStage` via `curric:isPartOf`
- Must have exactly one `curric:lowerAgeBoundary`
- Must have exactly one `curric:upperAgeBoundary`
- Lower age must be less than upper age
- Age boundaries must fall within parent key stage boundaries

### Subject Shape

**Target:** All instances of `curric:Subject`

**Constraints:**
- Must have at least one `rdfs:label` (language-tagged string)
- Must have at least one `skos:prefLabel` (language-tagged string)
- Must be in at least one `skos:ConceptScheme` via `skos:inScheme`
- May have zero or more `curric:hasStrand` relationships
- May have zero or more `curric:hasAim` statements
- Must be used in at least one sub-subject (not orphaned)

### SubSubject Shape

**Target:** All instances of `curric:SubSubject`

**Constraints:**
- Must have at least one `rdfs:label`
- Must be part of exactly one `curric:Subject` via `curric:isPartOf`
- May include zero or more `curric:Strand` via `curric:includesStrand`
- If `curric:includesStrand` is present, inverse `curric:applicableToSubSubject` must exist on the strand
- Must be used in at least one scheme (not orphaned)

### Scheme Shape

**Target:** All instances of `curric:Scheme`

**Constraints:**
- Must have at least one `rdfs:label`
- Must be part of at least one `curric:SubSubject` via `curric:isPartOf`
- Must have exactly one `curric:KeyStage` via `curric:hasKeyStage`
- May have zero or more `curric:ContentDescriptor` via `curric:hasContent`

**Example violation:**
```turtle
eng:scheme-invalid
  a curric:Scheme ;
  rdfs:label "Invalid Scheme" ;
  curric:isPartOf eng:subsubject-science ;
  curric:hasKeyStage eng:key-stage-3 , eng:key-stage-4 .  # VIOLATION: max 1 key stage
```

### Strand Shape

**Target:** All instances of `curric:Strand`

**Constraints:**
- Must have at least one `skos:prefLabel`
- Must be in exactly one `skos:ConceptScheme` via `skos:inScheme`
- Must have exactly one broader subject via `skos:broader`
- Must be applicable to at least one `curric:SubSubject` via `curric:applicableToSubSubject`
- Must have at least one narrower `curric:SubStrand` via `skos:narrower`
- If `curric:applicableToSubSubject` is present, inverse `curric:includesStrand` must exist on the sub-subject
- Must be referenced by at least one subject or sub-subject (not orphaned)

### SubStrand Shape

**Target:** All instances of `curric:SubStrand`

**Constraints:**
- Must have at least one `skos:prefLabel`
- Must be in exactly one `skos:ConceptScheme` via `skos:inScheme`
- Must have exactly one broader strand via `skos:broader`
- Must have at least one narrower `curric:ContentDescriptor` via `skos:narrower`
- Must be referenced by at least one strand via `skos:narrower` (not orphaned)

### ContentDescriptor Shape

**Target:** All instances of `curric:ContentDescriptor`

**Constraints:**
- Must have at least one `skos:prefLabel`
- Must be in exactly one `skos:ConceptScheme` via `skos:inScheme`
- Must have exactly one broader sub-strand via `skos:broader`
- May have zero or more narrower `curric:ContentSubDescriptor` via `skos:narrower`
- Must be used in at least one scheme OR referenced by at least one sub-strand (not orphaned)

### ContentSubDescriptor Shape

**Target:** All instances of `curric:ContentSubDescriptor`

**Constraints:**
- Must have at least one `skos:prefLabel`
- Must be in exactly one `skos:ConceptScheme` via `skos:inScheme`
- Must have exactly one broader content descriptor via `skos:broader`
- May have zero or more text examples via `curric:example`
- May have zero or more URL examples via `curric:exampleURL`
- Must be referenced by at least one content descriptor via `skos:narrower` (not orphaned)

### Theme Shape

**Target:** All instances of `curric:Theme`

**Constraints:**
- Must have at least one `skos:prefLabel`
- Must have at least one `skos:definition`
- Must be in exactly one `skos:ConceptScheme` via `skos:inScheme`
- Must be related to at least one content item via `skos:related` (not orphaned)

## Common Validation Errors

### Missing Required Labels

**Error message:** "Phases must have an rdfs:label."

**Cause:** The instance is missing a required label property.

**Fix:**
```turtle
# Before (invalid)
eng:my-phase a curric:Phase .

# After (valid)
eng:my-phase
  a curric:Phase ;
  rdfs:label "My Phase"@en .
```

### Age Boundary Issues

**Error message:** "Lower age boundary must be less than upper age boundary"

**Cause:** Age boundaries are inverted or equal.

**Fix:**
```turtle
# Before (invalid)
eng:my-keystage
  curric:lowerAgeBoundary 14 ;
  curric:upperAgeBoundary 11 .

# After (valid)
eng:my-keystage
  curric:lowerAgeBoundary 11 ;
  curric:upperAgeBoundary 14 .
```

### Cardinality Violations

**Error message:** "Every key stage must be part of exactly one phase."

**Cause:** Missing required relationship or too many relationships.

**Fix:**
```turtle
# Before (invalid - missing relationship)
eng:my-keystage a curric:KeyStage .

# After (valid)
eng:my-keystage
  a curric:KeyStage ;
  curric:isPartOf eng:phase-primary .
```

### Orphaned Entities

**Error message:** "Key stage is not used in any scheme (orphaned)"

**Cause:** A key stage exists but no scheme references it.

**Fix:** Create a scheme that uses the key stage:
```turtle
eng:scheme-science-my-keystage
  a curric:Scheme ;
  rdfs:label "Science - My Key Stage" ;
  curric:hasKeyStage eng:my-keystage ;
  curric:isPartOf eng:subsubject-science .
```

### Inverse Relationship Mismatches

**Error message:** "includesStrand must have corresponding applicableToSubSubject on the strand"

**Cause:** One direction of an inverse relationship is present but the other is missing.

**Fix:**
```turtle
# Both directions must be present
eng:subsubject-science curric:includesStrand eng:my-strand .
eng:my-strand curric:applicableToSubSubject eng:subsubject-science .
```

### Hierarchical Boundary Violations

**Error message:** "Year group age boundaries must fall within parent key stage boundaries"

**Cause:** A child entity has age boundaries outside its parent's range.

**Fix:**
```turtle
# Parent
eng:key-stage-3
  curric:lowerAgeBoundary 11 ;
  curric:upperAgeBoundary 14 .

# Before (invalid - 10 < 11)
eng:year-group-7
  curric:isPartOf eng:key-stage-3 ;
  curric:lowerAgeBoundary 10 ;
  curric:upperAgeBoundary 12 .

# After (valid)
eng:year-group-7
  curric:isPartOf eng:key-stage-3 ;
  curric:lowerAgeBoundary 11 ;
  curric:upperAgeBoundary 12 .
```

## Extending Constraints

### Adding New Shape Constraints

To add validation for a new class:

1. Define a new shape in `curriculum-constraints.ttl`:

```turtle
curric:MyNewClassShape
  a sh:NodeShape ;
  sh:targetClass curric:MyNewClass ;

  sh:property [
    sh:path rdfs:label ;
    sh:datatype rdf:langString ;
    sh:minCount 1 ;
    sh:message "MyNewClass must have a label." ;
  ] .
```

2. Test the constraint:

```bash
./tools/validate.sh data/my-new-data.ttl
```

### Adding Custom SPARQL Constraints

For complex validation logic, use SPARQL-based constraints:

```turtle
curric:MyCustomValidation
  sh:sparql [
    sh:message "Custom business rule violation" ;
    sh:select """
      PREFIX curric: <https://w3id.org/uk/curriculum/core/>
      SELECT $this WHERE {
        $this a curric:MyClass .
        # Complex validation logic here
        FILTER ( ... )
      }
    """ ;
  ] .
```

See the [SHACL Advanced Features](https://www.w3.org/TR/shacl/#sparql-constraints) specification for details.

### Severity Levels

SHACL supports three severity levels:

```turtle
sh:property [
  sh:path curric:myProperty ;
  sh:severity sh:Warning ;  # or sh:Violation (default), sh:Info
  sh:message "This is a warning, not an error." ;
] .
```

### Constraint Versioning

When constraints change:

1. Document the change in `CHANGELOG.md`
2. Save the previous version in `constraints/versions/`
3. Update the version info in the constraints ontology declaration
4. Consider backward compatibility - new constraints may invalidate previously valid data

## Validation in CI/CD

Example GitHub Actions workflow:

```yaml
name: Validate Curriculum Data

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Apache Jena
        run: |
          wget https://downloads.apache.org/jena/binaries/apache-jena-x.x.x.tar.gz
          tar xzf apache-jena-*.tar.gz
      - name: Run SHACL Validation
        run: |
          ./apache-jena-*/bin/shacl validate \
            --shapes=constraints/curriculum-constraints.ttl \
            --data=data/**/*.ttl
```

## Resources

- [SHACL Specification](https://www.w3.org/TR/shacl/) - W3C Recommendation
- [SHACL Playground](https://shacl.org/playground/) - Interactive testing environment
- [Apache Jena SHACL](https://jena.apache.org/documentation/shacl/) - Java implementation
- [pySHACL](https://github.com/RDFLib/pySHACL) - Python implementation
- [TopQuadrant SHACL](https://github.com/TopQuadrant/shacl) - JavaScript implementation

## Troubleshooting

**Problem:** Validation runs but reports no violations when there should be some

**Solution:** Check that:
- Your constraints file uses the correct namespace URIs
- Target classes match exactly (`curric:Phase`, not `Phase`)
- The data and shapes files are both being loaded

**Problem:** SPARQL-based constraints fail

**Solution:**
- Test the SELECT query independently first
- Ensure all prefixes are defined in the constraint
- Check that `$this` variable is used correctly (it's bound to the focus node)

**Problem:** Performance issues with large datasets

**Solution:**
- Use more specific target definitions instead of `sh:targetClass`
- Break validation into smaller batches
- Use a triple store for validation instead of in-memory processing
