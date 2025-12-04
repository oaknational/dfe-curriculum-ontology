# UK Curriculum Ontology

A semantic web ontology for describing curriculum structures, content organization, and educational programmes in the UK. Currently provides comprehensive coverage of the National Curriculum for England.

## Quick Start

```turtle
@prefix curric: <https://w3id.org/uk/curriculum/core/> .
@prefix eng: <https://w3id.org/uk/curriculum/england/> .

# Access Science content for Key Stage 3
eng:scheme-science-key-stage-3
  curric:hasContent eng:content-descriptor-cells-as-unit-of-living-organism .
```

**Namespace URIs:**
- Core ontology: `https://w3id.org/uk/curriculum/core/`
- England data: `https://w3id.org/uk/curriculum/england/`

## Persistent Identifiers via w3id.org

This ontology uses [w3id.org](https://w3id.org/) to provide **permanent, resolvable URIs** for all curriculum resources.

**Persistence**: URIs remain stable even if the repository moves or hosting changes. For example, `https://w3id.org/uk/curriculum/core/Phase` will always resolve, regardless of where the actual files are stored.

**Content Negotiation**: w3id.org supports automatic format negotiation. When you request a URI, it can serve different formats based on your needs:
- Web browsers receive human-readable documentation
- RDF tools receive machine-readable Turtle/RDF
- This is essential for semantic web best practices

**Professional Trust**: w3id.org is a community-managed service specifically designed for linked data identifiers. Using it signals this is a production-ready, professionally maintained ontology.

**Separation of Concerns**: The persistent identifier (`w3id.org`) is separate from the storage location (GitHub). This means:
- URIs never need to change
- Hosting providers can change without breaking links
- Other ontologies can safely reference these URIs

### How It Works

w3id.org uses HTTP redirects to point persistent URIs to the actual file locations:

```
User requests: https://w3id.org/uk/curriculum/core/curriculum-ontology.ttl
       |
       v
w3id.org redirects (HTTP 303) to:
       |
       v
GitHub: https://raw.githubusercontent.com/oaknational/uk-curriculum-ontology/main/ontology/curriculum-ontology.ttl
```

This redirection is configured via a `.htaccess` file in the [perma-id/w3id.org](https://github.com/perma-id/w3id.org) repository.

## Purpose

This ontology provides a standardized, machine-readable representation of the UK National Curriculum. It enables:

- **Interoperability**: Share curriculum data across educational platforms and systems
- **Semantic queries**: Discover content relationships, dependencies, and cross-cutting themes
- **Validation**: Ensure curriculum data quality through SHACL constraints
- **Linked data**: Connect curriculum content to other educational resources and standards

Designed to be reusable across England, Wales, Scotland, and Northern Ireland, though currently focused on the National Curriculum for England.

## Core Concepts

The ontology organizes curriculum data into three main hierarchies:

### 1. Temporal Hierarchy
Defines the age-based progression through the education system:
```
Phase (Primary, Secondary)
  └─ KeyStage (KS1, KS2, KS3, KS4)
      └─ YearGroup (Year 1-11)
```

### 2. Programme Hierarchy
Defines how subjects are organized and delivered:
```
Subject (e.g. Science)
  └─ SubSubject (e.g. Biology)
      └─ Scheme (e.g. Biology Key Stage 3)
```
A **Scheme** connects temporal and knowledge hierarchies by specifying which content descriptors are taught at which key stage.

### 3. Knowledge Taxonomy
Organizes the actual curriculum content and concepts:
```
Subject (e.g., Science)
  └─ Strand (e.g. Structure and function of living organisms)
      └─ SubStrand (e.g. Cells and organisation)
          └─ ContentDescriptor (e.g. Cells as the fundamental unit of living organisms)
              └─ ContentSubDescriptor (further detail, elaboration, examples)
```

### Cross-Cutting Themes
**Themes** provide connections across subjects (e.g., Climate Change, Digital Literacy) and can be linked to any content descriptor to show where these important topics appear throughout the curriculum.

![The three main hierarchies](https://raw.githubusercontent.com/oaknational/uk-curriculum-ontology/main/docs/images/model.png?raw=1)

## Quick Example

Find all science content for Year 7 students:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>

SELECT ?content ?label WHERE {
  ?scheme curric:hasKeyStage eng:key-stage-3 ;
          curric:hasContent ?content .
  ?content skos:prefLabel ?label .
}
```

See [docs/examples.md](docs/examples.md) for more SPARQL query examples.

## File Structure

```
uk-curriculum-ontology/
├── ontology/
│   ├── curriculum-ontology.ttl           # Core classes and properties
│   └── versions/                         # Versioned releases
├── constraints/
│   ├── curriculum-constraints.ttl        # SHACL validation shapes
│   └── versions/
├── data/
│   └── england/
│       ├── programme-structure.ttl       # Phases, Key Stages, Year Groups
│       ├── themes.ttl                    # Cross-cutting Themes
│       └── subjects/
│           └── science/
│               ├── science-subject.ttl                 # Subjects, Sub-Subjects
│               ├── science-knowledge-taxonomy.ttl      # Strands, Sub-Strands, ContentDescriptors
│               └── science-schemes.ttl                 # Schemes 
│
├── docs/                                 # Documentation
├── tools/                                # Utility scripts
└── validation/                           # Test data and examples
```

## How to Use

### Direct URI Access

Once published, URIs will resolve via content negotiation:
- `https://w3id.org/uk/curriculum/core/Phase` - Class definition
- `https://w3id.org/uk/curriculum/england/key-stage-3` - KS3 data

### Load into a Triple Store

Load TTL files into any RDF triple store ([Apache Jena](https://jena.apache.org/), [GraphDB](https://graphdb.ontotext.com/), [Blazegraph](https://blazegraph.com/)):

```bash
# Example with Jena TDB2
tdb2.tdbloader --loc=/path/to/database ontology/*.ttl data/**/*.ttl
```

### Validate Data with SHACL

```bash
./tools/validate.sh data/england/subjects/science/*.ttl
```

See [docs/validation.md](docs/validation.md) for validation details.

### Query with SPARQL

```bash
# Example with Apache Jena
sparql --data=data/england/*.ttl --query=your-query.rq
```

See [docs/examples.md](docs/examples.md) for query patterns.

## Versioning

This ontology follows [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0): Breaking changes to class/property definitions
- **Minor** (0.1.0): New classes, properties, or data (backward compatible)
- **Patch** (0.0.1): Bug fixes, corrections (backward compatible)

Current version: **0.1.0**

Each version is preserved in `versions/` directories with dated IRIs. See [CHANGELOG.md](CHANGELOG.md) for version history.

## Standards Used

- **RDF 1.1**: [W3C Recommendation](https://www.w3.org/TR/rdf11-primer/)
- **OWL 2**: [W3C Recommendation](https://www.w3.org/TR/owl2-overview/)
- **SKOS**: [W3C Recommendation](https://www.w3.org/TR/skos-reference/) for taxonomies
- **SHACL**: [W3C Recommendation](https://www.w3.org/TR/shacl/) for validation
- **Dublin Core**: Metadata terms ([DCMI](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/))

## Documentation

- [Conceptual Model](docs/model.md) - Detailed class and property descriptions
- [SPARQL Examples](docs/examples.md) - Practical query patterns
- [Validation Guide](docs/validation.md) - SHACL constraints and validation
- [Extension Guide](docs/extending.md) - How to add new content

## License

This work is made available under the [Open Government Licence v3.0](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

Crown Copyright (c) 2025

## Contributing

For questions, suggestions, or contributions, please contact the Department for Education.

## Related Resources

- [National Curriculum for England](https://www.gov.uk/government/collections/national-curriculum)
- [UK Government Linked Data](https://www.data.gov.uk/)
