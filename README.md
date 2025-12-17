# DfE Curriculum Ontology

A semantic web ontology for describing curriculum structures, content organization, and educational programmes. Currently provides comprehensive coverage of the National Curriculum for England.

## Quick Start

```turtle
@prefix curric: <https://w3id.org/uk/curriculum/core/> .
@prefix eng: <https://w3id.org/uk/curriculum/england/> .

# Access Science content for Key Stage 3
eng:scheme-science-key-stage-3
  curric:hasContent eng:content-descriptor-cells-as-unit-of-living-organism .
```

**Namespace URIs:**
- DfE Curriculum Ontology: `https://w3id.org/uk/curriculum/core/`
- National Curriculum for England Data: `https://w3id.org/uk/curriculum/england/`

## Namespace Strategy

**⚠️ IMPORTANT: The current w3id.org namespaces are TEMPORARY.**

This ontology currently uses w3id.org URIs for development and initial deployment. However, the ultimate production architecture will use organization-owned namespaces with clear ownership boundaries.

### Ultimate Vision

**Department for Education (DfE)** will own and maintain the core curriculum standard at:
- **curriculum.education.gov.uk** - Core ontology and reference data

This namespace will contain:
- Core classes: Subject, KeyStage, Phase, Programme, Scheme
- Core properties: hasSubject, hasKeyStage, isPartOf
- Reference data: Official subjects, key stages, phases

**DfE's commitment:**
- URI persistence (like legislation.gov.uk)
- Professional infrastructure and governance
- Content negotiation (HTML for humans, RDF for machines)
- Stable versioning and documentation

### Why Not w3id.org Long-Term?

**Clear Ownership**: The DfE wholly owns and maintains the national curriculum standard. Using curriculum.education.gov.uk makes ownership explicit from the URI itself.

**No Governance Complexity**: There's no need for shared namespace coordination. DfE publishes the standard. Other organizations extend it in their own namespaces. This is a standard producer/consumer pattern, not a multi-stakeholder collaboration.

**Infrastructure Control**: DfE controls their own infrastructure, persistence policies, and service levels without dependency on external services.

**Professional Trust**: A .gov.uk domain provides immediate trust and authority for an official government standard.

### The Schema.org Pattern

This architecture follows the established pattern used by Schema.org:
- **Schema.org** maintains the core vocabulary at schema.org
- **Extensions** exist in their own namespaces (health-lifesci.schema.org, bib.schema.org)
- **External adopters** use their own domains and link to the core

The DfE curriculum standard works the same way: DfE owns the core, others extend and implement in their own namespaces.

### Standard Semantic Web Linking

Other organizations will extend the DfE standard in their own namespaces using standard OWL linking patterns:
- Import the DfE ontology
- Extend with organization-specific classes
- Link to DfE reference data

This approach:
- Makes ownership clear from URIs
- Eliminates coordination overhead
- Allows each organization to move at their own pace
- Follows established semantic web best practices

### Current State

During development and initial deployment, w3id.org provides:
- Quick setup without infrastructure requirements
- Content negotiation for testing
- Flexibility to iterate

These temporary URIs will be migrated to curriculum.education.gov.uk once DfE infrastructure is in place.

## Purpose

This ontology provides a standardized, machine-readable representation of the National Curriculum for England. It enables:

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
Organizes the actual curriculum content and concepts by discipline:
```
Discipline (e.g., Science)
  └─ Strand (e.g. Structure and function of living organisms)
      └─ SubStrand (e.g. Cells and organisation)
          └─ ContentDescriptor (e.g. Cells as the fundamental unit of living organisms)
              └─ ContentSubDescriptor (further detail, elaboration, examples)
```

### Cross-Cutting Themes
**Themes** provide connections across subjects (e.g., Climate Change, Digital Literacy) and can be linked to any content descriptor to show where these important topics appear throughout the curriculum.

![The three main hierarchies](docs/images/model.png)

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

See [docs/user-guide/sparql-examples.md](docs/user-guide/sparql-examples.md) for more SPARQL query examples.

## File Structure

```
dfe-curriculum-ontology/
├── ontology/
│   ├── curriculum-ontology.ttl           # Core classes and properties
│   ├── curriculum-constraints.ttl        # SHACL validation shapes
│   └── versions/                         # Versioned releases
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
├── distributions/                        # Distribution packages
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

See [docs/user-guide/validation.md](docs/user-guide/validation.md) for validation details.

### Query with SPARQL

```bash
# Example with Apache Jena
sparql --data=data/england/*.ttl --query=your-query.rq
```

See [docs/user-guide/sparql-examples.md](docs/user-guide/sparql-examples.md) for query patterns.

## Deployment

### Production SPARQL Endpoint

A public SPARQL endpoint is available at:
`https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql`

### Deploy Your Own Instance

```bash
./deployment/deploy.sh
```

See [docs/deployment/deploying.md](docs/deployment/deploying.md) for detailed deployment instructions, monitoring, and troubleshooting.

## Three Ways to Access the Data

### 1. URI Dereferencing (Get Specific Resources)

Fetch individual curriculum resources in different RDF formats using SPARQL DESCRIBE:

```bash
# Get Science subject as JSON-LD
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/ld+json" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

**Supported formats:**
- `Accept: text/turtle` - Turtle (`.ttl`)
- `Accept: application/ld+json` - JSON-LD (`.jsonld`)
- `Accept: application/rdf+xml` - RDF/XML (`.rdf`)

### 2. SPARQL Queries (Custom Queries)

Execute custom SPARQL queries for complex data retrieval:

```bash
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/sparql-results+json" \
    --data "SELECT ?subject ?label WHERE { ?subject a <https://w3id.org/uk/curriculum/core/Subject> ; <http://www.w3.org/2000/01/rdf-schema#label> ?label }" \
    https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

**Endpoint:** `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql`

See [docs/user-guide/sparql-examples.md](docs/user-guide/sparql-examples.md) for query examples.

### 3. Bulk Downloads (Pre-Generated Files)

Download complete datasets from GitHub Releases in three RDF formats:

```bash
# Download subjects index as Turtle
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/index.ttl

# Download Science KS3 as JSON-LD
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/science-ks3.jsonld

# Download full curriculum as RDF/XML
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/curriculum-full.rdf
```

**Available datasets:**
- `index.*` - All subjects
- `science-ks3.*` - Science Key Stage 3 content
- `curriculum-full.*` - Complete curriculum

**All formats:**
- `.ttl` (Turtle) - Compact, human-readable
- `.jsonld` (JSON-LD) - JSON-based RDF for web apps
- `.rdf` (RDF/XML) - XML-based RDF for legacy tools

---

### Which Access Method Should I Use?

| Use Case | Recommended Method |
|----------|-------------------|
| **Web application** fetching specific resources | URI Dereferencing (SPARQL DESCRIBE) with JSON-LD |
| **Complex queries** across the curriculum | SPARQL Queries |
| **Initial data load** for application | Bulk Downloads |
| **Offline analysis** or research | Bulk Downloads (Turtle format) |
| **Legacy RDF tools** | Bulk Downloads (RDF/XML format) |

> **📘 See:** [Content Negotiation Guide](docs/user-guide/content-negotiation.md) for detailed examples

## For Developers

### Building

See [docs/deployment/building.md](docs/deployment/building.md) for build instructions.

### Deployment

See [docs/deployment/deploying.md](docs/deployment/deploying.md) for deployment guide.

### Releases

See [docs/deployment/releasing.md](docs/deployment/releasing.md) for release process.

### Architecture

See [docs/deployment/architecture.md](docs/deployment/architecture.md) for complete architecture documentation.

## Data Access

This ontology provides three complementary ways to access curriculum data:

### 1. **URI Dereferencing** - Fetch specific resources with content negotiation
Get RDF data about individual curriculum resources (subjects, key stages, content descriptors) in Turtle, JSON-LD, or RDF/XML format.

### 2. **SPARQL Endpoint** - Execute custom queries
Run SPARQL queries for complex data retrieval and discovery across the entire curriculum.

### 3. **Bulk Downloads** - Pre-generated RDF files
Download complete datasets from GitHub Releases in three RDF formats for offline use, analysis, or loading into your own triple store.

**📖 See the "Three Ways to Access the Data" section below for detailed examples.**

**Endpoint:** `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql`

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

### Auto-Generated Ontology Documentation

Complete HTML documentation including class hierarchies, properties, and visualizations:
- **GitHub Pages**: Available after first release (see [setup instructions](docs/deployment/github-actions.md#enabling-github-pages-first-time-setup))

### User Guide

- [Data Model](docs/user-guide/data-model.md) - Curriculum structure and concepts
- [SPARQL Examples](docs/user-guide/sparql-examples.md) - Query patterns and examples
- [API Examples](docs/user-guide/api-examples.md) - SPARQL queries and JSON downloads
- [Validation Guide](docs/user-guide/validation.md) - Data validation

### Deployment Guide

- [Architecture](docs/deployment/architecture.md) - System architecture
- [Building](docs/deployment/building.md) - Build process
- [Deploying](docs/deployment/deploying.md) - Cloud deployment
- [Releasing](docs/deployment/releasing.md) - Release process
- [Extending](docs/deployment/extending.md) - Adding content
- [GitHub Actions](docs/deployment/github-actions.md) - CI/CD workflows

## License

This work is made available under the [Open Government Licence v3.0](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

Crown Copyright (c) 2025

## Contributing

For questions, suggestions, or contributions, please contact the Department for Education.

## Related Resources

- [National Curriculum for England](https://www.gov.uk/government/collections/national-curriculum)
- [UK Government Linked Data](https://www.data.gov.uk/)
