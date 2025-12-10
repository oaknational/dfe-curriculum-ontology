#!/bin/bash
# Local validation script that matches CI/CD exactly
set -e

echo "========================================================================"
echo "LOCAL VALIDATION (matches CI/CD)"
echo "========================================================================"
echo ""

echo "Step 1: Merge TTL files with auto-discovery..."
python3 scripts/merge_ttls.py

echo ""
echo "Step 2: Run SHACL validation..."

# Try to find pyshacl - check venv first, then system
if [ -f ".venv/bin/pyshacl" ]; then
    PYSHACL=".venv/bin/pyshacl"
elif command -v pyshacl &> /dev/null; then
    PYSHACL="pyshacl"
else
    echo "❌ Error: pyshacl not found"
    echo ""
    echo "Install it with:"
    echo "  pip install pyshacl"
    echo ""
    echo "Or if using a virtual environment:"
    echo "  .venv/bin/pip install pyshacl"
    exit 1
fi

$PYSHACL \
  --shacl ontology/curriculum-constraints.ttl \
  --ont-graph ontology/curriculum-ontology.ttl \
  --inference rdfs \
  --abort \
  --format human \
  /tmp/combined-data.ttl

echo ""
echo "========================================================================"
echo "✅ All validation passed!"
echo "========================================================================"
