#!/usr/bin/env python3
"""
Sanity CMS to TTL Converter

Converts curriculum data from Sanity CMS JSON format to RDF Turtle (.ttl) files
that conform to the DfE Curriculum Ontology.

Usage:
    python scripts/sanity_to_ttl.py [--api | --sample] [--subjects SUBJECTS] [--incremental]

Options:
    --api          Fetch data from Sanity API (requires credentials)
    --sample       Use sample JSON data for testing (default)
    --subjects     Comma-separated list of subjects to update (e.g., 'science,history')
                   Use 'all' to update everything (default: all)
    --incremental  Only fetch documents changed since last run (requires --api)

Examples:
    # Test with sample data
    python scripts/sanity_to_ttl.py --sample

    # Update only science from Sanity
    python scripts/sanity_to_ttl.py --api --subjects science

    # Update everything from Sanity
    python scripts/sanity_to_ttl.py --api --subjects all

    # Incremental update (only changed documents)
    python scripts/sanity_to_ttl.py --api --incremental
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD

# Namespaces
CURRIC = Namespace("https://w3id.org/uk/curriculum/core/")
ENG = Namespace("https://w3id.org/uk/curriculum/england/")
DC = Namespace("http://purl.org/dc/elements/1.1/")

# Output paths
OUTPUT_DIR = "data/national-curriculum-for-england"
SUBJECTS_DIR = f"{OUTPUT_DIR}/subjects"


def fetch_from_sanity_api():
    """
    Fetch curriculum data from Sanity API.

    Requires environment variables:
    - SANITY_PROJECT_ID
    - SANITY_DATASET (usually 'production')
    - SANITY_TOKEN (read-only API token)
    """
    # TODO: Uncomment when ready to use Sanity API
    """
    import requests

    project_id = os.getenv('SANITY_PROJECT_ID')
    dataset = os.getenv('SANITY_DATASET', 'production')
    token = os.getenv('SANITY_TOKEN')

    if not all([project_id, dataset, token]):
        raise ValueError("Missing Sanity credentials. Set SANITY_PROJECT_ID, SANITY_DATASET, SANITY_TOKEN")

    base_url = f"https://{project_id}.api.sanity.io/v2021-10-21/data/query/{dataset}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Fetch all document types
    queries = {
        'phases': '*[_type == "phase"]',
        'keyStages': '*[_type == "keyStage"]{..., phase->{_id, label}}',
        'yearGroups': '*[_type == "yearGroup"]{..., keyStage->{_id, label}}',
        'disciplines': '*[_type == "discipline"]',
        'subjects': '*[_type == "subject"]{..., disciplines[]->{_id, prefLabel}}',
        'strands': '*[_type == "strand"]{..., discipline->{_id, prefLabel}}',
        'substrands': '*[_type == "substrand"]{..., strand->{_id, prefLabel}}',
        'contentDescriptors': '*[_type == "contentDescriptor"]{..., substrand->{_id, prefLabel}}',
        'contentSubdescriptors': '*[_type == "contentSubdescriptor"]{..., contentDescriptor->{_id, prefLabel}}',
        'subsubjects': '*[_type == "subsubject"]{..., subject->{_id, label}, strands[]->{_id, prefLabel}}',
        'schemes': '*[_type == "scheme"]{..., subsubject->{_id, label}, keyStage->{_id, label}, contentDescriptors[]->{_id}}',
        'progressions': '*[_type == "progression"]{..., scheme->{_id, label}, substrand->{_id, prefLabel}, contentDescriptors[]->{_id}}',
        'themes': '*[_type == "theme"]'
    }

    data = {}
    for key, query in queries.items():
        response = requests.get(base_url, params={'query': query}, headers=headers)
        response.raise_for_status()
        data[key] = response.json().get('result', [])

    return data
    """
    raise NotImplementedError("API fetching not yet implemented. Use --sample flag.")


def load_sample_data():
    """Load sample JSON data for testing."""
    sample_file = "sanity-sample-data/sample-data.json"

    if not os.path.exists(sample_file):
        raise FileNotFoundError(f"Sample data file not found: {sample_file}")

    with open(sample_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_uri_from_id(doc_id: str) -> URIRef:
    """Convert Sanity document ID to RDF URI."""
    # Remove 'drafts.' prefix if present
    doc_id = doc_id.replace('drafts.', '')
    return ENG[doc_id]


def get_slug(doc: Dict) -> str:
    """Extract slug from Sanity document."""
    if 'id' in doc and isinstance(doc['id'], dict):
        return doc['id'].get('current', '')
    return doc.get('_id', '').replace('drafts.', '')


def resolve_reference(ref: Any, data_store: Dict) -> URIRef:
    """Resolve a Sanity reference to a URI."""
    if isinstance(ref, dict) and '_ref' in ref:
        ref_id = ref['_ref']
        return get_uri_from_id(ref_id)
    return None


def create_graph() -> Graph:
    """Create and configure RDF graph with namespaces."""
    g = Graph()
    g.bind("curric", CURRIC)
    g.bind("eng", ENG)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("skos", SKOS)
    g.bind("dc", DC)
    g.bind("dcterms", DCTERMS)
    g.bind("xsd", XSD)
    return g


def add_ontology_header(g: Graph, uri: str, title: str, description: str, version: str = "0.1.0"):
    """Add ontology metadata to graph."""
    ontology_uri = URIRef(uri)

    g.add((ontology_uri, RDF.type, OWL.Ontology))
    g.add((ontology_uri, RDFS.label, Literal(title, lang="en")))
    g.add((ontology_uri, DC.title, Literal(title, lang="en")))
    g.add((ontology_uri, RDFS.comment, Literal(description, lang="en")))
    g.add((ontology_uri, OWL.versionInfo, Literal(version)))
    g.add((ontology_uri, DCTERMS.creator, Literal("Department for Education")))
    g.add((ontology_uri, DCTERMS.created, Literal(datetime.now().strftime("%Y-%m-%d"), datatype=XSD.date)))
    g.add((ontology_uri, DCTERMS.license, URIRef("http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/")))
    g.add((ontology_uri, DCTERMS.rights, Literal("Crown Copyright", lang="en")))
    g.add((ontology_uri, OWL.imports, URIRef(CURRIC)))


def convert_phases(data: List[Dict], g: Graph):
    """Convert Phase documents to RDF."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, CURRIC.Phase))
        g.add((uri, RDFS.label, Literal(doc['label'], lang="en")))
        g.add((uri, RDFS.comment, Literal(doc['description'], lang="en")))
        g.add((uri, CURRIC.lowerAgeBoundary, Literal(doc['lowerAgeBoundary'], datatype=XSD.nonNegativeInteger)))
        g.add((uri, CURRIC.upperAgeBoundary, Literal(doc['upperAgeBoundary'], datatype=XSD.positiveInteger)))


def convert_key_stages(data: List[Dict], g: Graph):
    """Convert KeyStage documents to RDF."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, CURRIC.KeyStage))
        g.add((uri, RDFS.label, Literal(doc['label'], lang="en")))
        g.add((uri, RDFS.comment, Literal(doc['description'], lang="en")))
        g.add((uri, CURRIC.lowerAgeBoundary, Literal(doc['lowerAgeBoundary'], datatype=XSD.nonNegativeInteger)))
        g.add((uri, CURRIC.upperAgeBoundary, Literal(doc['upperAgeBoundary'], datatype=XSD.positiveInteger)))

        # Add phase relationship
        if 'phase' in doc:
            phase_uri = resolve_reference(doc['phase'], {})
            if phase_uri:
                g.add((uri, CURRIC.isPartOf, phase_uri))


def convert_disciplines(data: List[Dict], g: Graph):
    """Convert Discipline documents to RDF (SKOS Concepts)."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, RDF.type, CURRIC.Discipline))
        g.add((uri, SKOS.prefLabel, Literal(doc['prefLabel'], lang="en")))
        g.add((uri, SKOS.definition, Literal(doc['definition'], lang="en")))

        if 'scopeNote' in doc and doc['scopeNote']:
            g.add((uri, SKOS.scopeNote, Literal(doc['scopeNote'], lang="en")))

        g.add((uri, SKOS.topConceptOf, ENG['knowledge-taxonomy']))
        g.add((uri, SKOS.inScheme, ENG['knowledge-taxonomy']))


def convert_subjects(data: List[Dict], g: Graph):
    """Convert Subject documents to RDF."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, CURRIC.Subject))
        g.add((uri, RDFS.label, Literal(doc['label'], lang="en")))
        g.add((uri, RDFS.comment, Literal(doc['description'], lang="en")))

        # Add discipline relationships
        if 'disciplines' in doc:
            for disc_ref in doc['disciplines']:
                disc_uri = resolve_reference(disc_ref, {})
                if disc_uri:
                    g.add((uri, CURRIC.hasDiscipline, disc_uri))


def convert_strands(data: List[Dict], g: Graph):
    """Convert Strand documents to RDF (SKOS Concepts)."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, RDF.type, CURRIC.Strand))
        g.add((uri, SKOS.prefLabel, Literal(doc['prefLabel'], lang="en")))

        if 'definition' in doc and doc['definition']:
            g.add((uri, SKOS.definition, Literal(doc['definition'], lang="en")))

        # Add discipline relationship
        if 'discipline' in doc:
            disc_uri = resolve_reference(doc['discipline'], {})
            if disc_uri:
                g.add((uri, SKOS.broader, disc_uri))

        g.add((uri, SKOS.inScheme, ENG['knowledge-taxonomy']))


def convert_substrands(data: List[Dict], g: Graph):
    """Convert SubStrand documents to RDF (SKOS Concepts)."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, RDF.type, CURRIC.SubStrand))
        g.add((uri, SKOS.prefLabel, Literal(doc['prefLabel'], lang="en")))

        if 'definition' in doc and doc['definition']:
            g.add((uri, SKOS.definition, Literal(doc['definition'], lang="en")))

        # Add strand relationship
        if 'strand' in doc:
            strand_uri = resolve_reference(doc['strand'], {})
            if strand_uri:
                g.add((uri, SKOS.broader, strand_uri))

        g.add((uri, SKOS.inScheme, ENG['knowledge-taxonomy']))


def convert_content_descriptors(data: List[Dict], g: Graph):
    """Convert ContentDescriptor documents to RDF (SKOS Concepts)."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, RDF.type, CURRIC.ContentDescriptor))
        g.add((uri, SKOS.prefLabel, Literal(doc['prefLabel'], lang="en")))

        if 'definition' in doc and doc['definition']:
            g.add((uri, SKOS.definition, Literal(doc['definition'], lang="en")))

        # Add substrand relationship
        if 'substrand' in doc:
            substrand_uri = resolve_reference(doc['substrand'], {})
            if substrand_uri:
                g.add((uri, SKOS.broader, substrand_uri))

        g.add((uri, SKOS.inScheme, ENG['knowledge-taxonomy']))


def convert_content_subdescriptors(data: List[Dict], g: Graph):
    """Convert ContentSubDescriptor documents to RDF (SKOS Concepts)."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, RDF.type, CURRIC.ContentSubDescriptor))
        g.add((uri, SKOS.prefLabel, Literal(doc['prefLabel'], lang="en")))

        if 'definition' in doc and doc['definition']:
            g.add((uri, SKOS.definition, Literal(doc['definition'], lang="en")))

        # Add content descriptor relationship
        if 'contentDescriptor' in doc:
            cd_uri = resolve_reference(doc['contentDescriptor'], {})
            if cd_uri:
                g.add((uri, SKOS.broader, cd_uri))

        # Add examples
        if 'exampleText' in doc and doc['exampleText']:
            g.add((uri, CURRIC.example, Literal(doc['exampleText'], lang="en")))

        if 'exampleUrl' in doc and doc['exampleUrl']:
            g.add((uri, CURRIC.exampleURL, Literal(doc['exampleUrl'], datatype=XSD.anyURI)))

        g.add((uri, SKOS.inScheme, ENG['knowledge-taxonomy']))


def convert_subsubjects(data: List[Dict], g: Graph):
    """Convert SubSubject documents to RDF."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, CURRIC.SubSubject))
        g.add((uri, RDFS.label, Literal(doc['label'], lang="en")))
        g.add((uri, RDFS.comment, Literal(doc['description'], lang="en")))

        if 'fullDescription' in doc and doc['fullDescription']:
            g.add((uri, DCTERMS.description, Literal(doc['fullDescription'], lang="en")))

        if 'sourceUrl' in doc and doc['sourceUrl']:
            g.add((uri, DCTERMS.source, URIRef(doc['sourceUrl'])))

        # Add subject relationship
        if 'subject' in doc:
            subject_uri = resolve_reference(doc['subject'], {})
            if subject_uri:
                g.add((uri, CURRIC.isPartOf, subject_uri))

        # Add strand relationships
        if 'strands' in doc:
            for strand_ref in doc['strands']:
                strand_uri = resolve_reference(strand_ref, {})
                if strand_uri:
                    g.add((uri, CURRIC.hasStrand, strand_uri))

        # Add aims
        if 'aims' in doc:
            for aim in doc['aims']:
                if 'aimText' in aim:
                    g.add((uri, CURRIC.hasAim, Literal(aim['aimText'], lang="en")))


def convert_schemes(data: List[Dict], g: Graph):
    """Convert Scheme documents to RDF."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, CURRIC.Scheme))
        g.add((uri, RDFS.label, Literal(doc['label'], lang="en")))
        g.add((uri, RDFS.comment, Literal(doc['description'], lang="en")))

        # Add subsubject relationship
        if 'subsubject' in doc:
            subsubject_uri = resolve_reference(doc['subsubject'], {})
            if subsubject_uri:
                g.add((uri, CURRIC.isPartOf, subsubject_uri))

        # Add key stage relationship
        if 'keyStage' in doc:
            ks_uri = resolve_reference(doc['keyStage'], {})
            if ks_uri:
                g.add((uri, CURRIC.hasKeyStage, ks_uri))

        # Add content descriptor relationships
        if 'contentDescriptors' in doc:
            for cd_ref in doc['contentDescriptors']:
                cd_uri = resolve_reference(cd_ref, {})
                if cd_uri:
                    g.add((uri, CURRIC.hasContentDescriptor, cd_uri))


def convert_themes(data: List[Dict], g: Graph):
    """Convert Theme documents to RDF (SKOS Concepts)."""
    for doc in data:
        uri = get_uri_from_id(get_slug(doc))

        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, RDF.type, CURRIC.Theme))
        g.add((uri, SKOS.prefLabel, Literal(doc['prefLabel'], lang="en")))
        g.add((uri, SKOS.definition, Literal(doc['definition'], lang="en")))
        g.add((uri, SKOS.inScheme, ENG['themes-scheme']))


def write_ttl_file(g: Graph, filepath: str):
    """Write graph to TTL file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Serialize to TTL format
    ttl_content = g.serialize(format='turtle')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(ttl_content)

    print(f"✓ Written: {filepath}")


def discover_subjects(data: Dict) -> List[str]:
    """
    Discover all subjects present in the data.
    Returns list of subject IDs (e.g., ['science', 'history', 'mathematics'])
    """
    subjects = set()

    # Get explicit subjects
    for subject in data.get('subjects', []):
        subject_id = get_slug(subject)
        if subject_id and subject_id.startswith('subject-'):
            subject_name = subject_id.replace('subject-', '')
            subjects.add(subject_name)

    # Also check subsubjects to catch any subjects we might have missed
    for subsubject in data.get('subsubjects', []):
        if 'subject' in subsubject:
            subject_ref = resolve_reference(subsubject['subject'], {})
            if subject_ref:
                subject_name = str(subject_ref).split('/')[-1].replace('subject-', '')
                subjects.add(subject_name)

    return sorted(list(subjects))


def get_subject_data(data: Dict, subject: str) -> Dict:
    """
    Filter data to only include documents for the specified subject.
    Follows reference chains to get complete subject data.
    """
    subject_data = {}

    # Filter subjects
    subject_data['subjects'] = [
        s for s in data.get('subjects', [])
        if get_slug(s).replace('subject-', '') == subject
    ]

    # Filter subsubjects
    subject_data['subsubjects'] = [
        ss for ss in data.get('subsubjects', [])
        if 'subject' in ss and
        str(resolve_reference(ss['subject'], {})).endswith(f'subject-{subject}')
    ]

    # Get discipline IDs used by this subject
    discipline_ids = set()
    for subj in subject_data['subjects']:
        for disc_ref in subj.get('disciplines', []):
            disc_uri = resolve_reference(disc_ref, {})
            if disc_uri:
                discipline_ids.add(str(disc_uri).split('/')[-1])

    # Filter disciplines
    subject_data['disciplines'] = [
        d for d in data.get('disciplines', [])
        if get_slug(d) in discipline_ids
    ]

    # Get strands that reference these disciplines
    strand_ids = set()
    for strand in data.get('strands', []):
        if 'discipline' in strand:
            disc_ref = str(resolve_reference(strand['discipline'], {})).split('/')[-1]
            if disc_ref in discipline_ids:
                strand_ids.add(get_slug(strand))

    subject_data['strands'] = [
        s for s in data.get('strands', [])
        if get_slug(s) in strand_ids
    ]

    # Get substrands for these strands
    substrand_ids = set()
    for substrand in data.get('substrands', []):
        if 'strand' in substrand:
            strand_ref = str(resolve_reference(substrand['strand'], {})).split('/')[-1]
            if strand_ref in strand_ids:
                substrand_ids.add(get_slug(substrand))

    subject_data['substrands'] = [
        ss for ss in data.get('substrands', [])
        if get_slug(ss) in substrand_ids
    ]

    # Get content descriptors for these substrands
    descriptor_ids = set()
    for cd in data.get('contentDescriptors', []):
        if 'substrand' in cd:
            substrand_ref = str(resolve_reference(cd['substrand'], {})).split('/')[-1]
            if substrand_ref in substrand_ids:
                descriptor_ids.add(get_slug(cd))

    subject_data['contentDescriptors'] = [
        cd for cd in data.get('contentDescriptors', [])
        if get_slug(cd) in descriptor_ids
    ]

    # Get content subdescriptors for these descriptors
    subject_data['contentSubdescriptors'] = [
        csd for csd in data.get('contentSubdescriptors', [])
        if 'contentDescriptor' in csd and
        str(resolve_reference(csd['contentDescriptor'], {})).split('/')[-1] in descriptor_ids
    ]

    # Get schemes for this subject's subsubjects
    subsubject_ids = set(get_slug(ss) for ss in subject_data['subsubjects'])
    subject_data['schemes'] = [
        sch for sch in data.get('schemes', [])
        if 'subsubject' in sch and
        str(resolve_reference(sch['subsubject'], {})).split('/')[-1] in subsubject_ids
    ]

    return subject_data


def generate_subject_files(subject: str, subject_data: Dict):
    """Generate all TTL files for a subject."""

    subject_dir = f"{SUBJECTS_DIR}/{subject}"
    subject_title = subject.replace('-', ' ').title()

    print(f"\n   Converting {subject_title}...")

    # Count documents
    counts = {
        'subjects': len(subject_data.get('subjects', [])),
        'disciplines': len(subject_data.get('disciplines', [])),
        'strands': len(subject_data.get('strands', [])),
        'contentDescriptors': len(subject_data.get('contentDescriptors', [])),
        'schemes': len(subject_data.get('schemes', []))
    }

    if counts['subjects'] == 0:
        print(f"   ⚠️  No data found for {subject_title}, skipping")
        return

    # 1. Subject file
    subject_graph = create_graph()
    add_ontology_header(
        subject_graph,
        f"https://w3id.org/uk/curriculum/england/{subject}-subject",
        f"National Curriculum for England - {subject_title} Subject",
        f"{subject_title} subject definition, including aims and strands."
    )

    if subject_data.get('subjects'):
        convert_subjects(subject_data['subjects'], subject_graph)
    if subject_data.get('subsubjects'):
        convert_subsubjects(subject_data['subsubjects'], subject_graph)

    write_ttl_file(subject_graph, f"{subject_dir}/{subject}-subject.ttl")

    # 2. Knowledge taxonomy file
    taxonomy_graph = create_graph()
    add_ontology_header(
        taxonomy_graph,
        f"https://w3id.org/uk/curriculum/england/{subject}-knowledge-taxonomy",
        f"National Curriculum for England - {subject_title} Knowledge Taxonomy",
        f"{subject_title} knowledge taxonomy from disciplines to content descriptors."
    )

    if subject_data.get('disciplines'):
        convert_disciplines(subject_data['disciplines'], taxonomy_graph)
    if subject_data.get('strands'):
        convert_strands(subject_data['strands'], taxonomy_graph)
    if subject_data.get('substrands'):
        convert_substrands(subject_data['substrands'], taxonomy_graph)
    if subject_data.get('contentDescriptors'):
        convert_content_descriptors(subject_data['contentDescriptors'], taxonomy_graph)
    if subject_data.get('contentSubdescriptors'):
        convert_content_subdescriptors(subject_data['contentSubdescriptors'], taxonomy_graph)

    write_ttl_file(taxonomy_graph, f"{subject_dir}/{subject}-knowledge-taxonomy.ttl")

    # 3. Schemes file
    schemes_graph = create_graph()
    add_ontology_header(
        schemes_graph,
        f"https://w3id.org/uk/curriculum/england/{subject}-schemes",
        f"National Curriculum for England - {subject_title} Schemes",
        f"{subject_title} schemes mapping content to key stages."
    )

    if subject_data.get('schemes'):
        convert_schemes(subject_data['schemes'], schemes_graph)

    write_ttl_file(schemes_graph, f"{subject_dir}/{subject}-schemes.ttl")

    # Print summary
    print(f"      ✓ {counts['subjects']} subjects, {counts['disciplines']} disciplines, "
          f"{counts['strands']} strands, {counts['contentDescriptors']} descriptors, "
          f"{counts['schemes']} schemes")


def main():
    """Main conversion process."""
    print("=" * 60)
    print("Sanity CMS → TTL Converter")
    print("=" * 60)

    # Determine data source
    use_api = '--api' in sys.argv

    # Load data
    print("\n📥 Loading data...")
    if use_api:
        print("   Source: Sanity API")
        data = fetch_from_sanity_api()
    else:
        print("   Source: Sample JSON file")
        data = load_sample_data()

    print(f"   ✓ Loaded {sum(len(v) if isinstance(v, list) else 0 for v in data.values())} documents")

    # Create graphs for different files
    print("\n🔄 Converting to RDF...")

    # 1. Programme Structure
    print("\n   Converting programme structure...")
    prog_graph = create_graph()
    add_ontology_header(
        prog_graph,
        "https://w3id.org/uk/curriculum/england/programme-structure",
        "National Curriculum for England - Programme Structure",
        "Programme structure defining phases, key stages, and year groups."
    )

    if 'phases' in data:
        convert_phases(data['phases'], prog_graph)
    if 'keyStages' in data:
        convert_key_stages(data['keyStages'], prog_graph)
    if 'yearGroups' in data:
        # Year groups conversion (similar to key stages)
        pass

    write_ttl_file(prog_graph, f"{OUTPUT_DIR}/programme-structure.ttl")

    # 2. Themes
    if 'themes' in data and data['themes']:
        print("\n   Converting themes...")
        themes_graph = create_graph()
        add_ontology_header(
            themes_graph,
            "https://w3id.org/uk/curriculum/england/themes",
            "National Curriculum for England - Themes",
            "Cross-cutting themes spanning multiple subjects."
        )

        # Add the themes concept scheme
        themes_graph.add((ENG['themes-scheme'], RDF.type, SKOS.ConceptScheme))
        themes_graph.add((ENG['themes-scheme'], SKOS.prefLabel, Literal("Cross-Cutting Themes", lang="en")))

        convert_themes(data['themes'], themes_graph)
        write_ttl_file(themes_graph, f"{OUTPUT_DIR}/themes.ttl")

    # 3. Discover and process all subjects dynamically
    print("\n🔍 Discovering subjects...")
    subjects = discover_subjects(data)

    if not subjects:
        print("   ⚠️  No subjects found in data")
    else:
        print(f"   Found subjects: {', '.join(subjects)}")

        print("\n📚 Processing subjects...")
        for subject in subjects:
            # Get data for this subject only
            subject_data = get_subject_data(data, subject)

            # Generate all files for this subject
            generate_subject_files(subject, subject_data)

    print("\n" + "=" * 60)
    print("✅ Conversion complete!")
    print("=" * 60)
    print(f"\nGenerated files in: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("  1. Validate: ./scripts/validate.sh")
    print("  2. Review: Check generated TTL files")
    print("  3. Commit: Add to version control")


if __name__ == "__main__":
    main()
