# Extension Guide

This guide explains how to extend the UK Curriculum Ontology with new content, subjects, or structural elements.

## Table of Contents

- [Before You Start](#before-you-start)
- [Adding a New Subject](#adding-a-new-subject)
- [Adding Content to an Existing Subject](#adding-content-to-an-existing-subject)
- [Adding a New Key Stage](#adding-a-new-key-stage)
- [Adding Cross-Cutting Themes](#adding-cross-cutting-themes)
- [Naming Conventions](#naming-conventions)
- [Required Properties Checklist](#required-properties-checklist)
- [Testing Your Changes](#testing-your-changes)

## Before You Start

### Understanding the File Structure

New content should be organized following the existing structure:

```
data/
└── {country}/                    # e.g., england, wales, scotland
    ├── programme-structure.ttl   # Phases, key stages, year groups
    ├── themes.ttl                # Cross-cutting themes
    └── subjects/
        └── {subject-name}/       # e.g., science, mathematics
            ├── {subject}-subject.ttl            # Subject definition
            ├── {subject}-knowledge-taxonomy.ttl # Strands and content
            └── {subject}-schemes.ttl            # Key stage mappings
```

### Namespace Conventions

- **Country namespace**: `https://w3id.org/uk/curriculum/{country}/`
- **Core namespace**: `https://w3id.org/uk/curriculum/core/`
- **Prefix**: Use country code (e.g., `eng:`, `wal:`, `sco:`)

### Version Control

1. Make changes to the main files (not versioned ones)
2. Update version info in the ontology declaration
3. When releasing, copy to `versions/` directory with version suffix

## Adding a New Subject

### Step 1: Create Subject Files

Create a new directory under `data/{country}/subjects/{subject-name}/`:

```bash
mkdir -p data/england/subjects/mathematics
```

### Step 2: Define the Subject

Create `{subject}-subject.ttl`:

```turtle
@prefix curric: <https://w3id.org/uk/curriculum/core/> .
@prefix eng: <https://w3id.org/uk/curriculum/england/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Ontology declaration
<https://w3id.org/uk/curriculum/england/mathematics-subject>
  rdf:type owl:Ontology ;
  rdfs:label "National Curriculum England - Mathematics Subject"@en ;
  owl:versionInfo "0.1.0" ;
  owl:versionIRI <https://w3id.org/uk/curriculum/england/mathematics-subject/0.1.0> ;
  dcterms:created "2025-12-04"^^xsd:date ;
  dcterms:modified "2025-12-04"^^xsd:date ;
  owl:imports <https://w3id.org/uk/curriculum/core/> .

# Add to knowledge taxonomy (or reference existing one)
eng:knowledge-taxonomy a skos:ConceptScheme ;
  skos:hasTopConcept eng:subject-mathematics .

# Define the subject
eng:subject-mathematics
  a skos:Concept, curric:Subject ;
  skos:prefLabel "Mathematics"@en ;
  rdfs:label "Mathematics"@en ;
  skos:inScheme eng:knowledge-taxonomy ;
  skos:topConceptOf eng:knowledge-taxonomy ;
  skos:definition "The study of numbers, quantities, shapes, and patterns."@en ;
  dcterms:description "Mathematics curriculum description..."@en ;
  curric:hasAim
    "Become fluent in the fundamentals of mathematics..."@en ,
    "Reason mathematically..."@en ,
    "Solve problems..."@en ;
  curric:hasStrand eng:strand-number , eng:strand-algebra .

# Define sub-subject
eng:subsubject-mathematics
  a curric:SubSubject ;
  rdfs:label "Mathematics"@en ;
  curric:isPartOf eng:subject-mathematics ;
  curric:includesStrand eng:strand-number , eng:strand-algebra .
```

### Step 3: Create Knowledge Taxonomy

Create `{subject}-knowledge-taxonomy.ttl`:

```turtle
# Import subject file
owl:imports <https://w3id.org/uk/curriculum/england/mathematics-subject> .

# Define strands
eng:strand-number
  a skos:Concept, curric:Strand ;
  skos:prefLabel "Number"@en ;
  skos:broader eng:subject-mathematics ;
  skos:narrower eng:substrand-place-value , eng:substrand-addition-subtraction ;
  curric:applicableToSubSubject eng:subsubject-mathematics ;
  skos:inScheme eng:knowledge-taxonomy .

# Define sub-strands
eng:substrand-place-value
  a skos:Concept, curric:SubStrand ;
  skos:prefLabel "Place Value"@en ;
  skos:broader eng:strand-number ;
  skos:narrower eng:content-descriptor-understand-place-value ;
  skos:inScheme eng:knowledge-taxonomy .

# Define content descriptors
eng:content-descriptor-understand-place-value
  a skos:Concept, curric:ContentDescriptor ;
  skos:prefLabel "Understand the place value of digits in numbers up to 1000"@en ;
  skos:broader eng:substrand-place-value ;
  skos:inScheme eng:knowledge-taxonomy .
```

### Step 4: Create Schemes

Create `{subject}-schemes.ttl`:

```turtle
# Import dependencies
owl:imports <https://w3id.org/uk/curriculum/england/programme-structure> ;
owl:imports <https://w3id.org/uk/curriculum/england/mathematics-subject> ;
owl:imports <https://w3id.org/uk/curriculum/england/mathematics-knowledge-taxonomy> .

# Define schemes for each key stage
eng:scheme-mathematics-key-stage-1
  a curric:Scheme ;
  rdfs:label "Mathematics Key Stage 1"@en ;
  curric:isPartOf eng:subsubject-mathematics ;
  curric:hasKeyStage eng:key-stage-1 ;
  curric:hasContent
    eng:content-descriptor-understand-place-value ,
    eng:content-descriptor-count-in-steps .

eng:scheme-mathematics-key-stage-2
  a curric:Scheme ;
  rdfs:label "Mathematics Key Stage 2"@en ;
  curric:isPartOf eng:subsubject-mathematics ;
  curric:hasKeyStage eng:key-stage-2 ;
  curric:hasContent
    eng:content-descriptor-decimal-place-value ,
    eng:content-descriptor-multiply-divide .
```

### Step 5: Validate

```bash
./tools/validate.sh data/england/subjects/mathematics/*.ttl
```

## Adding Content to an Existing Subject

### Adding a New Strand

In `{subject}-knowledge-taxonomy.ttl`:

```turtle
# 1. Define the strand
eng:strand-my-new-strand
  a skos:Concept, curric:Strand ;
  skos:prefLabel "My New Strand"@en ;
  skos:broader eng:subject-science ;           # Link to subject
  skos:narrower eng:substrand-my-substrand ;   # Link to sub-strands
  curric:applicableToSubSubject eng:subsubject-science ;
  skos:inScheme eng:knowledge-taxonomy .

# 2. Update the subject to reference the strand
eng:subject-science
  curric:hasStrand eng:strand-my-new-strand .  # Add this line

# 3. Update the sub-subject to include the strand
eng:subsubject-science
  curric:includesStrand eng:strand-my-new-strand .  # Add this line
```

### Adding a New Content Descriptor

```turtle
# 1. Define the content descriptor
eng:content-descriptor-my-new-content
  a skos:Concept, curric:ContentDescriptor ;
  skos:prefLabel "Description of the content to be learned"@en ;
  skos:broader eng:substrand-cells-organisation ;  # Link to parent sub-strand
  skos:inScheme eng:knowledge-taxonomy .

# 2. Update the parent sub-strand
eng:substrand-cells-organisation
  skos:narrower eng:content-descriptor-my-new-content .  # Add this line

# 3. Add to appropriate scheme(s)
eng:scheme-science-key-stage-3
  curric:hasContent eng:content-descriptor-my-new-content .  # Add this line
```

### Adding Content Sub-Descriptors

```turtle
# Define content sub-descriptor with examples
eng:content-subdescriptor-my-detail
  a skos:Concept, curric:ContentSubDescriptor ;
  skos:prefLabel "Detailed elaboration"@en ;
  skos:broader eng:content-descriptor-my-new-content ;
  skos:inScheme eng:knowledge-taxonomy ;
  curric:example "Example text illustrating this concept"@en ;
  curric:exampleURL <https://example.org/resource> .

# Update parent content descriptor
eng:content-descriptor-my-new-content
  skos:narrower eng:content-subdescriptor-my-detail .
```

## Adding a New Key Stage

If you need to add a new key stage (e.g., for a different country):

In `programme-structure.ttl`:

```turtle
# 1. Define the key stage
eng:key-stage-5
  a curric:KeyStage ;
  rdfs:label "Key Stage 5"@en ;
  rdfs:comment "Key Stage 5 covering years 12-13 (A-levels)."@en ;
  curric:lowerAgeBoundary 16 ;
  curric:upperAgeBoundary 18 ;
  curric:isPartOf eng:phase-secondary .  # Or create a new phase

# 2. Define year groups within it
eng:year-group-12
  a curric:YearGroup ;
  rdfs:label "Year Group 12"@en ;
  curric:lowerAgeBoundary 16 ;
  curric:upperAgeBoundary 17 ;
  curric:isPartOf eng:key-stage-5 .

eng:year-group-13
  a curric:YearGroup ;
  rdfs:label "Year Group 13"@en ;
  curric:lowerAgeBoundary 17 ;
  curric:upperAgeBoundary 18 ;
  curric:isPartOf eng:key-stage-5 .

# 3. Create ordered collections
eng:key-stage-5-year-groups
  a skos:OrderedCollection ;
  rdfs:label "Key Stage 5 Year Groups"@en ;
  skos:memberList (eng:year-group-12 eng:year-group-13) .
```

Then create schemes for the new key stage:

```turtle
eng:scheme-science-key-stage-5
  a curric:Scheme ;
  rdfs:label "Science Key Stage 5"@en ;
  curric:isPartOf eng:subsubject-science ;
  curric:hasKeyStage eng:key-stage-5 ;
  curric:hasContent eng:content-descriptor-advanced-physics .
```

## Adding Cross-Cutting Themes

In `themes.ttl`:

```turtle
# 1. Add to themes taxonomy
eng:themes-taxonomy
  skos:hasTopConcept eng:theme-my-new-theme .  # Add this line

# 2. Define the theme
eng:theme-my-new-theme
  a skos:Concept, curric:Theme ;
  skos:prefLabel "My New Theme"@en ;
  skos:definition "Description of this cross-cutting theme."@en ;
  skos:inScheme eng:themes-taxonomy ;
  skos:topConceptOf eng:themes-taxonomy .

# 3. Link theme to content (in knowledge taxonomy files)
eng:content-descriptor-relevant-content
  skos:related eng:theme-my-new-theme .
```

## Naming Conventions

### URI Patterns

Follow these patterns for consistent, readable URIs:

**Programme Structure:**
- Phases: `{prefix}:phase-{name}` (e.g., `eng:phase-primary`)
- Key Stages: `{prefix}:key-stage-{number}` (e.g., `eng:key-stage-3`)
- Year Groups: `{prefix}:year-group-{number}` (e.g., `eng:year-group-7`)

**Knowledge Structure:**
- Subjects: `{prefix}:subject-{name}` (e.g., `eng:subject-science`)
- Sub-subjects: `{prefix}:subsubject-{name}` (e.g., `eng:subsubject-science`)
- Strands: `{prefix}:strand-{descriptive-name}` (e.g., `eng:strand-number`)
- Sub-strands: `{prefix}:substrand-{descriptive-name}` (e.g., `eng:substrand-place-value`)
- Content Descriptors: `{prefix}:content-descriptor-{descriptive-name}` (e.g., `eng:content-descriptor-cells-as-unit`)
- Content Sub-Descriptors: `{prefix}:content-subdescriptor-{descriptive-name}`

**Other:**
- Schemes: `{prefix}:scheme-{subject}-key-stage-{n}` (e.g., `eng:scheme-science-key-stage-3`)
- Themes: `{prefix}:theme-{name}` (e.g., `eng:theme-digital-literacy`)
- Taxonomies: `{prefix}:{name}-taxonomy` (e.g., `eng:knowledge-taxonomy`)

### Label Conventions

- Use title case for labels: "Key Stage 3", not "key stage 3"
- Always include language tags: `"Science"@en`
- Be concise but descriptive
- Use full words, not abbreviations (in labels)

## Required Properties Checklist

### For All Classes

- [ ] `rdf:type` (class membership)
- [ ] `rdfs:label` or `skos:prefLabel` (as appropriate)
- [ ] At least one descriptive property (comment, definition, or description)

### Phase
- [ ] `rdfs:label`
- [ ] `curric:lowerAgeBoundary`
- [ ] `curric:upperAgeBoundary`

### KeyStage
- [ ] `rdfs:label`
- [ ] `curric:isPartOf` (exactly one Phase)
- [ ] `curric:lowerAgeBoundary`
- [ ] `curric:upperAgeBoundary`
- [ ] Used in at least one Scheme

### YearGroup
- [ ] `rdfs:label`
- [ ] `curric:isPartOf` (exactly one KeyStage)
- [ ] `curric:lowerAgeBoundary`
- [ ] `curric:upperAgeBoundary`

### Subject
- [ ] `rdfs:label`
- [ ] `skos:prefLabel`
- [ ] `skos:inScheme` (at least one ConceptScheme)
- [ ] `skos:definition` (recommended)
- [ ] `curric:hasAim` (recommended, multiple values)
- [ ] Used in at least one SubSubject

### SubSubject
- [ ] `rdfs:label`
- [ ] `curric:isPartOf` (exactly one Subject)
- [ ] `curric:includesStrand` (recommended)
- [ ] Used in at least one Scheme

### Strand
- [ ] `skos:prefLabel`
- [ ] `skos:inScheme` (exactly one ConceptScheme)
- [ ] `skos:broader` (exactly one Subject)
- [ ] `curric:applicableToSubSubject` (at least one)
- [ ] `skos:narrower` (at least one SubStrand)
- [ ] Both `curric:hasStrand` from Subject AND `curric:includesStrand` from SubSubject

### SubStrand
- [ ] `skos:prefLabel`
- [ ] `skos:inScheme` (exactly one ConceptScheme)
- [ ] `skos:broader` (exactly one Strand)
- [ ] `skos:narrower` (at least one ContentDescriptor)

### ContentDescriptor
- [ ] `skos:prefLabel`
- [ ] `skos:inScheme` (exactly one ConceptScheme)
- [ ] `skos:broader` (exactly one SubStrand)
- [ ] Used in at least one Scheme via `curric:hasContent`

### ContentSubDescriptor
- [ ] `skos:prefLabel`
- [ ] `skos:inScheme` (exactly one ConceptScheme)
- [ ] `skos:broader` (exactly one ContentDescriptor)
- [ ] `curric:example` or `curric:exampleURL` (recommended)

### Scheme
- [ ] `rdfs:label`
- [ ] `curric:isPartOf` (at least one SubSubject)
- [ ] `curric:hasKeyStage` (exactly one KeyStage)
- [ ] `curric:hasContent` (recommended, at least one ContentDescriptor)

### Theme
- [ ] `skos:prefLabel`
- [ ] `skos:definition`
- [ ] `skos:inScheme` (exactly one ConceptScheme)
- [ ] Related to at least one content item via `skos:related`

### Ontology Metadata

Every ontology file should include:

- [ ] `rdfs:label` - Human-readable name
- [ ] `owl:versionInfo` - Version number (e.g., "0.1.0")
- [ ] `owl:versionIRI` - URI for this version
- [ ] `dcterms:created` - Creation date
- [ ] `dcterms:modified` - Last modification date
- [ ] `dcterms:license` - License URI
- [ ] `owl:imports` - References to imported ontologies

## Testing Your Changes

### 1. Syntax Validation

Check for Turtle syntax errors:

```bash
# Using rapper (from Raptor RDF)
rapper -i turtle -c data/england/subjects/mathematics/mathematics-subject.ttl

# Using Apache Jena
riot --validate data/england/subjects/mathematics/mathematics-subject.ttl
```

### 2. SHACL Validation

Validate against constraints:

```bash
./tools/validate.sh data/england/subjects/mathematics/*.ttl
```

### 3. Manual Checks

- [ ] All URIs are resolvable (or will be once published)
- [ ] No duplicate URIs
- [ ] All prefixes are declared
- [ ] All referenced entities exist
- [ ] Inverse relationships are consistent (both directions present)
- [ ] Age boundaries are logical (lower < upper)
- [ ] Hierarchies are complete (no orphaned nodes)

### 4. Query Testing

Write SPARQL queries to verify:

```sparql
# Check that new content appears in the hierarchy
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>

SELECT * WHERE {
  eng:subject-mathematics curric:hasStrand ?strand .
  ?strand skos:narrower+ ?content .
}
```

### 5. Integration Testing

Load all files together and test:

```bash
# Load into a triple store and query
./tools/load-triple-store.sh
```

## Best Practices

1. **Start small**: Add one strand at a time, validate, then continue
2. **Reuse existing patterns**: Follow the structure of existing subjects
3. **Document as you go**: Add comments and descriptions
4. **Test incrementally**: Validate after each significant addition
5. **Use semantic versioning**: Increment version numbers appropriately
6. **Preserve history**: Keep old versions in `versions/` directories
7. **Be consistent**: Follow naming conventions strictly
8. **Think hierarchically**: Ensure parent-child relationships are complete
9. **Consider reusability**: Design for potential use by other UK nations
10. **Link to sources**: Use `dcterms:source` to reference official documents

## Common Pitfalls

1. **Forgetting inverse properties**: If you add `curric:hasStrand`, also add `curric:isStrandOf`
2. **Missing language tags**: Always use `"text"@en`, not just `"text"`
3. **Wrong datatypes**: Use `xsd:nonNegativeInteger` for ages, `rdf:langString` for labels
4. **Circular references**: Don't make A broader than B and B broader than A
5. **Orphaned entities**: Ensure all entities are connected to the hierarchy
6. **Inconsistent namespaces**: Always use the full URI or defined prefix
7. **Missing ontology imports**: Each file should import its dependencies
8. **Cardinality violations**: Check SHACL constraints for exact requirements (e.g., exactly one `curric:isPartOf`)

## Getting Help

- Review existing files for patterns
- Check [../user-guide/data-model.md](../user-guide/data-model.md) for class and property definitions
- See [../user-guide/sparql-examples.md](../user-guide/sparql-examples.md) for query patterns
- Consult [../user-guide/validation.md](../user-guide/validation.md) for constraint details
- Refer to W3C specifications: [RDF](https://www.w3.org/TR/rdf11-primer/), [OWL](https://www.w3.org/TR/owl2-overview/), [SKOS](https://www.w3.org/TR/skos-reference/), [SHACL](https://www.w3.org/TR/shacl/)
