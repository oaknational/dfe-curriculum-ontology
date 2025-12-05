# Expected SHACL Validation Violations

This file documents the expected validation violations when running SHACL validation against `invalid-example.ttl`.

## Running the Test

```bash
shacl validate --shapes=../ontology/curriculum-constraints.ttl \
               --data=invalid-example.ttl
```

## Expected Violations

### 1. ex:phase-missing-label
- **Violation:** Missing rdfs:label
- **Shape:** curric:PhaseShape
- **Property:** rdfs:label
- **Constraint:** sh:minCount 1
- **Message:** "Phases must have an rdfs:label."

### 2. ex:phase-invalid-ages
- **Violation:** Lower age boundary not less than upper age boundary
- **Shape:** curric:PhaseShape
- **SPARQL Constraint:** Lower >= Upper check
- **Message:** "Lower age boundary must be less than upper age boundary"

### 3. ex:phase-unreasonable-age
- **Violation:** Age boundary outside reasonable range (0-25)
- **Shape:** curric:PhaseShape
- **SPARQL Constraint:** Age range check
- **Message:** "Age boundaries must be in reasonable range (0-25 years)"

### 4. ex:keystage-orphaned
- **Violation:** Missing curric:isPartOf
- **Shape:** curric:KeyStageShape
- **Property:** curric:isPartOf
- **Constraint:** sh:minCount 1
- **Message:** "Key stages must specify which phase they belong to."

### 5. ex:scheme-multiple-keystages
- **Violation:** Too many curric:hasKeyStage values (2, max is 1)
- **Shape:** curric:SchemeShape
- **Property:** curric:hasKeyStage
- **Constraint:** sh:maxCount 1
- **Message:** "Schemes must specify exactly which key stage they cover."

### 6. ex:keystage-outside-parent
- **Violation:** Age boundaries outside parent phase boundaries
- **Shape:** curric:KeyStageShape
- **SPARQL Constraint:** Child age bounds within parent check
- **Message:** "Key stage age boundaries must fall within parent phase boundaries"

### 7. ex:strand-missing-inverse
- **Violation:** Missing inverse relationship curric:applicableToSubSubject
- **Shape:** curric:StrandShape
- **Property:** curric:applicableToSubSubject
- **Constraint:** sh:minCount 1
- **Message:** "Strands must specify which sub-subject(s) they apply to."

### 8. ex:subject-missing-skos (Multiple violations)

**a. Missing skos:prefLabel**
- **Shape:** curric:SubjectShape
- **Property:** skos:prefLabel
- **Constraint:** sh:minCount 1
- **Message:** "Subjects must have a skos:prefLabel for SKOS taxonomy."

**b. Missing skos:inScheme**
- **Shape:** curric:SubjectShape
- **Property:** skos:inScheme
- **Constraint:** sh:minCount 1
- **Message:** "Subjects must specify which concept scheme they belong to."

### 9. ex:phase-wrong-datatype
- **Violation:** Wrong datatype for curric:lowerAgeBoundary ("five" instead of integer)
- **Shape:** curric:PhaseShape
- **Property:** curric:lowerAgeBoundary
- **Constraint:** sh:datatype xsd:nonNegativeInteger
- **Message:** Data type mismatch

### 10. ex:orphaned-keystage
- **Violation:** Key stage not used in any scheme
- **Shape:** curric:KeyStageShape
- **SPARQL Constraint:** Orphan check
- **Message:** "Key stage is not used in any scheme (orphaned)"

### 11. ex:orphaned-strand (Multiple violations)

**a. Not referenced by any subject**
- **Shape:** curric:StrandShape
- **SPARQL Constraint:** Orphan check
- **Message:** "Strand is not referenced by any subject or sub-subject (orphaned)"

**b. Missing curric:applicableToSubSubject**
- **Shape:** curric:StrandShape
- **Property:** curric:applicableToSubSubject
- **Constraint:** sh:minCount 1
- **Message:** "Strands must specify which sub-subject(s) they apply to."

### 12. ex:strand-no-children
- **Violation:** Missing skos:narrower (no child SubStrands)
- **Shape:** curric:StrandShape
- **Property:** skos:narrower
- **Constraint:** sh:minCount 1
- **Message:** "Strands must have at least one sub-strand."

### 13. ex:orphaned-theme
- **Violation:** Theme not related to any content
- **Shape:** curric:ThemeShape
- **SPARQL Constraint:** Content relationship check
- **Message:** "Theme is not related to any content (orphaned)"

### 14. ex:subject-no-lang-tag
- **Violation:** Missing language tag on skos:prefLabel
- **Shape:** curric:SubjectShape
- **Property:** skos:prefLabel
- **Constraint:** sh:datatype rdf:langString
- **Message:** Data type mismatch (expected rdf:langString)

## Summary

**Total Expected Violations:** 15+

(Exact number may vary depending on SHACL processor implementation)

## Notes

- Some entities may generate multiple violations
- SPARQL-based constraints may vary slightly between processors
- The order of violations in the report is not guaranteed
- Some processors may report additional implicit violations

## How to Use This File

1. Run SHACL validation on invalid-example.ttl
2. Compare the violations report with this expected list
3. Ensure all expected violations are detected
4. Use this as a test suite for validation tooling
