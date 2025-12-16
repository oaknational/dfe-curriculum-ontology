# Build Instructions

This document provides instructions for building static JSON files from the UK Curriculum Ontology RDF data.

## Prerequisites

### Required Tools

- **Apache Jena 4.10.0+** (includes `arq`, `riot`, `tdbloader`)
- **Bash** (standard on macOS/Linux)
- **Python 3.x** (optional, for JSON validation)

### Installing Apache Jena

**macOS (Manual Installation):**
```bash
# Download pre-built binaries
cd ~/Downloads
# Download from: https://archive.apache.org/dist/jena/binaries/apache-jena-4.10.0.tar.gz
tar -xzf apache-jena-4.10.0.tar.gz
sudo mv apache-jena-4.10.0 /usr/local/
echo 'export PATH="/usr/local/apache-jena-4.10.0/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Linux (Ubuntu/Debian):**
```bash
wget https://archive.apache.org/dist/jena/binaries/apache-jena-4.10.0.tar.gz
tar -xzf apache-jena-4.10.0.tar.gz
sudo mv apache-jena-4.10.0 /opt/jena
echo 'export PATH="/opt/jena/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Verify Installation:**
```bash
arq --version
riot --version
```

## Building Static JSON Files

### Quick Start

Generate static JSON files from RDF data:

```bash
./scripts/build-static-data.sh
```

### Output

The script generates the following files in the `distributions/` directory:

- **`distributions/subjects/index.json`** - List of all subjects (Science, History, etc.)
- **`distributions/subjects/science-ks3.json`** - Science Key Stage 3 content descriptors
- **`distributions/curriculum-full.json`** - Complete curriculum dataset (for client-side search)

**Note:** Generated files are gitignored and published via GitHub Releases (not committed to repository).

### Build Process

The build script performs the following steps:

1. **Collects data files**: Automatically discovers all `.ttl` files in `ontology/` and `data/` directories
2. **Executes SPARQL queries**: Runs queries from `queries/*.sparql` using Apache Jena's `arq` tool
3. **Generates JSON**: Outputs SPARQL JSON results format files
4. **Reports statistics**: Shows file count and total size

### Expected Output

```
==========================================
🏗️  Building Static JSON Files
==========================================

📦 Collecting data files...
✓ Data files collected

📋 Generating subjects index...
✓ subjects/index.json
🔬 Generating Science KS3...
✓ subjects/science-ks3.json
🌍 Generating full curriculum dataset...
✓ curriculum-full.json

==========================================
✅ Generated 3 JSON files (36K)
==========================================
```

## Validation

### Validate Turtle Syntax

Validate all TTL files before building:

```bash
./scripts/validate.sh
```

This checks:
- Turtle syntax validity (using `riot`)
- SHACL constraints (using `pyshacl`)

### Validate Generated JSON

Check that generated JSON is valid:

```bash
# Validate with Python
for file in distributions/**/*.json; do
    python3 -m json.tool "$file" > /dev/null && echo "✓ $file"
done

# Or with jq (if installed)
for file in distributions/**/*.json; do
    jq empty "$file" && echo "✓ $file"
done
```

## Running SPARQL Queries Manually

All queries are stored in `queries/*.sparql` and can be run independently:

### Example: List All Subjects

```bash
arq --data=ontology/dfe-curriculum-ontology.ttl \
    --data=data/national-curriculum-for-england/subjects/science/science-subject.ttl \
    --data=data/national-curriculum-for-england/subjects/history/history-subject.ttl \
    --query=queries/subjects-index.sparql \
    --results=JSON
```

### Example: Get Science KS3 Content

```bash
arq --data=ontology/dfe-curriculum-ontology.ttl \
    --data=data/national-curriculum-for-england/programme-structure.ttl \
    --data=data/national-curriculum-for-england/subjects/science/*.ttl \
    --query=queries/science-ks3.sparql \
    --results=JSON
```

### Example: Export Full Curriculum

```bash
# Using wildcard expansion (bash)
arq --data=ontology/*.ttl \
    --data=data/national-curriculum-for-england/*.ttl \
    --data=data/national-curriculum-for-england/subjects/**/*.ttl \
    --query=queries/full-curriculum.sparql \
    --results=JSON > full-curriculum.json
```

## Troubleshooting

### Apache Jena Commands Not Found

If `arq` or `riot` are not found:

1. Check installation:
   ```bash
   ls /usr/local/apache-jena-4.10.0/bin/
   ```

2. Check PATH:
   ```bash
   echo $PATH | grep jena
   ```

3. Export PATH manually:
   ```bash
   export PATH="/usr/local/apache-jena-4.10.0/bin:$PATH"
   ```

4. Open new terminal (PATH in `~/.zshrc` applies to new sessions only)

### Build Script Fails

If the build script fails:

1. **Check prerequisites**: Ensure Apache Jena is installed and in PATH
2. **Validate data**: Run `./scripts/validate.sh` to check for data errors
3. **Check file paths**: Ensure all required `.ttl` files exist
4. **Run queries manually**: Test individual SPARQL queries to isolate issues

### Java Warnings

You may see warnings like:
```
WARNING: java.io.tmpdir directory does not exist
```

These are **non-blocking** and can be safely ignored. They don't affect the build output.

### Empty or Missing Output

If generated files are empty or missing:

1. Check that data files contain the expected content
2. Verify SPARQL queries match the data structure
3. Check that the ontology and data files use consistent URIs
4. Review query results by running queries manually with `--results=TEXT` for debugging

## CI/CD Integration

The build process is designed to work in CI environments:

1. **Clone repository**: All required files are tracked in git
2. **Install Apache Jena**: Only external dependency
3. **Run build script**: `./scripts/build-static-data.sh`
4. **Upload artifacts**: Generated JSON files

See `.github/workflows/generate-json.yml` for the CI workflow configuration.

## Development Workflow

### Making Changes

1. **Edit data files**: Modify `.ttl` files in `ontology/` or `data/`
2. **Validate**: Run `./scripts/validate.sh`
3. **Build**: Run `./scripts/build-static-data.sh`
4. **Test**: Inspect generated JSON files
5. **Commit**: Commit only source `.ttl` files (not generated JSON)

### Adding New Queries

1. Create new `.sparql` file in `queries/` directory
2. Test query manually with `arq`
3. Add query execution to `scripts/build-static-data.sh`
4. Run build to generate new JSON file
5. Commit query file and updated build script

## File Locations

- **Source data**: `ontology/`, `data/`
- **SPARQL queries**: `queries/`
- **Build scripts**: `scripts/`
- **Generated output**: `distributions/` (gitignored)
- **Validation**: `scripts/validate.sh`

## Additional Resources

- **Apache Jena Documentation**: https://jena.apache.org/documentation/
- **SPARQL 1.1 Query Language**: https://www.w3.org/TR/sparql11-query/
- **RDF 1.1 Turtle**: https://www.w3.org/TR/turtle/
- **SPARQL JSON Results Format**: https://www.w3.org/TR/sparql11-results-json/

## Support

For questions or issues:
- Review `../../CLAUDE.md` for project-specific guidance
- See [architecture.md](architecture.md) for system architecture
- Open an issue on GitHub
