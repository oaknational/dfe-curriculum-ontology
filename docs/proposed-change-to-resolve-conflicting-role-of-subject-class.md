# Subject/Discipline Separation: Architectural Refinement for World-Class Ontology

**Version:** 1.0  
**Date:** December 2025  
**Status:** Proposed Enhancement

---

## Executive Summary

The current curriculum ontology has a structural ambiguity that prevents it from being considered world-class: the `Subject` class is performing two distinct ontological roles simultaneously. This document proposes a straightforward architectural refinement that separates these concerns, dramatically improving the model's clarity, queryability, and alignment with semantic web best practices.

**The Fix:** Introduce a new `Discipline` class to handle knowledge taxonomy, while `Subject` focuses solely on programme structure.

**Impact:** This change transforms the ontology from technically compromised to architecturally sound, with minimal practical disruption to DfE's current implementation.

---

## The Problem: One Class, Two Jobs

### Current Situation

In the existing ontology, `Subject` (e.g., "Science", "English") serves as:

1. **Top of the Programme Structure Hierarchy**
   - **Subject** → SubSubject → Scheme
   - Represents what gets taught organisationally

2. **Top of the Knowledge Taxonomy Hierarchy**  
   - **Subject** → Strand → SubStrand → ContentDescriptor → ContentSubDescriptor
   - Represents how knowledge is conceptually organised

This means a single entity like `eng:subject-science` is simultaneously:
- A programme structure component (answering "What do students study?")
- A knowledge taxonomy root (answering "How is scientific knowledge organised?")

### Why This Is Problematic

#### 1. **Semantic Confusion**

The dual role creates fundamental ambiguity:
- When you reference "Subject", which hierarchy are you navigating?
- Properties and relationships become context-dependent
- Third parties must understand implicit conventions rather than explicit structure

**Example:** The property `curric:hasStrand` connects Subject to knowledge structure, but `curric:isPartOf` 
connects it to programme structure. This mixing of concerns is architecturally unclear.

#### 2. **Query Complexity**

Practical SPARQL queries become unnecessarily complex:

```sparql
# Current model: Ambiguous queries
SELECT ?content WHERE {
  ?subject a curric:Subject .
  ?subject ?relationship ?content .
  # Which relationships? Which hierarchy?
}
```

Users must know implicit rules about which properties belong to which conceptual model.

#### 3. **SKOS/RDFS Hybrid Confusion**

- Subject is both an `owl:Class` (for programme structure) and a `skos:Concept` (for knowledge taxonomy)
- This dual typing is technically valid but semantically muddled
- It violates the principle of separation of concerns

#### 4. **SHACL Validation Complications**

Writing validation constraints becomes convoluted:
- Constraints for programme structure vs. knowledge structure must be artificially separated
- Shape definitions become overloaded with conditional logic
- Maintenance burden increases significantly

#### 5. **Rigidity for Future Evolution**

The current model locks us into a 1:1 relationship between programme subjects and knowledge disciplines. This prevents potential future scenarios, such as:
- Splitting "Science" (as taught) from separate "Biology", "Chemistry", "Physics" knowledge taxonomies
- Splitting "English" (as taught) from separate "English" and "Drama" knowledge taxonomies
- Cross-cutting knowledge organisation that doesn't match teaching structures

---

## The Solution: Introduce `Discipline`

### Proposed Architecture

**Create a clean separation:**

1. **Subject** (Programme Structure)
   - **Subject** → SubSubject → Scheme
   - Focus: "What is taught and when?"
   - Properties: programme structure relationships (partOf, isPartOf)

2. **Discipline** (Knowledge Taxonomy)
   - **Discipline** → Strand → SubStrand → ContentDescriptor
   - Focus: "How is knowledge organised?"
   - Properties: SKOS relationships (broader, narrower, related)

3. **Bridge Relationship**
   - New property: `curric:hasDiscipline` / `curric:isDisciplineOf`
   - This would be a 1:1 mapping (e.g., `subject-science` → `discipline-science`)
   - This cardinality could be relaxed in the future to enable re-structuring of the knowledge taxonomy

4. **DfE's Impact:**
- No functional change because of the 1:1 mapping
- No impact on authoring process or data requirements
- No additional entities (just separated)

### Implementation Approach

#### Core Ontology Changes

```turtle
# New class definition
curric:Discipline
  rdf:type owl:Class ;
  rdfs:subClassOf skos:Concept ;
  rdfs:label "Discipline"@en ;
  rdfs:comment "A discipline representing a domain of knowledge."@en ;
  rdfs:isDefinedBy curric: .

# New relationship
curric:hasDiscipline
  rdf:type owl:ObjectProperty ;
  rdfs:label "has discipline"@en ;
  rdfs:comment "Indicates that a subject corresponds to a discipline of knowledge."@en ;
  rdfs:domain curric:Subject ;
  rdfs:range curric:Discipline ;
  owl:inverseOf curric:isDisciplineOf ;
  rdfs:isDefinedBy curric: .
```

#### Instance Implementation

```turtle
# Programme structure
eng:subject-science
  a curric:Subject ;
  rdfs:label "Science"@en ;
  curric:hasDiscipline eng:discipline-science ;
  # Programme structure properties only
  curric:isPartOf eng:key-stage-3 .

# Knowledge taxonomy
eng:discipline-science
  a skos:Concept, curric:Discipline ;
  skos:prefLabel "Science"@en ;
  skos:inScheme eng:knowledge-taxonomy ;
  skos:topConceptOf eng:knowledge-taxonomy ;
  # Knowledge structure only
  skos:narrower eng:strand-structure-function-living-organisms .
```

#### SHACL Constraint (Enforcing 1:1)

```turtle
# Ensure Subject-Discipline correspondence
:SubjectDisciplineShape
  a sh:NodeShape ;
  sh:targetClass curric:Subject ;
  sh:property [
    sh:path curric:hasDiscipline ;
    sh:minCount 1 ;
    sh:maxCount 1 ;  # Enforces 1:1 for DfE requirements
    sh:class curric:Discipline ;
  ] .
```

---

## Why This Makes the Model World-Class

### 1. **Ontological Clarity**

Each class has a single, well-defined purpose:
- Clear semantics: no ambiguity about what each entity represents
- Self-documenting: third parties immediately understand the structure
- Follows semantic web best practices for vocabulary design

### 2. **Improved Queryability**

Queries become intuitive and efficient:

```sparql
# Programme structure query
SELECT ?subject ?keyStage WHERE {
  ?subject a curric:Subject ;
           curric:isPartOf ?keyStage .
}

# Knowledge taxonomy query
SELECT ?discipline ?strand WHERE {
  ?discipline a curric:Discipline ;
              skos:narrower ?strand .
}

# Bridge query
SELECT ?subject ?knowledge WHERE {
  ?subject curric:hasDiscipline ?discipline ;
           curric:isPartOf ?keyStage .
  ?discipline skos:narrower ?strand .
}
```

### 3. **Proper SKOS Alignment**

- Knowledge taxonomy is now a proper SKOS ConceptScheme
- Discipline sits correctly as `skos:topConcept`
- All knowledge relationships use appropriate SKOS properties
- Aligns with W3C Semantic Web standards

### 4. **Maintainable Constraints**

SHACL shapes become clean and focused:
- Programme structure shapes validate programme properties
- Knowledge taxonomy shapes validate SKOS properties
- No conditional logic based on implicit context

### 5. **Industry Recognition**

Semantic web experts and potential data consumers will recognise:
- Proper separation of concerns
- Adherence to ontology design patterns
- Professional-grade vocabulary engineering
- Alignment with linked data principles

---

## Recommendation

**We should implement this change before finalizing the National Curriculum ontology.**

This is the right time because:
- The model is still in active development (v0.1.0)
- Changes are surgical and well-contained
- Impact to downstream systems is minimal
- Benefit to overall quality is substantial

The alternative—leaving the model as-is—means:
- Permanently compromised architecture
- Ongoing complexity burden
- Reduced credibility with semantic web community
- Compromised future flexibility of knowledge taxonomy

---

## Conclusion

The Subject/Discipline separation transforms the National Curriculum ontology from technically acceptable to architecturally excellent. By cleanly separating programme structure from knowledge taxonomy, we create a model that is:

- **Clearer:** Self-explanatory and unambiguous
- **Queryable:** Intuitive and efficient
- **Standard:** Aligned with semantic web best practices
- **Future-proof:** Flexible for emerging requirements
- **Professional:** Ready for public scrutiny and reuse

In practical terms, from a DfE perspective, this proposed change is 'under-the-hood' and has no impact on the current work authoring the new National Curriculum. With the 1:1 constrain employed, the model is logically equivalent to the current agreed National Curriculum ontology.

**This is the architectural refinement results in an ontology that is demonstrably world-class.**
