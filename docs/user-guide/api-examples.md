# Data Access Examples

This guide shows the three ways to access curriculum data:
1. **URI Dereferencing** - Get RDF about specific resources
2. **SPARQL Queries** - Execute custom queries
3. **Bulk Downloads** - Download pre-generated RDF files

> **📘 See also:** [Content Negotiation Guide](content-negotiation.md) for detailed information about format selection.

---

## 1. URI Dereferencing (SPARQL DESCRIBE)

Get all data about a specific curriculum resource in different RDF formats.

**Endpoint:** `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql`

### Get Subject in Different Formats

**Turtle:**
```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: text/turtle" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

**JSON-LD:**
```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/ld+json" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

**RDF/XML:**
```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/rdf+xml" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

---

## 2. SPARQL Queries

Execute custom queries to find specific curriculum data.

---

## 3. Bulk Downloads

Download pre-generated RDF files from GitHub Releases. All datasets available in three formats:
- `.ttl` (Turtle) - Compact, human-readable
- `.jsonld` (JSON-LD) - JSON-based RDF for web apps
- `.rdf` (RDF/XML) - Legacy XML format

### Download Subjects Index

```bash
# As Turtle
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/index.ttl

# As JSON-LD
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/index.jsonld

# As RDF/XML
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/index.rdf
```

### Download Science KS3 Content

```bash
# As Turtle
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/science-ks3.ttl

# As JSON-LD
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/science-ks3.jsonld
```

### Download Full Curriculum

```bash
# As Turtle (most compact)
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/curriculum-full.ttl

# As JSON-LD
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/curriculum-full.jsonld
```

### Load into Application

**Python with rdflib:**
```python
from rdflib import Graph

# Download and parse Turtle file
g = Graph()
g.parse("https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/curriculum-full.ttl", format="turtle")

# Query the graph
for subj, pred, obj in g.triples((None, RDFS.label, None)):
    print(f"{subj}: {obj}")
```

**JavaScript with JSON-LD:**
```javascript
// Download JSON-LD file
const response = await fetch('https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/index.jsonld');
const data = await response.json();

// Access RDF data
data['@graph'].forEach(item => {
  console.log(item['rdfs:label']['@value']);
});
```

---

## Querying the SPARQL Endpoint

The curriculum data is queryable via a SPARQL HTTP endpoint.

**Endpoint:** `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql`

### Python Example

```python
import requests

endpoint = "https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql"

query = """
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?label WHERE {
  ?subject a curric:Subject ;
           rdfs:label ?label .
}
ORDER BY ?label
"""

response = requests.post(
    endpoint,
    data=query,
    headers={
        'Content-Type': 'application/sparql-query',
        'Accept': 'application/json'
    }
)

data = response.json()
for binding in data['results']['bindings']:
    print(f"{binding['subject']['value']}: {binding['label']['value']}")
```

### JavaScript (Node.js) Example

```javascript
const fetch = require('node-fetch');

const endpoint = 'https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql';

const query = `
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label WHERE {
  ?scheme curric:hasSubject eng:subject-science ;
          curric:hasKeyStage eng:key-stage-3 ;
          curric:hasContent ?content .
  ?content skos:prefLabel ?label .
}
LIMIT 10
`;

fetch(endpoint, {
  method: 'POST',
  body: query,
  headers: {
    'Content-Type': 'application/sparql-query',
    'Accept': 'application/json'
  }
})
.then(res => res.json())
.then(data => {
  data.results.bindings.forEach(item => {
    console.log(`${item.content.value}: ${item.label.value}`);
  });
});
```

### curl Example

```bash
# Save query to file
cat > query.sparql <<'SPARQL'
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?ks ?label WHERE {
  ?ks a curric:KeyStage ;
      skos:prefLabel ?label .
}
ORDER BY ?label
SPARQL

# Execute query
curl -X POST \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: application/json" \
    --data-binary @query.sparql \
    https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql | jq .
```

## Common Queries

### Find Content by Keyword

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label ?definition WHERE {
  ?content skos:prefLabel ?label ;
           skos:definition ?definition .
  FILTER(CONTAINS(LCASE(?definition), "photosynthesis"))
}
```

### Get All Content for a Subject

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX eng: <https://w3id.org/uk/curriculum/england/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?content ?label WHERE {
  ?scheme curric:hasSubject eng:subject-science ;
          curric:hasContent ?content .
  ?content skos:prefLabel ?label .
}
```

### Find Cross-Cutting Themes

```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?theme ?themeLabel ?content ?contentLabel WHERE {
  ?content curric:hasTheme ?theme .
  ?theme skos:prefLabel ?themeLabel .
  ?content skos:prefLabel ?contentLabel .
}
```

## Property Patterns

**Important:** Different entity types use different property patterns:

### Subject Entities

**Classes:** `curric:Subject`, `curric:SubSubject`, `curric:Scheme`

**Properties:**
- Label: `rdfs:label` (required)
- Description: `rdfs:comment` (optional)

**Example:**
```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?label ?comment WHERE {
  ?subject a curric:Subject ;
           rdfs:label ?label .
  OPTIONAL { ?subject rdfs:comment ?comment }
}
```

### SKOS Concepts

**Classes:** `curric:Discipline`, `curric:Strand`, `curric:SubStrand`, `curric:ContentDescriptor`, `curric:ContentSubDescriptor`

**Properties:**
- Label: `skos:prefLabel` (required)
- Description: `skos:definition` (optional)

**Example:**
```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?descriptor ?label ?definition WHERE {
  ?descriptor a curric:ContentDescriptor ;
              skos:prefLabel ?label .
  OPTIONAL { ?descriptor skos:definition ?definition }
}
```

## Response Format

All SPARQL queries return JSON in the SPARQL 1.1 Query Results JSON Format:

```json
{
  "head": {
    "vars": ["subject", "label"]
  },
  "results": {
    "bindings": [
      {
        "subject": {
          "type": "uri",
          "value": "https://w3id.org/uk/curriculum/england/subject-science"
        },
        "label": {
          "type": "literal",
          "value": "Science",
          "xml:lang": "en"
        }
      }
    ]
  }
}
```

## Error Handling

### Python Example with Error Handling

```python
import requests

endpoint = "https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql"

query = """
SELECT * WHERE { ?s ?p ?o } LIMIT 10
"""

try:
    response = requests.post(
        endpoint,
        data=query,
        headers={
            'Content-Type': 'application/sparql-query',
            'Accept': 'application/json'
        },
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    print(f"Found {len(data['results']['bindings'])} results")

except requests.exceptions.Timeout:
    print("Query timeout - try a more specific query")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Rate Limiting

The public SPARQL endpoint has no explicit rate limits, but please:
- Cache results when possible
- Avoid unnecessary repeated queries
- Use JSON downloads for bulk data access
- Contact us if you need higher query volumes
