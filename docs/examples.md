# SPARQL Query Examples

This document provides practical SPARQL query patterns for working with the UK Curriculum Ontology.

For more information about SPARQL, see the [W3C SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/) specification and the [W3C SPARQL Tutorial](https://www.w3.org/TR/sparql11-query/).

## Table of Contents

- [Basic Queries](#basic-queries)
- [Programme Structure Queries](#programme-structure-queries)
- [Knowledge Structure Queries](#knowledge-structure-queries)
- [Content Discovery](#content-discovery)
- [Cross-Cutting Themes](#cross-cutting-themes)
- [Hierarchical Traversal](#hierarchical-traversal)
- [Validation Queries](#validation-queries)

## Basic Queries

### List All Subjects

Find all subjects in the curriculum:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?subject ?label ?definition WHERE {
  ?subject a curric:Subject ;
           skos:prefLabel ?label .
  OPTIONAL { ?subject skos:definition ?definition }
}
```

**Sample Output:**
```
subject                              | label      | definition
-------------------------------------|------------|------------------
eng:subject-science                  | "Science"  | "The systematic study..."
```

### List All Key Stages

Find all key stages with their age boundaries:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?keystage ?label ?lower ?upper WHERE {
  ?keystage a curric:KeyStage ;
            rdfs:label ?label ;
            curric:lowerAgeBoundary ?lower ;
            curric:upperAgeBoundary ?upper .
}
ORDER BY ?lower
```

**Sample Output:**
```
keystage          | label            | lower | upper
------------------|------------------|-------|------
eng:key-stage-1   | "Key Stage 1"    | 5     | 7
eng:key-stage-2   | "Key Stage 2"    | 7     | 11
eng:key-stage-3   | "Key Stage 3"    | 11    | 14
eng:key-stage-4   | "Key Stage 4"    | 14    | 16
```

## Programme Structure Queries

### Find Year Groups for a Key Stage

Get all year groups belonging to Key Stage 3:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?year ?label ?lower ?upper WHERE {
  ?year a curric:YearGroup ;
        rdfs:label ?label ;
        curric:isPartOf eng:key-stage-3 ;
        curric:lowerAgeBoundary ?lower ;
        curric:upperAgeBoundary ?upper .
}
ORDER BY ?lower
```

**Sample Output:**
```
year              | label          | lower | upper
------------------|----------------|-------|------
eng:year-group-7  | "Year Group 7" | 11    | 12
eng:year-group-8  | "Year Group 8" | 12    | 13
eng:year-group-9  | "Year Group 9" | 13    | 14
```

### Find the Phase for a Year Group

Traverse up the hierarchy to find which phase a year group belongs to:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?phase ?phaseLabel WHERE {
  eng:year-group-7 curric:isPartOf ?keystage .
  ?keystage curric:isPartOf ?phase .
  ?phase rdfs:label ?phaseLabel .
}
```

**Sample Output:**
```
phase               | phaseLabel
--------------------|------------
eng:phase-secondary | "Secondary"
```

## Knowledge Structure Queries

### Get All Strands for a Subject

Find all organizational strands within Science:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?strand ?label WHERE {
  eng:subject-science curric:hasStrand ?strand .
  ?strand skos:prefLabel ?label .
}
```

**Sample Output:**
```
strand                                       | label
---------------------------------------------|-----------------------------------
eng:strand-structure-function-living-organisms | "Structure and function of living organisms"
eng:strand-material-cycles-and-energy        | "Material cycles and energy"
```

### Navigate the Knowledge Hierarchy

Get strands, sub-strands, and content descriptors for Science:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?strand ?strandLabel ?substrand ?substrandLabel ?content ?contentLabel WHERE {
  eng:subject-science curric:hasStrand ?strand .
  ?strand skos:prefLabel ?strandLabel ;
          skos:narrower ?substrand .
  ?substrand skos:prefLabel ?substrandLabel ;
             skos:narrower ?content .
  ?content skos:prefLabel ?contentLabel .
}
```

### Get Subject Aims

Retrieve the educational aims for a subject:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>

SELECT ?aim WHERE {
  eng:subject-science curric:hasAim ?aim .
}
```

**Sample Output:**
```
aim
------------------------------------------------------------------------
"Develop scientific knowledge and conceptual understanding through..."
"Develop understanding of the nature, processes and methods of science..."
"Are equipped with the scientific knowledge required to understand..."
```

## Content Discovery

### Find All Content for a Key Stage

Get all content descriptors taught in Key Stage 3:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label WHERE {
  ?scheme curric:hasKeyStage eng:key-stage-3 ;
          curric:hasContent ?content .
  ?content skos:prefLabel ?label .
}
```

### Find Which Key Stages Cover Specific Content

Determine where "cells" content is taught:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?keystage ?ksLabel ?content ?contentLabel WHERE {
  ?scheme curric:hasKeyStage ?keystage ;
          curric:hasContent ?content .
  ?keystage rdfs:label ?ksLabel .
  ?content skos:prefLabel ?contentLabel .
  FILTER(REGEX(?contentLabel, "cell", "i"))
}
```

### Find Content by Subject and Key Stage

Get all Science content for Key Stage 3:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label ?substrand ?substrandLabel WHERE {
  ?scheme curric:isPartOf eng:subsubject-science ;
          curric:hasKeyStage eng:key-stage-3 ;
          curric:hasContent ?content .
  ?content skos:prefLabel ?label ;
           skos:broader ?substrand .
  ?substrand skos:prefLabel ?substrandLabel .
}
ORDER BY ?substrandLabel
```

## Cross-Cutting Themes

### List All Themes

Find all cross-cutting themes in the curriculum:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?theme ?label ?definition WHERE {
  ?theme a curric:Theme ;
         skos:prefLabel ?label ;
         skos:definition ?definition .
}
```

**Sample Output:**
```
theme                                    | label                        | definition
-----------------------------------------|------------------------------|------------------
eng:theme-climate-change-and-sustainability | "Climate and Sustainability" | "Understanding climate change..."
eng:theme-digital-literacy               | "Digital Literacy"           | "Using technology safely..."
eng:theme-financial-education            | "Financial Education"        | "Understanding money..."
eng:theme-media-literacy                 | "Media Literacy"             | "Ability to access, analyze..."
```

### Find Content Related to a Theme

Discover all content related to Climate Change:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?contentLabel ?theme ?themeLabel WHERE {
  ?content skos:related ?theme .
  ?theme a curric:Theme ;
         skos:prefLabel ?themeLabel .
  ?content skos:prefLabel ?contentLabel .
  FILTER(?theme = eng:theme-climate-change-and-sustainability)
}
```

### Find Themes Across Multiple Subjects

Identify which subjects address a specific theme (when data is expanded):

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?subject ?subjectLabel WHERE {
  ?content skos:related eng:theme-digital-literacy ;
           skos:broader+ ?strand .
  ?subject curric:hasStrand ?strand ;
           skos:prefLabel ?subjectLabel .
}
```

## Hierarchical Traversal

### Get Full Hierarchy Path for Content

Trace the complete path from content descriptor to subject:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?contentLabel ?substrand ?substrandLabel ?strand ?strandLabel ?subject ?subjectLabel WHERE {
  BIND(eng:content-descriptor-cells-as-unit-of-living-organism AS ?content)

  ?content skos:prefLabel ?contentLabel ;
           skos:broader ?substrand .
  ?substrand skos:prefLabel ?substrandLabel ;
             skos:broader ?strand .
  ?strand skos:prefLabel ?strandLabel ;
          skos:broader ?subject .
  ?subject skos:prefLabel ?subjectLabel .
}
```

### Find All Descendants of a Strand

Get all content under a specific strand (using property paths):

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?descendant ?label ?type WHERE {
  ?descendant skos:broader+ eng:strand-structure-function-living-organisms ;
              skos:prefLabel ?label ;
              a ?type .
  FILTER(?type IN (curric:SubStrand, curric:ContentDescriptor, curric:ContentSubDescriptor))
}
ORDER BY ?type ?label
```

**Note:** The `+` operator means "one or more" - see [SPARQL Property Paths](https://www.w3.org/TR/sparql11-query/#propertypaths) for details.

## Validation Queries

### Find Schemes Without Content

Identify schemes that have no content descriptors assigned:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?scheme ?label WHERE {
  ?scheme a curric:Scheme ;
          rdfs:label ?label .
  FILTER NOT EXISTS {
    ?scheme curric:hasContent ?content .
  }
}
```

### Check Age Boundary Consistency

Find year groups where age boundaries don't match their parent key stage:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?year ?yearLabel ?yearLower ?yearUpper ?ksLower ?ksUpper WHERE {
  ?year a curric:YearGroup ;
        rdfs:label ?yearLabel ;
        curric:isPartOf ?keystage ;
        curric:lowerAgeBoundary ?yearLower ;
        curric:upperAgeBoundary ?yearUpper .

  ?keystage curric:lowerAgeBoundary ?ksLower ;
            curric:upperAgeBoundary ?ksUpper .

  FILTER(?yearLower < ?ksLower || ?yearUpper > ?ksUpper)
}
```

### Find Orphaned Strands

Identify strands not connected to any subject:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?strand ?label WHERE {
  ?strand a curric:Strand ;
          skos:prefLabel ?label .
  FILTER NOT EXISTS {
    ?subject curric:hasStrand ?strand .
  }
}
```

### Count Content by Key Stage

Get statistics on content coverage:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?keystage ?ksLabel (COUNT(?content) AS ?contentCount) WHERE {
  ?scheme curric:hasKeyStage ?keystage ;
          curric:hasContent ?content .
  ?keystage rdfs:label ?ksLabel .
}
GROUP BY ?keystage ?ksLabel
ORDER BY ?keystage
```

## Advanced Examples

### Find Content Gaps Between Key Stages

Identify content in KS3 but not in KS2 (progression analysis):

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label WHERE {
  ?scheme3 curric:hasKeyStage eng:key-stage-3 ;
           curric:hasContent ?content .
  ?content skos:prefLabel ?label .

  FILTER NOT EXISTS {
    ?scheme2 curric:hasKeyStage eng:key-stage-2 ;
             curric:hasContent ?content .
  }
}
```

### Find Common Content Across Subjects

Identify content descriptors that appear in multiple subjects (when subjects share content):

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label (COUNT(DISTINCT ?subject) AS ?subjectCount) WHERE {
  ?scheme curric:hasContent ?content ;
          curric:isPartOf ?subsubject .
  ?subsubject curric:isPartOf ?subject .
  ?content skos:prefLabel ?label .
}
GROUP BY ?content ?label
HAVING (COUNT(DISTINCT ?subject) > 1)
```

### Federated Query Template

Example of querying this ontology alongside other linked data sources:

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

# Find curriculum content and link to external educational resources
SELECT ?content ?label ?externalResource WHERE {
  # Local curriculum data
  eng:subject-science curric:hasStrand ?strand .
  ?strand skos:narrower+ ?content .
  ?content skos:prefLabel ?label .

  # Link to external resource (example - actual endpoint would vary)
  SERVICE <http://example.org/sparql> {
    ?externalResource dc:subject ?label .
  }
}
```

See [SPARQL 1.1 Federated Query](https://www.w3.org/TR/sparql11-federated-query/) for more details on the SERVICE keyword.

## Tips and Best Practices

1. **Use DISTINCT** when traversing hierarchies to avoid duplicates
2. **Use property paths** (`+`, `*`) for flexible hierarchical queries
3. **Add FILTER clauses** for text matching (case-insensitive with "i" flag)
4. **Use OPTIONAL** for properties that may not always be present
5. **Use COUNT and GROUP BY** for statistics and aggregation
6. **Test queries** against small datasets first, then scale up
7. **Add LIMIT** during development to speed up query testing

## Running Queries

### Command Line (Apache Jena)

```bash
# Query local files
sparql --data=ontology/curriculum-ontology.ttl \
       --data=data/england/programme-structure.ttl \
       --data=data/england/subjects/science/*.ttl \
       --query=your-query.rq

# Query a triple store
sparql --service=http://localhost:3030/curriculum \
       --query=your-query.rq
```

### With a Triple Store

Load the data into a triple store (Jena Fuseki, GraphDB, etc.) and use the SPARQL endpoint:

```bash
curl -X POST http://localhost:3030/curriculum/query \
     -H "Content-Type: application/sparql-query" \
     --data-binary @your-query.rq
```

See the [SPARQL Protocol](https://www.w3.org/TR/sparql11-protocol/) specification for details.

## Resources

- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/) - Full specification
- [SPARQL Tutorial](https://www.w3.org/TR/sparql11-query/) - W3C learning resource
- [Apache Jena](https://jena.apache.org/) - Java framework for semantic web applications
- [SPARQL Playground](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/Wikidata_Query_Help) - Interactive learning
