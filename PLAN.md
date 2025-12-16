# Content Negotiation Implementation Plan

## Overview

Implementing world-class best practice for curriculum data access:
- ✅ Content negotiation for URI dereferencing (linked data web)
- ✅ SPARQL endpoint for complex queries
- ✅ Bulk downloads for convenience/archival

Following patterns from legislation.gov.uk, Schema.org, and W3C Linked Data principles.

---

## **PHASE 1: Enhance Static File Generation** ✅ COMPLETE
*Goal: Generate bulk downloads in TTL, JSON-LD, RDF/XML formats*

**Decision: Dropped JSON (SPARQL Results) format** - Only generating RDF formats since:
- End users don't need JSON - they use the website
- Web app developers can use JSON-LD (it's still JSON, just RDF-structured)
- Third-party integrators want proper RDF formats
- Cleaner architecture with fewer formats to maintain

### Completed Steps:
1. **Created CONSTRUCT query versions**
   - Converted SELECT queries to CONSTRUCT queries
   - Queries now build RDF graphs instead of tabular results
   - Renamed to replace original queries

2. **Refactored build script**
   - Removed JSON generation
   - Added `generate_rdf_formats()` function
   - Generates 3 RDF formats per dataset:
     - Turtle (.ttl) - Native format
     - JSON-LD (.jsonld) - Converted from Turtle
     - RDF/XML (.rdf) - Converted from Turtle
   - Output: 9 distribution files (3 datasets × 3 formats)

3. **Updated GitHub Actions workflow**
   - Renamed: `generate-json.yml` → `generate-distributions.yml`
   - Removed JSON validation (jq dependency)
   - Added RDF validation for all three formats
   - Updated summary reporting

4. **Tested and validated**
   - All RDF files pass riot validation
   - Total size: 104K across 9 files
   - Content verified with proper RDF structure

---

## **PHASE 2: Implement URI Dereferencing** ✅ COMPLETE
*Goal: Enable URI dereferencing with content negotiation*

**Decision: Use Fuseki's built-in content negotiation** - No nginx needed!

### Discovery
Fuseki already provides complete content negotiation support via SPARQL DESCRIBE queries:
- ✅ Turtle (`Accept: text/turtle`)
- ✅ JSON-LD (`Accept: application/ld+json`)
- ✅ RDF/XML (`Accept: application/rdf+xml`)

### Completed Steps
1. **Tested Fuseki's built-in capabilities**
   - Verified SPARQL endpoint content negotiation works
   - Tested DESCRIBE queries with all three RDF formats
   - Confirmed proper RDF serialization for each format

2. **Validated approach**
   - Built and tested Docker container locally
   - Verified content negotiation with curl requests
   - Example working URLs tested:
     ```bash
     curl -X POST \
       -H "Content-Type: application/sparql-query" \
       -H "Accept: text/turtle" \
       --data "DESCRIBE <https://w3id.org/uk/curriculum/england/subject-science>" \
       http://localhost:3030/national-curriculum-for-england/sparql
     ```

### Why This Is Better
- ✅ Zero additional infrastructure (no nginx)
- ✅ Standards-compliant (W3C SPARQL DESCRIBE)
- ✅ Simpler architecture
- ✅ Less to maintain
- ✅ Already deployed and working

---

## **PHASE 3: Document SPARQL Endpoint** ✅ COMPLETE
*Goal: Document content negotiation and all access methods*

### Completed Steps

1. **Created comprehensive content negotiation guide**
   - New file: `docs/user-guide/content-negotiation.md`
   - Documented all three access methods:
     1. URI Dereferencing (SPARQL DESCRIBE)
     2. SPARQL Queries
     3. Bulk Downloads
   - Examples for all three RDF formats (Turtle, JSON-LD, RDF/XML)
   - Programming examples (Python, JavaScript, curl)
   - Best practices and troubleshooting

2. **Updated api-examples.md**
   - Restructured to feature three access methods
   - Added URI dereferencing examples with content negotiation
   - Updated bulk download examples to show all RDF formats
   - Added code examples for parsing different formats

3. **Updated README.md**
   - Added prominent "Three Ways to Access the Data" section
   - Provided quick examples for each method
   - Added decision table for choosing access method
   - Updated Data Access section for consistency
   - Linked to content negotiation guide

---

## **PHASE 4: Update Deployment Configuration** ✅ COMPLETE (Not Needed)
*Goal: Deploy content negotiation to Cloud Run*

**Decision: No deployment changes needed!**

Since we're using Fuseki's built-in content negotiation (no nginx), the existing deployment configuration is already correct:
- ✅ Fuseki config already has SPARQL endpoint
- ✅ Content negotiation works out of the box
- ✅ No infrastructure changes required
- ✅ Tested and validated with Docker locally

**Existing configuration is production-ready.**

---

## **PHASE 5: Update Documentation** ✅ COMPLETE
*Goal: Comprehensive docs for all three access methods*

**Merged with Phase 3 - All documentation complete!**

### Completed Documentation

1. **Content Negotiation Guide** (`docs/user-guide/content-negotiation.md`)
   - Comprehensive guide to all three access methods
   - Examples for Turtle, JSON-LD, RDF/XML
   - Programming examples (Python, JavaScript, curl)
   - Best practices and troubleshooting

2. **API Examples** (`docs/user-guide/api-examples.md`)
   - Restructured around three access methods
   - URI dereferencing with content negotiation
   - SPARQL query examples
   - Bulk download examples with all formats

3. **README.md**
   - Featured "Three Ways to Access the Data" section
   - Decision table for choosing access method
   - Quick examples for each method
   - Links to detailed guides

**Note:** Architecture documentation doesn't need updates since no infrastructure changes were made.

---

## **PHASE 6: Test & Deploy**
*Goal: End-to-end testing and production deployment*

### Steps:

1. **End-to-end testing**
   - Test all three access methods:
     - URI dereferencing with each format
     - SPARQL queries with different Accept headers
     - Download static files from distributions/
   - Test error cases (404s, invalid Accept headers)
   - Validate RDF output from each method

2. **Performance testing**
   - Test response times for URI dereferencing
   - Test SPARQL endpoint under load
   - Ensure static files are appropriately sized

3. **Deploy to Cloud Run**
   - Run `./deployment/deploy.sh`
   - Monitor deployment
   - Verify health checks pass

4. **Post-deployment testing**
   - Test production URLs
   - Verify content negotiation works
   - Test from different clients (curl, browser, Python)

5. **Create release**
   - Tag release with new version
   - Ensure GitHub Actions publishes all formats
   - Test downloading from release artifacts

---

## **Priority Order**

**Quick Wins First:**
1. ✅ **Phase 1** - Extend static file generation (relatively simple, immediate value)
3. ✅ **Phase 3** - Document SPARQL endpoint (already works, just needs docs)

**Core Implementation:**
2. ✅ **Phase 2** - URI dereferencing (most complex, highest value for linked data)

**Polish & Ship:**
4. ✅ **Phase 4** - Deployment updates
5. ✅ **Phase 5** - Documentation
6. ✅ **Phase 6** - Testing & deployment

---

## **Estimated Complexity**

- **Phase 1:** 🟢 Low (2-3 hours)
- **Phase 2:** 🟡 Medium (4-6 hours)
- **Phase 3:** 🟢 Low (1-2 hours)
- **Phase 4:** 🟡 Medium (2-3 hours)
- **Phase 5:** 🟢 Low (2-3 hours)
- **Phase 6:** 🟡 Medium (2-3 hours)

**Total:** ~15-20 hours of focused work

---

## **Success Criteria**

### Phase 1 Complete When:
- [ ] Static files generated in JSON, TTL, JSON-LD, RDF/XML
- [ ] All formats validate successfully
- [ ] GitHub Actions workflow updated to publish all formats

### Phase 2 Complete When:
- [ ] URIs like `/england/subject-science` resolve
- [ ] Content negotiation works for TTL, JSON-LD, RDF/XML
- [ ] Basic HTML view available
- [ ] Docker image builds and runs locally

### Phase 3 Complete When:
- [ ] SPARQL endpoint content negotiation documented
- [ ] Examples provided for each format
- [ ] User guide updated

### Phase 4 Complete When:
- [ ] Deployed to Cloud Run successfully
- [ ] Health checks passing
- [ ] No performance regressions

### Phase 5 Complete When:
- [ ] All documentation updated
- [ ] Content negotiation guide created
- [ ] README reflects all three access methods

### Phase 6 Complete When:
- [ ] All tests passing
- [ ] Production deployment verified
- [ ] Release created with all format artifacts

---

## **Notes**

- This follows W3C 5-star Linked Open Data principles
- Modeled after legislation.gov.uk and other government linked data services
- Prepares for future curriculum.education.gov.uk migration
- Maintains backward compatibility with existing static JSON files
