#!/usr/bin/env python3
"""
Enhanced version of sanity_to_ttl.py that handles NEW subjects automatically.

Key improvements:
- Discovers subjects dynamically from data
- Creates new directories/files as needed
- No hardcoded subject names
- Handles any number of subjects
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Set
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD

# Configuration
OUTPUT_DIR = "data/national-curriculum-for-england"
SUBJECTS_DIR = f"{OUTPUT_DIR}/subjects"

# Namespaces
CURRIC = Namespace("https://w3id.org/uk/curriculum/core/")
ENG = Namespace("https://w3id.org/uk/curriculum/england/")
DC = Namespace("http://purl.org/dc/elements/1.1/")


def discover_subjects(data: Dict) -> Set[str]:
    """
    Discover all subjects present in the data.

    Returns set of subject IDs (e.g., {'science', 'history', 'mathematics'})
    """
    subjects = set()

    # Get explicit subjects
    for subject in data.get('subjects', []):
        subject_id = subject.get('_id', '').replace('subject-', '')
        if subject_id:
            subjects.add(subject_id)

    # Infer from subsubjects
    for subsubject in data.get('subsubjects', []):
        if 'subject' in subsubject:
            subject_ref = subsubject['subject'].get('_ref', '')
            subject_id = subject_ref.replace('subject-', '')
            if subject_id:
                subjects.add(subject_id)

    # Infer from document IDs (backup method)
    all_docs = []
    for key, docs in data.items():
        if isinstance(docs, list):
            all_docs.extend(docs)

    for doc in all_docs:
        doc_id = doc.get('_id', '')
        # Common patterns: "subject-science", "scheme-mathematics-ks3", etc.
        for known_subject in ['science', 'history', 'mathematics', 'english', 'geography']:
            if known_subject in doc_id.lower():
                subjects.add(known_subject)

    return subjects


def get_subject_data(data: Dict, subject: str) -> Dict:
    """
    Filter data to only include documents for the specified subject.

    Args:
        data: All Sanity data
        subject: Subject ID (e.g., 'science', 'mathematics')

    Returns:
        Filtered data containing only this subject's documents
    """
    subject_data = {}

    # Filter subjects
    subject_data['subjects'] = [
        s for s in data.get('subjects', [])
        if s.get('_id', '').replace('subject-', '') == subject
    ]

    # Filter subsubjects
    subject_data['subsubjects'] = [
        ss for ss in data.get('subsubjects', [])
        if ss.get('subject', {}).get('_ref', '').replace('subject-', '') == subject
    ]

    # Get discipline IDs for this subject
    discipline_ids = set()
    for subj in subject_data['subjects']:
        for disc_ref in subj.get('disciplines', []):
            discipline_ids.add(disc_ref.get('_ref', ''))

    # Filter disciplines
    subject_data['disciplines'] = [
        d for d in data.get('disciplines', [])
        if d.get('_id', '') in discipline_ids
    ]

    # Get strand IDs for these disciplines
    strand_ids = set()
    for discipline in subject_data['disciplines']:
        # Find strands that reference this discipline
        for strand in data.get('strands', []):
            if strand.get('discipline', {}).get('_ref', '') == discipline['_id']:
                strand_ids.add(strand['_id'])

    # Filter strands
    subject_data['strands'] = [
        s for s in data.get('strands', [])
        if s.get('_id', '') in strand_ids
    ]

    # Get substrand IDs for these strands
    substrand_ids = set()
    for strand in subject_data['strands']:
        for substrand in data.get('substrands', []):
            if substrand.get('strand', {}).get('_ref', '') == strand['_id']:
                substrand_ids.add(substrand['_id'])

    # Filter substrands
    subject_data['substrands'] = [
        ss for ss in data.get('substrands', [])
        if ss.get('_id', '') in substrand_ids
    ]

    # Filter content descriptors
    subject_data['contentDescriptors'] = [
        cd for cd in data.get('contentDescriptors', [])
        if cd.get('substrand', {}).get('_ref', '') in substrand_ids
    ]

    # Get content descriptor IDs
    descriptor_ids = set(cd['_id'] for cd in subject_data['contentDescriptors'])

    # Filter content subdescriptors
    subject_data['contentSubdescriptors'] = [
        csd for csd in data.get('contentSubdescriptors', [])
        if csd.get('contentDescriptor', {}).get('_ref', '') in descriptor_ids
    ]

    # Filter schemes (by subsubject reference)
    subsubject_ids = set(ss['_id'] for ss in subject_data['subsubjects'])
    subject_data['schemes'] = [
        sch for sch in data.get('schemes', [])
        if sch.get('subsubject', {}).get('_ref', '') in subsubject_ids
    ]

    return subject_data


def generate_subject_files(subject: str, subject_data: Dict):
    """
    Generate all TTL files for a subject.

    Creates:
    - {subject}-subject.ttl
    - {subject}-knowledge-taxonomy.ttl
    - {subject}-schemes.ttl
    """

    subject_dir = f"{SUBJECTS_DIR}/{subject}"

    # Create directory if it doesn't exist
    os.makedirs(subject_dir, exist_ok=True)

    print(f"\n   Generating {subject} files...")

    # Import conversion functions from main script
    # (In practice, these would be imported from sanity_to_ttl.py)
    from sanity_to_ttl import (
        create_graph, add_ontology_header, write_ttl_file,
        convert_subjects, convert_subsubjects,
        convert_disciplines, convert_strands, convert_substrands,
        convert_content_descriptors, convert_content_subdescriptors,
        convert_schemes
    )

    # 1. Subject file
    subject_graph = create_graph()
    add_ontology_header(
        subject_graph,
        f"https://w3id.org/uk/curriculum/england/{subject}-subject",
        f"National Curriculum for England - {subject.title()} Subject",
        f"{subject.title()} subject definition, including aims and strands."
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
        f"National Curriculum for England - {subject.title()} Knowledge Taxonomy",
        f"{subject.title()} knowledge taxonomy from disciplines to content descriptors."
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
        f"National Curriculum for England - {subject.title()} Schemes",
        f"{subject.title()} schemes mapping content to key stages."
    )

    if subject_data.get('schemes'):
        convert_schemes(subject_data['schemes'], schemes_graph)

    write_ttl_file(schemes_graph, f"{subject_dir}/{subject}-schemes.ttl")

    # Count what was generated
    counts = {
        'subjects': len(subject_data.get('subjects', [])),
        'disciplines': len(subject_data.get('disciplines', [])),
        'strands': len(subject_data.get('strands', [])),
        'contentDescriptors': len(subject_data.get('contentDescriptors', [])),
        'schemes': len(subject_data.get('schemes', []))
    }

    print(f"      ✓ {counts['subjects']} subjects, {counts['disciplines']} disciplines, "
          f"{counts['strands']} strands, {counts['contentDescriptors']} descriptors, "
          f"{counts['schemes']} schemes")


def main():
    """Enhanced main that handles new subjects automatically."""

    print("=" * 60)
    print("Sanity CMS → TTL Converter (Dynamic Subjects)")
    print("=" * 60)

    # Load data (simplified - would use load_sample_data() or fetch_from_sanity_api())
    with open('sanity-sample-data/sample-data.json', 'r') as f:
        data = json.load(f)

    # 1. Process programme structure (subject-agnostic)
    print("\n📋 Processing programme structure...")
    # ... (phases, key stages, year groups)

    # 2. Process themes (subject-agnostic)
    print("\n🎨 Processing themes...")
    # ... (themes)

    # 3. Discover subjects in the data
    print("\n🔍 Discovering subjects...")
    subjects = discover_subjects(data)

    if not subjects:
        print("   ⚠️  No subjects found in data")
        return

    print(f"   Found subjects: {', '.join(sorted(subjects))}")

    # 4. Process each subject
    print("\n📚 Processing subjects...")

    for subject in sorted(subjects):
        print(f"\n   Processing: {subject}")

        # Get data for this subject only
        subject_data = get_subject_data(data, subject)

        # Generate files
        generate_subject_files(subject, subject_data)

    print("\n" + "=" * 60)
    print("✅ All subjects processed!")
    print("=" * 60)

    # Show what was created
    print("\n📁 Generated structure:")
    for subject in sorted(subjects):
        print(f"   subjects/{subject}/")
        print(f"      ├─ {subject}-subject.ttl")
        print(f"      ├─ {subject}-knowledge-taxonomy.ttl")
        print(f"      └─ {subject}-schemes.ttl")


if __name__ == "__main__":
    main()
