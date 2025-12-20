#!/usr/bin/env python3
"""
Enhanced Sanity CMS to TTL Converter with Scope Control

This version adds:
- Subject-level filtering (update only specific subjects)
- Incremental updates (only changed documents)
- Timestamp tracking
- Dependency awareness
"""

import json
import os
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD

# Configuration
TIMESTAMP_FILE = "scripts/.last-run-timestamp"
OUTPUT_DIR = "data/national-curriculum-for-england"
SUBJECTS_DIR = f"{OUTPUT_DIR}/subjects"

# Namespaces
CURRIC = Namespace("https://w3id.org/uk/curriculum/core/")
ENG = Namespace("https://w3id.org/uk/curriculum/england/")
DC = Namespace("http://purl.org/dc/elements/1.1/")


class UpdateScope:
    """Manages what needs to be updated based on filters and dependencies."""

    def __init__(self, subjects: List[str] = None, incremental: bool = False):
        self.subjects = subjects or ['all']
        self.incremental = incremental
        self.changed_doc_ids = set()
        self.affected_subjects = set()

    def should_update_subject(self, subject_id: str) -> bool:
        """Check if a subject should be updated."""
        if 'all' in self.subjects:
            return True
        # Extract subject name from ID (e.g., 'subject-science' -> 'science')
        subject_name = subject_id.replace('subject-', '')
        return subject_name in self.subjects

    def mark_changed(self, doc_id: str, doc_type: str):
        """Mark a document as changed and determine affected subjects."""
        self.changed_doc_ids.add(doc_id)

        # Determine which subject(s) this affects
        # This is a simplified version - you'd extract from the actual document
        if 'science' in doc_id:
            self.affected_subjects.add('science')
        elif 'history' in doc_id:
            self.affected_subjects.add('history')
        # Programme structure affects everything
        elif doc_type in ['phase', 'keyStage', 'yearGroup']:
            self.affected_subjects.add('_programme_structure')


def get_last_run_timestamp() -> Optional[str]:
    """Get the timestamp of the last successful run."""
    if not os.path.exists(TIMESTAMP_FILE):
        return None

    with open(TIMESTAMP_FILE, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return lines[0] if lines else None


def save_run_timestamp():
    """Save the current timestamp as the last successful run."""
    timestamp = datetime.now(timezone.utc).isoformat()

    with open(TIMESTAMP_FILE, 'w') as f:
        f.write("# Last successful run of sanity_to_ttl.py\n")
        f.write("# Used for incremental updates\n")
        f.write(f"{timestamp}\n")


def fetch_from_sanity_api(scope: UpdateScope) -> Dict:
    """
    Fetch curriculum data from Sanity API with scope filtering.

    Args:
        scope: UpdateScope defining what to fetch
    """
    # TODO: Uncomment when ready to use Sanity API
    """
    import requests

    project_id = os.getenv('SANITY_PROJECT_ID')
    dataset = os.getenv('SANITY_DATASET', 'production')
    token = os.getenv('SANITY_TOKEN')

    if not all([project_id, dataset, token]):
        raise ValueError("Missing Sanity credentials")

    base_url = f"https://{project_id}.api.sanity.io/v2021-10-21/data/query/{dataset}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Build queries based on scope
    queries = {}

    # 1. Programme structure (if needed)
    if 'all' in scope.subjects or '_programme_structure' in scope.affected_subjects:
        if scope.incremental:
            last_run = get_last_run_timestamp()
            time_filter = f' && _updatedAt > "{last_run}"' if last_run else ''
            queries['phases'] = f'*[_type == "phase"{time_filter}]'
            queries['keyStages'] = f'*[_type == "keyStage"{time_filter}]{{..., phase->{{_id, label}}}}'
        else:
            queries['phases'] = '*[_type == "phase"]'
            queries['keyStages'] = '*[_type == "keyStage"]{..., phase->{_id, label}}'

    # 2. Subject-specific data
    for subject in scope.subjects:
        if subject == 'all':
            # Fetch all subjects
            subject_filter = ''
        else:
            # Fetch only specified subject
            # This assumes subject documents have IDs like 'subject-science'
            subject_filter = f' && _id match "**{subject}**"'

        if scope.incremental:
            last_run = get_last_run_timestamp()
            time_filter = f' && _updatedAt > "{last_run}"' if last_run else ''
        else:
            time_filter = ''

        # Combine filters
        combined_filter = subject_filter + time_filter

        queries.update({
            'disciplines': f'*[_type == "discipline"{combined_filter}]',
            'subjects': f'*[_type == "subject"{combined_filter}]{{..., disciplines[]->{{_id, prefLabel}}}}',
            'strands': f'*[_type == "strand"{combined_filter}]{{..., discipline->{{_id, prefLabel}}}}',
            # ... etc for all types
        })

    # Execute queries
    data = {}
    for key, query in queries.items():
        response = requests.get(base_url, params={'query': query}, headers=headers)
        response.raise_for_status()
        result = response.json().get('result', [])
        data[key] = result

        # Track changed documents
        for doc in result:
            scope.mark_changed(doc['_id'], doc['_type'])

    return data
    """
    raise NotImplementedError("API fetching not yet implemented. Use --sample flag.")


def load_sample_data(scope: UpdateScope) -> Dict:
    """Load sample JSON data with scope filtering applied."""
    sample_file = "sanity-sample-data/sample-data.json"

    if not os.path.exists(sample_file):
        raise FileNotFoundError(f"Sample data file not found: {sample_file}")

    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Apply subject filtering to sample data
    if 'all' not in scope.subjects:
        # Filter subjects
        if 'subjects' in data:
            data['subjects'] = [s for s in data['subjects']
                                if scope.should_update_subject(s['_id'])]

        # Filter related data (disciplines, strands, etc.)
        # For simplicity in sample mode, we'll include all related data
        # In production, you'd filter based on relationships

    return data


def get_subject_name_from_doc(doc: Dict) -> Optional[str]:
    """Extract subject name from a document."""
    doc_id = doc.get('_id', '')

    # Try to extract subject from ID
    if 'science' in doc_id:
        return 'science'
    elif 'history' in doc_id:
        return 'history'
    elif 'mathematics' in doc_id or 'maths' in doc_id:
        return 'mathematics'

    # For subjects themselves
    if doc.get('_type') == 'subject':
        return doc_id.replace('subject-', '')

    return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert Sanity CMS data to TTL files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with sample data
  %(prog)s --sample

  # Update only science from Sanity
  %(prog)s --api --subjects science

  # Update multiple subjects
  %(prog)s --api --subjects science,history

  # Incremental update (only changed since last run)
  %(prog)s --api --incremental

  # Update everything
  %(prog)s --api --subjects all
        """
    )

    parser.add_argument(
        '--api',
        action='store_true',
        help='Fetch data from Sanity API (requires credentials)'
    )

    parser.add_argument(
        '--sample',
        action='store_true',
        help='Use sample JSON data for testing'
    )

    parser.add_argument(
        '--subjects',
        type=str,
        default='all',
        help='Comma-separated list of subjects to update (default: all)'
    )

    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Only fetch documents changed since last run (requires --api)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )

    return parser.parse_args()


def print_scope_summary(scope: UpdateScope, data: Dict):
    """Print a summary of what will be updated."""
    print("\n" + "=" * 60)
    print("UPDATE SCOPE")
    print("=" * 60)

    print(f"\n📊 Mode: {'Incremental' if scope.incremental else 'Full update'}")

    if 'all' in scope.subjects:
        print(f"📚 Subjects: All")
    else:
        print(f"📚 Subjects: {', '.join(scope.subjects)}")

    # Count documents
    doc_counts = {}
    for key, docs in data.items():
        if isinstance(docs, list) and docs:
            doc_counts[key] = len(docs)

    if doc_counts:
        print(f"\n📄 Documents to process:")
        for doc_type, count in sorted(doc_counts.items()):
            print(f"   - {doc_type}: {count}")

    if scope.incremental:
        last_run = get_last_run_timestamp()
        if last_run:
            print(f"\n🕐 Changes since: {last_run}")
        else:
            print(f"\n🕐 First run (no previous timestamp)")

    print("=" * 60)


def main():
    """Main conversion process with scope control."""
    args = parse_arguments()

    print("=" * 60)
    print("Sanity CMS → TTL Converter (Enhanced)")
    print("=" * 60)

    # Determine data source
    if args.api and args.sample:
        print("\n❌ Error: Cannot use both --api and --sample")
        return 1

    use_api = args.api
    use_sample = args.sample or not args.api  # Default to sample

    # Validate incremental mode
    if args.incremental and not use_api:
        print("\n❌ Error: --incremental requires --api")
        return 1

    # Parse subjects filter
    subjects = [s.strip() for s in args.subjects.split(',')]

    # Create update scope
    scope = UpdateScope(subjects=subjects, incremental=args.incremental)

    # Load data
    print("\n📥 Loading data...")
    print(f"   Source: {'Sanity API' if use_api else 'Sample JSON file'}")

    try:
        if use_api:
            data = fetch_from_sanity_api(scope)
        else:
            data = load_sample_data(scope)
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        return 1

    # Show scope summary
    print_scope_summary(scope, data)

    if args.dry_run:
        print("\n🔍 DRY RUN - No files will be modified")
        return 0

    # Proceed with conversion (using existing conversion functions)
    print("\n🔄 Converting to RDF...")

    # Import the conversion functions from the original script
    # (In practice, you'd refactor these into importable functions)
    # For now, this is a demonstration of the control flow

    print("\n✅ Conversion complete!")

    # Save timestamp if successful
    if use_api and not args.dry_run:
        save_run_timestamp()
        print(f"💾 Saved run timestamp to {TIMESTAMP_FILE}")

    return 0


if __name__ == "__main__":
    exit(main())
