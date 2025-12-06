#!/usr/bin/env python3
"""
Local validation script - run before pushing to catch errors early
This runs the same validation as CI/CD
"""
import sys
from pathlib import Path
from rdflib import Graph
from pyshacl import validate

VALIDATION_TARGETS = [
    "data/england/programme-structure.ttl",
    "data/england/themes.ttl",
    "data/england/subjects/science/science-subject.ttl",
    "data/england/subjects/science/science-knowledge-taxonomy.ttl",
    "data/england/subjects/science/science-schemes.ttl",
]


def check_syntax(file_path: Path) -> bool:
    """Check Turtle syntax"""
    print(f"Checking syntax: {file_path}")
    try:
        g = Graph()
        g.parse(file_path, format='turtle')
        print("  ✓ Valid syntax")
        return True
    except Exception as e:
        print(f"  ✗ Syntax error: {e}")
        return False


def validate_shacl(data_file: Path, repo_root: Path) -> bool:
    """Validate against SHACL constraints"""
    print(f"\nValidating: {data_file}")
    print("-" * 60)
    
    shapes_file = repo_root / "ontology" / "curriculum-constraints.ttl"
    ontology_file = repo_root / "ontology" / "curriculum-ontology.ttl"
    
    conforms, _, results_text = validate(
        data_file,
        shacl_graph=shapes_file,
        ont_graph=ontology_file,
        inference='rdfs',
        abort_on_first=False,
    )
    
    if conforms:
        print(f"✅ Valid")
        return True
    else:
        print(f"❌ Validation errors:\n{results_text}")
        return False


def main():
    repo_root = Path(__file__).parent.parent
    files = [repo_root / f for f in VALIDATION_TARGETS]
    
    print("=" * 60)
    print("SYNTAX CHECK")
    print("=" * 60)
    syntax_ok = all(check_syntax(f) for f in files)
    
    if not syntax_ok:
        print("\n❌ Syntax errors found. Fix these before SHACL validation.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("SHACL VALIDATION")
    print("=" * 60)
    validation_ok = all(validate_shacl(f, repo_root) for f in files)
    
    print("\n" + "=" * 60)
    if syntax_ok and validation_ok:
        print("✅ All validations passed!")
        print("\nSafe to push! (CI will run the same checks)")
        sys.exit(0)
    else:
        print("❌ Validation failed")
        print("\n⚠️  Do not push until these are fixed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
