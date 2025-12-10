#!/usr/bin/env python3
"""
merge_ttls.py

Merge TTL files for validation.
Simpler than oak-curriculum-ontology version (no external imports to resolve).
"""

from pathlib import Path
from rdflib import Graph, URIRef

OUTPUT_FILE = "/tmp/combined-data.ttl"

# Entry points - will auto-discover all .ttl files
ROOT_DIRS = [
    "ontology",
    "data"
]

# OWL imports predicate
OWL_IMPORTS = URIRef("http://www.w3.org/2002/07/owl#imports")


def check_imports(g, repo_root):
    """
    Check that all owl:imports declarations are resolvable.
    Warns about external imports that might not be available.
    """
    external_imports = []
    local_imports = []

    for s, p, o in g.triples((None, OWL_IMPORTS, None)):
        import_uri = str(o)

        # Check if it's a local w3id.org import
        if "w3id.org/uk/curriculum" in import_uri:
            local_imports.append(import_uri)
        elif not import_uri.startswith("http://www.w3.org/"):
            # Skip standard W3C vocabularies (OWL, RDFS, SKOS, etc.)
            external_imports.append(import_uri)

    if local_imports:
        print("\n📋 Local curriculum imports found:")
        for uri in sorted(set(local_imports)):
            print(f"   ✓ {uri}")

    if external_imports:
        print("\n⚠️  External imports found:")
        for uri in sorted(set(external_imports)):
            print(f"   ! {uri}")
        print("   These should resolve via w3id.org or be standard vocabularies.")


def main():
    repo_root = Path(__file__).parent.parent
    g = Graph()
    files_processed = []

    print("=" * 70)
    print("MERGING TTL FILES FOR VALIDATION")
    print("=" * 70)

    for root_dir in ROOT_DIRS:
        dir_path = repo_root / root_dir
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {root_dir}")
            continue

        # Find all .ttl files, excluding versions/
        for ttl_file in sorted(dir_path.rglob("*.ttl")):
            if "versions" in ttl_file.parts:
                print(f"⏭  Skipping versioned file: {ttl_file.relative_to(repo_root)}")
                continue

            print(f"📄 Parsing: {ttl_file.relative_to(repo_root)}")
            try:
                g.parse(str(ttl_file), format="turtle")
                files_processed.append(ttl_file)
            except Exception as e:
                print(f"❌ Error parsing {ttl_file}: {e}")
                raise

    # Check owl:imports declarations
    check_imports(g, repo_root)

    # Serialize merged graph
    g.serialize(destination=OUTPUT_FILE, format="turtle")

    print("\n" + "=" * 70)
    print(f"✅ Successfully merged {len(files_processed)} files into {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()
