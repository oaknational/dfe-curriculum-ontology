#!/bin/bash
# Generate static JSON files from RDF data

set -e

echo "=========================================="
echo "🏗️  Building Static JSON Files"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Output directory
OUTPUT_DIR="distributions"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/subjects" "$OUTPUT_DIR/keystages" "$OUTPUT_DIR/themes"

# Build common data file list
echo -e "${BLUE}📦 Collecting data files...${NC}"
DATA_FILES=""
DATA_FILES="$DATA_FILES --data=ontology/dfe-curriculum-ontology.ttl"
DATA_FILES="$DATA_FILES --data=data/national-curriculum-for-england/programme-structure.ttl"

# Check if themes file exists
if [ -f "data/national-curriculum-for-england/themes.ttl" ]; then
    DATA_FILES="$DATA_FILES --data=data/national-curriculum-for-england/themes.ttl"
fi

# Add all subject files
for file in data/national-curriculum-for-england/subjects/**/*.ttl; do
    if [ -f "$file" ]; then
        DATA_FILES="$DATA_FILES --data=$file"
    fi
done

echo -e "${GREEN}✓${NC} Data files collected"
echo ""

# Generate subjects index
echo -e "${BLUE}📋 Generating subjects index...${NC}"
arq $DATA_FILES \
    --query=queries/subjects-index.sparql \
    --results=JSON > "$OUTPUT_DIR/subjects/index.json"
echo -e "${GREEN}✓${NC} subjects/index.json"

# Generate Science KS3
echo -e "${BLUE}🔬 Generating Science KS3...${NC}"
arq $DATA_FILES \
    --query=queries/science-ks3.sparql \
    --results=JSON > "$OUTPUT_DIR/subjects/science-ks3.json"
echo -e "${GREEN}✓${NC} subjects/science-ks3.json"

# Generate full curriculum
echo -e "${BLUE}🌍 Generating full curriculum dataset...${NC}"
arq $DATA_FILES \
    --query=queries/full-curriculum.sparql \
    --results=JSON > "$OUTPUT_DIR/curriculum-full.json"
echo -e "${GREEN}✓${NC} curriculum-full.json"

# Calculate statistics
echo ""
echo "=========================================="
TOTAL_FILES=$(find "$OUTPUT_DIR" -name "*.json" | wc -l | tr -d ' ')
TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)
echo -e "${GREEN}✅ Generated $TOTAL_FILES JSON files ($TOTAL_SIZE)${NC}"
echo "=========================================="
echo ""

# List files
echo "Generated files:"
find "$OUTPUT_DIR" -name "*.json" -exec echo "  - {}" \;
echo ""
