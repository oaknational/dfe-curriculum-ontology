# Conceptual Model

This document describes the classes, properties, and design decisions of the UK Curriculum Ontology.

## Table of Contents

- [Domain Overview](#domain-overview)
- [Class Hierarchy](#class-hierarchy)
- [Properties](#properties)
- [Design Decisions](#design-decisions)

## Domain Overview

The UK National Curriculum is organized into a structured framework that defines what students should learn at different stages of their education. The curriculum has two primary organizational dimensions:

1. **Programme Structure**: The temporal/organizational framework (when and how content is taught)
2. **Knowledge Structure**: The content itself (what is taught)

### Programme Structure

Education in England is divided into:
- **Phases**: Broad divisions (Primary: ages 5-11, Secondary: ages 11-16)
- **Key Stages**: Standardized learning stages (KS1 through KS4)
- **Year Groups**: Individual school years (Year 1 through Year 11)

### Knowledge Structure

Curriculum content is organized hierarchically:
- **Subjects**: Major disciplines (Science, Mathematics, History, etc.)
- **Strands**: Major organizational divisions within a subject
- **Sub-Strands**: Subdivisions of strands
- **Content Descriptors**: Specific statements of knowledge, concepts, or skills
- **Content Sub-Descriptors**: Detailed elaborations and examples

### Connecting Structure and Content

**Schemes** define what content is taught at each key stage for each subject. For example, "Science Key Stage 3" is a scheme that maps specific content descriptors to KS3.

**Themes** provide cross-cutting connections across subjects (e.g., Climate Change, Digital Literacy).

## Class Hierarchy

### Programme Structure Classes

```
curric:Phase
  ├─ eng:phase-primary
  └─ eng:phase-secondary

curric:KeyStage
  ├─ eng:key-stage-1
  ├─ eng:key-stage-2
  ├─ eng:key-stage-3
  └─ eng:key-stage-4

curric:YearGroup
  ├─ eng:year-group-1 through eng:year-group-11
```

**Phase** (`curric:Phase`)
- A broad phase of study in the UK education system
- Properties: `rdfs:label`, `curric:lowerAgeBoundary`, `curric:upperAgeBoundary`
- Example: Primary education (ages 5-11)

**KeyStage** (`curric:KeyStage`)
- A key stage that structures learning for specific age groups
- Properties: `rdfs:label`, `curric:isPartOf` (Phase), `curric:lowerAgeBoundary`, `curric:upperAgeBoundary`
- Example: Key Stage 3 (ages 11-14, Years 7-9)

**YearGroup** (`curric:YearGroup`)
- A single year of study within a key stage
- Properties: `rdfs:label`, `curric:isPartOf` (KeyStage), `curric:lowerAgeBoundary`, `curric:upperAgeBoundary`
- Example: Year 7 (ages 11-12)

### Knowledge Structure Classes

```
curric:Subject (subclass of skos:Concept)
  └─ curric:Strand (subclass of skos:Concept)
      └─ curric:SubStrand (subclass of skos:Concept)
          └─ curric:ContentDescriptor (subclass of skos:Concept)
              └─ curric:ContentSubDescriptor (subclass of skos:Concept)

curric:Theme (subclass of skos:Concept)
```

**Subject** (`curric:Subject`)
- A subject discipline (e.g., Science, Mathematics, History)
- Subclass of `skos:Concept` for integration with SKOS taxonomies
- Properties: `skos:prefLabel`, `skos:definition`, `curric:hasAim`, `curric:hasStrand`
- Example: Science subject with aims about developing scientific knowledge and understanding

**Strand** (`curric:Strand`)
- An organizational strand within a subject
- Properties: `skos:prefLabel`, `skos:broader` (Subject), `skos:narrower` (SubStrand), `curric:applicableToSubSubject`
- Example: "Structure and function of living organisms" in Science

**SubStrand** (`curric:SubStrand`)
- A subdivision of a strand
- Properties: `skos:prefLabel`, `skos:broader` (Strand), `skos:narrower` (ContentDescriptor)
- Example: "Cells and organisation" within the structure/function strand

**ContentDescriptor** (`curric:ContentDescriptor`)
- A specific statement of knowledge, concept, fact, or skill
- Properties: `skos:prefLabel`, `skos:broader` (SubStrand), `skos:narrower` (ContentSubDescriptor)
- Example: "Cells as the fundamental unit of living organisms, including how to observe, interpret and record cell structure using a light microscope"

**ContentSubDescriptor** (`curric:ContentSubDescriptor`)
- Elaboration or specific detail relating to a content descriptor
- Properties: `skos:prefLabel`, `skos:broader` (ContentDescriptor), `curric:example`, `curric:exampleURL`
- Example: Specific examples of cell observation techniques

**Theme** (`curric:Theme`)
- A cross-cutting theme spanning multiple subjects
- Properties: `skos:prefLabel`, `skos:definition`, `skos:related` (to content)
- Example: Climate Change and Sustainability

### Connecting Classes

**SubSubject** (`curric:SubSubject`)
- Represents a subject as taught in the curriculum (may differ from the conceptual subject)
- Properties: `rdfs:label`, `curric:isPartOf` (Subject), `curric:includesStrand`
- Enables flexibility where teaching structure differs from knowledge structure

**Scheme** (`curric:Scheme`)
- Defines curriculum content for a subject across one or more year groups
- Properties: `rdfs:label`, `curric:isPartOf` (SubSubject), `curric:hasKeyStage`, `curric:hasContent`
- Example: Science Key Stage 3 scheme

## Properties

### Object Properties

**Hierarchical Relationships**

- **`curric:hasPart`** / **`curric:isPartOf`**
  - Transitive properties for hierarchical containment
  - Inverse of each other
  - Example: `eng:key-stage-3 curric:isPartOf eng:phase-secondary`

- **`curric:hasKeyStage`** / **`curric:isKeyStageOf`**
  - Connects schemes to key stages
  - Domain: `curric:Scheme`, Range: `curric:KeyStage`
  - Example: `eng:scheme-science-key-stage-3 curric:hasKeyStage eng:key-stage-3`

**Content Relationships**

- **`curric:hasStrand`** / **`curric:isStrandOf`**
  - Connects subjects to strands
  - Subproperty of `skos:narrower` / `skos:broader`
  - Example: `eng:subject-science curric:hasStrand eng:strand-structure-function-living-organisms`

- **`curric:includesStrand`** / **`curric:applicableToSubSubject`**
  - Connects sub-subjects to strands
  - Example: `eng:subsubject-science curric:includesStrand eng:strand-material-cycles-and-energy`

- **`curric:hasContent`** / **`curric:isContentOf`**
  - Connects schemes to content descriptors
  - Domain: `curric:Scheme`, Range: `curric:ContentDescriptor`
  - Example: `eng:scheme-science-key-stage-3 curric:hasContent eng:content-descriptor-cells-as-unit-of-living-organism`

**SKOS Properties** (used throughout knowledge structure)

- **`skos:broader`** / **`skos:narrower`**: Hierarchical relationships in taxonomies
- **`skos:related`**: Associative relationships (e.g., content to themes)
- **`skos:inScheme`**: Membership in a concept scheme
- **`skos:topConceptOf`**: Top-level concepts in a scheme

See [SKOS Primer](https://www.w3.org/TR/skos-primer/) for detailed semantics.

### Datatype Properties

**Age Boundaries**

- **`curric:lowerAgeBoundary`**
  - Domain: Phase, KeyStage, or YearGroup
  - Range: `xsd:nonNegativeInteger`
  - Example: `eng:key-stage-3 curric:lowerAgeBoundary 11`

- **`curric:upperAgeBoundary`**
  - Domain: Phase, KeyStage, or YearGroup
  - Range: `xsd:positiveInteger`
  - Example: `eng:key-stage-3 curric:upperAgeBoundary 14`

**Descriptive Properties**

- **`curric:hasAim`**
  - Educational aims for a subject
  - Range: `rdf:langString`
  - Example: Develop scientific knowledge through biology, chemistry, and physics

- **`curric:example`**
  - Text examples illustrating content
  - Domain: `curric:ContentSubDescriptor`
  - Range: `rdf:langString`

- **`curric:exampleURL`**
  - URL examples illustrating content
  - Domain: `curric:ContentSubDescriptor`
  - Range: `xsd:anyURI`

## Design Decisions

### Why SKOS?

[SKOS (Simple Knowledge Organization System)](https://www.w3.org/TR/skos-reference/) provides:
- Standard vocabulary for taxonomies and thesauri
- Broader/narrower hierarchical relationships
- Multilingual label support
- Wide tool support in semantic web ecosystem

Knowledge structure classes (Subject, Strand, etc.) are subclasses of `skos:Concept` to leverage these capabilities.

### Why Separate Subject and SubSubject?

This separation provides flexibility:
- **Subject** represents the conceptual discipline (e.g., "Science" as a field of knowledge)
- **SubSubject** represents how it's taught (e.g., "Science" as taught in England may combine biology, chemistry, physics differently than in Scotland)

This allows the same knowledge taxonomy to be reused across different teaching structures.

### Why Both Custom Properties and SKOS Properties?

- **SKOS properties** (`skos:broader`, `skos:narrower`) are used for pure taxonomic relationships within the knowledge structure
- **Custom properties** (`curric:hasStrand`, `curric:hasContent`) are used where:
  - More specific domain/range constraints are needed
  - The relationship crosses between programme structure and knowledge structure
  - Additional semantics beyond SKOS are required

Both approaches coexist: `curric:hasStrand` is a subproperty of `skos:narrower`, so SKOS-aware tools can still navigate the hierarchy.

### Versioning Strategy

Each ontology file includes:
- **`owl:versionInfo`**: Simple version string (e.g., "0.1.0")
- **`owl:versionIRI`**: URI for this specific version
- **`owl:priorVersion`**: Link to previous version

Versioned files are preserved in `versions/` directories, enabling:
- Stable references to specific versions
- Backward compatibility tracking
- Evolution documentation

See [OWL 2 Versioning](https://www.w3.org/TR/owl2-syntax/#Ontology_IRI_and_Version_IRI) for specification details.

### Separation of Ontology and Constraints

The **ontology** (`curriculum-ontology.ttl`) defines what _can_ be said (classes and properties).

The **constraints** (`curriculum-constraints.ttl`) define what _should_ be said (validation rules using [SHACL](https://www.w3.org/TR/shacl/)).

This separation allows:
- Ontology to remain stable while policies evolve
- Different constraint profiles for different contexts
- Validation rules that may be more restrictive than the ontology allows

For example, the ontology allows multiple key stages per scheme, but current constraints require exactly one.

### Use of Ordered Collections

Programme structure uses `skos:OrderedCollection` for sequences:
- Year groups within a key stage (Year 1, Year 2, ...)
- Key stages within a phase (KS1, KS2, ...)

This preserves the natural ordering important for educational progression.

### Namespace Design

- **Core namespace** (`https://w3id.org/uk/curriculum/core/`): Reusable across UK nations
- **Country namespaces** (`https://w3id.org/uk/curriculum/england/`): Nation-specific data
- **Subject namespaces**: Could be further subdivided if needed (e.g., `/england/science/`)

This supports:
- Reuse of core model across Wales, Scotland, Northern Ireland
- Clear provenance of data
- Potential federation of curriculum data

### Metadata Standards

Comprehensive metadata using [Dublin Core Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/):
- **Provenance**: `dcterms:creator`, `dcterms:source`
- **Temporal**: `dcterms:created`, `dcterms:modified`, `dcterms:issued`
- **Rights**: `dcterms:license`, `dcterms:rights`
- **Documentation**: `dcterms:description`, `rdfs:comment`

This enables discovery, trust, and proper attribution.
