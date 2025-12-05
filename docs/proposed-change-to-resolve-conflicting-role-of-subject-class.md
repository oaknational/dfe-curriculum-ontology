# Subject/Discipline Separation: Architectural Refinement for World-Class Ontology

**Version:** 1.0  
**Date:** December 2025  
**Audience:** Technical Management  
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
   - Phase → KeyStage → YearGroup → **Subject** → SubSubject → Scheme
   - Represents what gets taught organizationally

2. **Top of the Knowledge Taxonomy Hierarchy**  
   - **Subject** → Strand → SubStrand → ContentDescriptor → ContentSubDescriptor
   - Represents how knowledge is conceptually organized

This means a single entity like `eng:subject-science` is simultaneously:
- A programme structure component (answering "What do students study?")
- A knowledge taxonomy root (answering "How is scientific knowledge organized?")

### Why This Is Problematic

#### 1. **Semantic Confusion**

The dual role creates fundamental ambiguity:
- When you reference "Subject", which hierarchy are you navigating?
- Properties and relationships become context-dependent
- Third parties must understand implicit conventions rather than explicit structure

**Example:** The property `curric:hasStrand` connects Subject to knowledge structure, but `curric:isPartOf` might connect it to programme structure. This mixing of concerns is architecturally unclear.

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

The current model locks us into a 1:1 relationship between programme subjects and knowledge disciplines. This prevents potential future scenarios like:
- Splitting "Science" (as taught) from separate "Biology", "Chemistry", "Physics" knowledge taxonomies
- Merging "English" and "Drama" in the curriculum while maintaining separate knowledge structures
- Cross-cutting knowledge organization that doesn't match teaching structures

---

## The Solution: Introduce `Discipline`

### Proposed Architecture

**Create a clean separation:**

1. **Subject** (Programme Structure)
   - Phase → KeyStage → YearGroup → **Subject** → SubSubject → Scheme
   - Focus: "What is taught and when?"
   - Properties: programme structure relationships

2. **Discipline** (Knowledge Taxonomy)
   - ConceptScheme → **Discipline** → Strand → SubStrand → ContentDescriptor
   - Focus: "How is knowledge organized?"
   - Properties: SKOS relationships (broader, narrower, related)

3. **Bridge Relationship**
   - New property: `curric:hasDiscipline` / `curric:isDisciplineOf`
   - Currently 1:1 mapping (e.g., `subject-science` → `discipline-science`)
   - Future-proof for potential restructuring

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

### 5. **Future-Ready Architecture**

While DfE maintains 1:1 relationships now, the architecture supports:

**Scenario 1: Knowledge Granularity**
```turtle
eng:subject-science curric:hasDiscipline 
  eng:discipline-biology ,
  eng:discipline-chemistry ,
  eng:discipline-physics .
```

**Scenario 2: Cross-Cutting Disciplines**
```turtle
eng:subject-english curric:hasDiscipline eng:discipline-literacy .
eng:subject-drama curric:hasDiscipline eng:discipline-literacy .
```

**Scenario 3: Emerging Disciplines**
```turtle
eng:subject-computing curric:hasDiscipline 
  eng:discipline-computer-science ,
  eng:discipline-digital-literacy .
```

### 6. **Industry Recognition**

Semantic web experts and potential data consumers will recognize:
- Proper separation of concerns
- Adherence to ontology design patterns
- Professional-grade vocabulary engineering
- Alignment with linked data principles

This distinction elevates the ontology from "functional" to "exemplary".

---

## Why We Must Make This Change

### Current Model Is Not World-Class Because:

1. **Violates Single Responsibility Principle**
   - Subject does too many things
   - Mixed concerns throughout the model

2. **Creates Technical Debt**
   - Future enhancements require workarounds
   - Complexity compounds over time
   - Documentation burden increases

3. **Limits Interoperability**
   - Other organizations may misinterpret the model
   - Integration requires extensive explanation
   - Reduces reusability across contexts

4. **Complicates DfE Demonstration**
   - Harder to explain to stakeholders
   - Validation appears convoluted
   - Questions about architectural decisions

### Proposed Model Is World-Class Because:

1. **Clear Separation of Concerns**
   - Each class has one purpose
   - Relationships are unambiguous
   - Self-explanatory to newcomers

2. **Follows Best Practices**
   - Aligns with W3C standards
   - Uses SKOS appropriately
   - Implements proven patterns

3. **Enables Growth**
   - Future use cases don't require rework
   - Flexibility built into foundation
   - Extensible without breaking changes

4. **Professional Quality**
   - Ready for public consumption
   - Demonstrates technical excellence
   - Sets standard for UK curriculum data

---

## Implementation Impact

### Minimal Disruption

**For DfE's Current Use:**
- 1:1 mapping means no functional change
- Equivalent number of entities (just renamed/separated)
- All current queries still work (with minor updates)

**For the Demonstration:**
- Clearer explanation of architecture
- More confidence in technical decisions
- Better story for future applications

### Migration Path

1. **Phase 1:** Add Discipline class to core ontology
2. **Phase 2:** Create discipline instances alongside subjects
3. **Phase 3:** Move knowledge relationships from Subject to Discipline
4. **Phase 4:** Update SHACL constraints for both classes
5. **Phase 5:** Update documentation and examples

**Estimated effort:** 2-3 days for core changes, testing, and documentation

---

## Recommendation

**We should implement this change before finalizing the ontology for the DfE demonstration.**

This is the right time because:
- The model is still in active development (v0.1.0)
- Changes are surgical and well-contained
- Impact to downstream systems is minimal
- Benefit to overall quality is substantial

The alternative—leaving the model as-is—means:
- Permanently compromised architecture
- Ongoing complexity burden
- Reduced credibility with semantic web community
- Limited future flexibility

This isn't just a "nice to have" improvement—it's the difference between a functional ontology and a world-class one.

---

## Conclusion

The Subject/Discipline separation transforms our curriculum ontology from technically acceptable to architecturally excellent. By cleanly separating programme structure from knowledge taxonomy, we create a model that is:

- **Clearer:** Self-explanatory and unambiguous
- **Queryable:** Intuitive and efficient
- **Standard:** Aligned with semantic web best practices
- **Future-proof:** Flexible for emerging requirements
- **Professional:** Ready for public scrutiny and reuse

For DfE's immediate needs, this change introduces a 1:1 correspondence that maintains all current functionality while establishing a foundation for world-class curriculum data infrastructure.

**This is the architectural refinement that makes our ontology demonstrably world-class.**
