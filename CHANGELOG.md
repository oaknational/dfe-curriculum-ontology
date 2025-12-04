# Changelog

All notable changes to the UK Curriculum Ontology will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning Policy

Version numbers follow Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to class or property definitions
- **MINOR**: New classes, properties, or data (backward compatible)
- **PATCH**: Bug fixes, corrections, documentation updates (backward compatible)

Each version is preserved in the `versions/` directories with dated version IRIs.

---

## [0.1.0] - 2025-12-03

**Release:** [curriculum-ontology/0.1.0](https://w3id.org/uk/curriculum/core/curriculum-ontology/0.1.0)

### Added
- Initial public release of UK Curriculum Ontology
- Core ontology defining curriculum structure classes and properties
- SHACL constraints for data validation
- National Curriculum England programme structure (Phases, Key Stages, Year Groups)
- Science subject implementation with knowledge taxonomy
- Cross-cutting themes (Financial Education, Digital Literacy, Climate Change, Media Literacy)
- Comprehensive documentation suite

### Core Ontology Classes
- `Phase`, `KeyStage`, `YearGroup` - Programme structure
- `Subject`, `Strand`, `SubStrand`, `ContentDescriptor`, `ContentSubDescriptor` - Knowledge structure
- `SubSubject` - Teaching structure mapping
- `Scheme` - Content-to-key-stage mapping
- `Theme` - Cross-cutting themes

### Core Properties
- `hasPart` / `isPartOf` - Hierarchical relationships
- `hasKeyStage` / `isKeyStageOf` - Scheme-to-key-stage links
- `hasStrand` / `isStrandOf` - Subject-to-strand links
- `includesStrand` / `applicableToSubSubject` - SubSubject-to-strand links
- `hasContent` / `isContentOf` - Scheme-to-content links
- `lowerAgeBoundary`, `upperAgeBoundary` - Age ranges
- `hasAim`, `example`, `exampleURL` - Descriptive properties

### Data Files
- England programme structure (Primary/Secondary phases, KS1-4, Years 1-11)
- Science subject with strands and sample content descriptors
- Science schemes for Key Stage 3
- Four cross-cutting themes

### Documentation
- README with quick start and usage guide
- Conceptual model documentation
- SPARQL query examples
- SHACL validation guide
- Extension guide for contributors

### Tools
- Validation script template
- Triple store loading script template
- Documentation generation script template

## [0.0.9] - 2025-12-03

**Release:** [curriculum-ontology/0.0.9](https://w3id.org/uk/curriculum/core/curriculum-ontology/0.0.9)

### Added
- Development version with initial structure
- Core class definitions
- Basic SHACL constraints

### Changed
- Namespace URIs finalized to w3id.org structure
- Refined property domains and ranges
