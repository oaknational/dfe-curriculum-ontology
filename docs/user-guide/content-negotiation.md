# Content Negotiation Guide

This guide explains how to access curriculum data in different RDF formats using HTTP content negotiation.

## What is Content Negotiation?

Content negotiation is an HTTP mechanism that allows the same URI to return different representations based on the client's preferences. By setting the `Accept` header in your HTTP request, you can request the data format that best suits your needs.

## Supported Formats

The SPARQL endpoint supports three RDF serialization formats:

| Format | Accept Header | File Extension | Use Case |
|--------|--------------|----------------|----------|
| **Turtle** | `text/turtle` | `.ttl` | Compact, human-readable RDF. Good for debugging and manual inspection. |
| **JSON-LD** | `application/ld+json` | `.jsonld` | JSON-based RDF. Ideal for web applications and JavaScript developers. |
| **RDF/XML** | `application/rdf+xml` | `.rdf` | XML-based RDF. Legacy format for older tools and systems. |

## Three Ways to Access Data

### 1. URI Dereferencing (SPARQL DESCRIBE)

Get all RDF data about a specific resource using SPARQL DESCRIBE queries.

**Endpoint:** `https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql`

#### Example: Get Science Subject

**Turtle:**
```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: text/turtle" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

**Response:**
```turtle
@prefix curric: <https://w3id.org/uk/curriculum/core/> .
@prefix eng: <https://w3id.org/uk/curriculum/england/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

eng:subject-science a curric:Subject ;
    rdfs:label "Science"@en ;
    rdfs:comment "Science subject in the National Curriculum for England."@en ;
    curric:hasDiscipline eng:discipline-science .
```

**JSON-LD:**
```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/ld+json" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

**Response:**
```json
{
  "@id": "eng:subject-science",
  "@type": "curric:Subject",
  "rdfs:label": {
    "@language": "en",
    "@value": "Science"
  },
  "rdfs:comment": {
    "@language": "en",
    "@value": "Science subject in the National Curriculum for England."
  },
  "curric:hasDiscipline": {
    "@id": "eng:discipline-science"
  },
  "@context": {
    "curric": "https://w3id.org/uk/curriculum/core/",
    "eng": "https://w3id.org/uk/curriculum/england/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  }
}
```

**RDF/XML:**
```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/rdf+xml" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

### 2. SPARQL Queries

Execute custom SPARQL queries to retrieve specific data.

**Query Results also support content negotiation:**

| Format | Accept Header | Use Case |
|--------|--------------|----------|
| **JSON** | `application/sparql-results+json` | Default, best for web apps |
| **XML** | `application/sparql-results+xml` | Legacy systems |
| **CSV** | `text/csv` | Data analysis, spreadsheets |
| **TSV** | `text/tab-separated-values` | Data processing |

#### Example: Get All Subjects

**Query:**
```sparql
PREFIX curric: <https://w3id.org/uk/curriculum/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?label WHERE {
  ?subject a curric:Subject ;
           rdfs:label ?label .
}
ORDER BY ?label
```

**As JSON:**
```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/sparql-results+json" \
  --data @query.sparql \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

**As CSV:**
```bash
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: text/csv" \
  --data @query.sparql \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

### 3. Bulk Downloads

Download pre-generated RDF files from GitHub Releases.

**Available datasets:**
- `subjects/index.*` - All subjects
- `subjects/science-ks3.*` - Science Key Stage 3 content
- `curriculum-full.*` - Complete curriculum dataset

**All datasets available in three formats:**
- `.ttl` (Turtle)
- `.jsonld` (JSON-LD)
- `.rdf` (RDF/XML)

**Download examples:**
```bash
# Download subjects index as Turtle
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/index.ttl

# Download Science KS3 as JSON-LD
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/science-ks3.jsonld

# Download full curriculum as RDF/XML
curl -L -O https://github.com/oaknational/uk-curriculum-ontology/releases/latest/download/curriculum-full.rdf
```

## Programming Examples

### Python with rdflib

```python
from rdflib import Graph
import requests

# Fetch resource as Turtle
query = "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>"
response = requests.post(
    "https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql",
    data=query,
    headers={
        "Content-Type": "application/sparql-query",
        "Accept": "text/turtle"
    }
)

# Parse into RDF graph
g = Graph()
g.parse(data=response.text, format="turtle")

# Query the graph
for subj, pred, obj in g:
    print(f"{subj} {pred} {obj}")
```

### JavaScript (Node.js)

```javascript
const fetch = require('node-fetch');

// Fetch resource as JSON-LD
const query = 'DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>';

fetch('https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql', {
  method: 'POST',
  body: query,
  headers: {
    'Content-Type': 'application/sparql-query',
    'Accept': 'application/ld+json'
  }
})
.then(res => res.json())
.then(data => {
  console.log('Subject:', data['rdfs:label']['@value']);
  console.log('Description:', data['rdfs:comment']['@value']);
});
```

### curl with Different Resources

```bash
# Get a Key Stage
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/ld+json" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/key-stage-3>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql

# Get a Content Descriptor
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: text/turtle" \
  --data "DESCRIBE <https://w3id.org/uk/curriculum/england/content-descriptor-cells-as-unit-of-living-organism>" \
  https://national-curriculum-for-england-sparql-6336353060.europe-west1.run.app/national-curriculum-for-england/sparql
```

## Best Practices

### For Web Applications

1. **Use JSON-LD** for easy parsing in JavaScript
2. **Cache responses** to reduce load on the endpoint
3. **Use bulk downloads** for initial data loads
4. **Use SPARQL queries** for dynamic, user-specific requests

### For Data Integration

1. **Use Turtle** for importing into triple stores (most compact)
2. **Use bulk downloads** for batch processing
3. **Validate with riot** after downloading:
   ```bash
   riot --validate curriculum-full.ttl
   ```

### For Legacy Systems

1. **Use RDF/XML** for older RDF tools
2. **Use CSV output** from SPARQL queries for spreadsheets
3. **Download and cache** bulk files locally

## Content Negotiation HTTP Headers

### Request Headers

Set these headers in your HTTP request:

```http
POST /national-curriculum-for-england/sparql HTTP/1.1
Host: national-curriculum-for-england-sparql-6336353060.europe-west1.run.app
Content-Type: application/sparql-query
Accept: text/turtle

DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>
```

### Response Headers

The server responds with matching content type:

```http
HTTP/1.1 200 OK
Content-Type: text/turtle; charset=utf-8
Vary: Accept

@prefix curric: <https://w3id.org/uk/curriculum/core/> .
...
```

## Troubleshooting

### Issue: Empty Response

**Problem:** DESCRIBE query returns empty result

**Solution:** Check that the URI exists in the dataset:
```sparql
ASK WHERE { <https://w3id.org/uk/curriculum/england/subject-science> ?p ?o }
```

### Issue: Format Not Supported

**Problem:** Server returns 406 Not Acceptable

**Solution:** Check your Accept header matches supported formats:
- `text/turtle`
- `application/ld+json`
- `application/rdf+xml`

### Issue: Parsing Errors

**Problem:** Can't parse the response

**Solution:** Verify content type matches your parser:
```python
# Check response content type
print(response.headers['Content-Type'])

# Use matching parser
g.parse(data=response.text, format="turtle")  # for text/turtle
g.parse(data=response.text, format="json-ld")  # for application/ld+json
```

## Further Reading

- [W3C Content Negotiation](https://www.w3.org/Protocols/rfc2616/rfc2616-sec12.html)
- [SPARQL 1.1 Protocol](https://www.w3.org/TR/sparql11-protocol/)
- [Linked Data Principles](https://www.w3.org/DesignIssues/LinkedData.html)
- [RDF 1.1 Primer](https://www.w3.org/TR/rdf11-primer/)
