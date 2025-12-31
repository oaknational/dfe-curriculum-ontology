#!/usr/bin/env python3
"""
Export Oak Curriculum Ontology TTL files to Neo4j AuraDB using rdflib-neo4j.

This script uses rdflib-neo4j (not neosemantics) because n10s plugin
is not available on AuraDB Professional.

See: https://neo4j.com/labs/rdflib-neo4j/
"""

import os
import sys
import re
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from rdflib import Graph, Namespace, URIRef
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS - Configuration Validation
# ============================================================================

class LabelMappingConfig(BaseModel):
    """Configuration for replacing node labels."""
    source_label: str = "Resource"
    target_label: str = "Oak"
    uri_pattern: str
    description: Optional[str] = None


class FileDiscoveryConfig(BaseModel):
    """Configuration for discovering TTL files to import."""
    base_dir: str = "data/oak-curriculum"
    include_files: List[str] = []
    include_patterns: List[str] = []
    exclude_patterns: List[str] = ["**/versions/**"]


class FilterConfig(BaseModel):
    """Configuration for filtering RDF triples."""
    exclude_subjects_by_type: List[str] = ["owl:Ontology"]


class RDFSourceConfig(BaseModel):
    """Configuration for RDF data source."""
    namespaces: Dict[str, str]
    file_discovery: FileDiscoveryConfig
    filters: FilterConfig = FilterConfig()


class Neo4jConnectionConfig(BaseModel):
    """Configuration for Neo4j connection."""
    database: str = "neo4j"
    batching: bool = True


class InclusionFlatteningConfig(BaseModel):
    """Configuration for flattening inclusion nodes."""
    description: str
    inclusion_node_label: str
    source_node_label: str
    target_node_label: str
    relationship_type: str
    relationship_property_mappings: Dict[str, str] = {}
    copy_target_properties: Dict[str, str] = {}


class Neo4jExportConfig(BaseModel):
    """Complete configuration for Neo4j export."""
    model_config = {"extra": "allow"}  # Allow extra fields like _notes

    rdf_source: RDFSourceConfig
    neo4j_connection: Neo4jConnectionConfig = Neo4jConnectionConfig()
    label_mapping: LabelMappingConfig
    uri_slug_extraction: Dict[str, str] = {}
    property_mappings: Dict[str, Dict[str, str]] = {}
    relationship_type_mappings: Dict[str, str] = {}
    reverse_relationships: Dict[str, str] = {}
    inclusion_flattening: List[InclusionFlatteningConfig] = []


# ============================================================================
# CONFIGURATION LOADER
# ============================================================================

class ExportConfig:
    """Manages configuration loading and environment variables."""

    def __init__(self, config_path: Path, env_path: Optional[Path] = None):
        """
        Load configuration from JSON file and environment.

        Args:
            config_path: Path to JSON configuration file
            env_path: Optional path to .env file
        """
        self.config_path = config_path
        self.env_path = env_path or config_path.parent.parent / ".env"

        # Load environment
        load_dotenv(self.env_path)

        # Load and validate config
        with open(config_path, 'r') as f:
            config_dict = json.load(f)

        self.config = Neo4jExportConfig(**config_dict)

        # Load Neo4j credentials from environment
        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.neo4j_database = os.getenv("NEO4J_DATABASE", self.config.neo4j_connection.database)

        if not self.neo4j_uri or not self.neo4j_password:
            raise ValueError("NEO4J_URI and NEO4J_PASSWORD must be set in .env file")

    def get_auth_data(self) -> Dict[str, str]:
        """Get Neo4j authentication data."""
        return {
            'uri': self.neo4j_uri,
            'database': self.neo4j_database,
            'user': self.neo4j_username,
            'pwd': self.neo4j_password
        }


# ============================================================================
# RDF LOADER
# ============================================================================

class RDFLoader:
    """Handles TTL file discovery, loading, and filtering."""

    def __init__(self, config: RDFSourceConfig, project_root: Path):
        """
        Initialize RDF loader.

        Args:
            config: RDF source configuration
            project_root: Project root directory
        """
        self.config = config
        self.project_root = project_root
        self.data_dir = project_root / config.file_discovery.base_dir

        # Create namespace objects for filtering
        self.OWL = Namespace("http://www.w3.org/2002/07/owl#")
        self.RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    def discover_files(self) -> List[Path]:
        """
        Discover TTL files based on configuration.

        Returns:
            List of paths to TTL files
        """
        ttl_files = []

        # Add explicitly listed files
        for file in self.config.file_discovery.include_files:
            file_path = self.data_dir / file
            if file_path.exists():
                ttl_files.append(file_path)

        # Add files matching patterns
        for pattern in self.config.file_discovery.include_patterns:
            # Handle patterns like "programmes/**/*.ttl"
            if "**" in pattern:
                base_path = pattern.split("**")[0].strip("/")
                glob_pattern = pattern.split("/", 1)[1] if "/" in pattern else "*.ttl"
                search_dir = self.data_dir / base_path if base_path else self.data_dir

                if search_dir.exists():
                    for ttl_file in search_dir.rglob(glob_pattern.replace("**/", "")):
                        # Check exclude patterns
                        if not self._is_excluded(ttl_file):
                            ttl_files.append(ttl_file)

        return ttl_files

    def _is_excluded(self, file_path: Path) -> bool:
        """Check if file matches any exclude patterns."""
        for pattern in self.config.file_discovery.exclude_patterns:
            # Handle patterns like "**/versions/**"
            # Extract the key directory name from the pattern
            pattern_clean = pattern.replace("**/", "").replace("/**", "")
            if pattern_clean in file_path.parts:
                return True
        return False

    def load_and_filter(self, ttl_file: Path) -> tuple[Graph, int, int]:
        """
        Load TTL file and filter out unwanted triples.

        Args:
            ttl_file: Path to TTL file

        Returns:
            Tuple of (filtered_graph, original_count, filtered_count)
        """
        # Parse TTL file
        graph = Graph()
        graph.parse(ttl_file, format="turtle")
        original_count = len(graph)

        # Filter based on config
        filtered_count = 0

        for subject_type in self.config.filters.exclude_subjects_by_type:
            # Convert namespace prefix to full URI
            if subject_type == "owl:Ontology":
                type_uri = self.OWL.Ontology
            else:
                # Handle other namespace prefixes if needed
                type_uri = URIRef(subject_type)

            # Find subjects of this type
            subjects_to_remove = set(graph.subjects(self.RDF.type, type_uri))

            # Remove all triples with these subjects
            for subject in subjects_to_remove:
                triples_to_remove = list(graph.triples((subject, None, None)))
                for triple in triples_to_remove:
                    graph.remove(triple)
                    filtered_count += 1

        return graph, original_count, filtered_count


# ============================================================================
# NEO4J CONNECTION
# ============================================================================

class Neo4jConnection:
    """Context manager for Neo4j RDF store connection (rdflib-neo4j only)."""

    def __init__(self, auth_data: Dict[str, str], custom_prefixes: Dict[str, str], config: Neo4jConnectionConfig):
        """
        Initialize Neo4j RDF store connection.

        Args:
            auth_data: Neo4j authentication dictionary
            custom_prefixes: RDF namespace prefixes
            config: Neo4j connection configuration
        """
        self.auth_data = auth_data
        self.custom_prefixes = custom_prefixes
        self.config = config
        self.store = None
        self.graph = None

    def __enter__(self):
        """Open Neo4j RDF store."""
        # Create rdflib-neo4j store
        store_config = Neo4jStoreConfig(
            auth_data=self.auth_data,
            custom_prefixes=self.custom_prefixes,
            handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.MAP,
            batching=self.config.batching
        )

        self.store = Neo4jStore(config=store_config)
        self.graph = Graph(store=self.store, identifier=self.auth_data['uri'])

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close Neo4j RDF store."""
        if self.store:
            self.store.close()

    def commit(self):
        """Commit RDF graph changes."""
        if self.graph:
            self.graph.commit()


# ============================================================================
# NEO4J TRANSFORMER
# ============================================================================

class Neo4jTransformer:
    """Executes post-import transformations on Neo4j graph."""

    def __init__(self, driver, database: str, config: Neo4jExportConfig):
        """
        Initialize transformer.

        Args:
            driver: Neo4j driver (native, not rdflib)
            database: Database name
            config: Export configuration
        """
        self.driver = driver
        self.database = database
        self.config = config
        self.main_label = config.label_mapping.target_label

    def _session(self):
        """Get a Neo4j session."""
        return self.driver.session(database=self.database)

    def apply_all_transformations(self):
        """Execute all configured transformations in order."""
        logger.info("\n" + "=" * 60)
        logger.info("Applying transformations...")
        logger.info("=" * 60)

        # Execute transformations in specific order
        self._apply_label_mapping()
        self._apply_slug_extraction()
        self._apply_property_mappings()
        self._apply_relationship_type_mappings()
        self._apply_reverse_relationships()
        self._apply_inclusion_flattening()
        self._apply_camelcase_conversion()

    def _apply_label_mapping(self):
        """Replace source labels with target labels."""
        if not self.config.label_mapping:
            return

        logger.info("\n" + "=" * 60)
        label_config = self.config.label_mapping
        source_label = label_config.source_label
        target_label = label_config.target_label
        uri_pattern = label_config.uri_pattern

        logger.info(f"Replacing {source_label} labels with {target_label} labels...")

        with self._session() as session:
            # Add target label and remove source label for matching URIs
            result = session.run(f"""
                MATCH (n:{source_label})
                WHERE n.uri STARTS WITH $uri_pattern
                SET n:{target_label}
                REMOVE n:{source_label}
                RETURN count(n) as count
            """, uri_pattern=uri_pattern)
            relabeled_count = result.single()["count"]
            logger.info(f"✓ Relabeled {relabeled_count} nodes ({source_label} → {target_label})")

            # Check remaining nodes with source label
            result = session.run(f"MATCH (n:{source_label}) RETURN count(n) as count")
            remaining = result.single()["count"]
            if remaining > 0:
                logger.info(f"  Note: {remaining} nodes kept {source_label} label (external URIs)")

    def _apply_slug_extraction(self):
        """Extract URI slugs as node properties."""
        if not self.config.uri_slug_extraction:
            return

        logger.info("\n" + "=" * 60)
        logger.info("Extracting URI slugs as properties...")

        total_slugs = 0
        with self._session() as session:
            for node_label, slug_property in self.config.uri_slug_extraction.items():
                result = session.run(f"""
                    MATCH (n:{node_label}:{self.main_label})
                    WHERE n.uri IS NOT NULL
                    WITH n, split(n.uri, '/') as uri_parts
                    SET n.{slug_property} = uri_parts[-1]
                    RETURN count(n) as count
                """)
                count = result.single()["count"]
                if count > 0:
                    logger.info(f"✓ {node_label}: Extracted slug to '{slug_property}' ({count} nodes)")
                    total_slugs += count

        if total_slugs > 0:
            logger.info(f"✓ Total slugs extracted: {total_slugs}")

    def _apply_property_mappings(self):
        """Rename properties based on configuration."""
        if not self.config.property_mappings:
            return

        logger.info("\n" + "=" * 60)
        logger.info("Applying custom property mappings...")

        total_renamed = 0
        with self._session() as session:
            for node_label, mappings in self.config.property_mappings.items():
                for old_prop, new_prop in mappings.items():
                    result = session.run(f"""
                        MATCH (n:{node_label}:{self.main_label})
                        WHERE n.{old_prop} IS NOT NULL
                        SET n.{new_prop} = n.{old_prop}
                        REMOVE n.{old_prop}
                        RETURN count(n) as count
                    """)
                    count = result.single()["count"]
                    if count > 0:
                        logger.info(f"✓ {node_label}: '{old_prop}' → '{new_prop}' ({count} nodes)")
                        total_renamed += count

        if total_renamed > 0:
            logger.info(f"✓ Total properties renamed: {total_renamed}")

    def _apply_relationship_type_mappings(self):
        """Rename relationship types based on configuration."""
        if not self.config.relationship_type_mappings:
            return

        logger.info("\n" + "=" * 60)
        logger.info("Renaming relationship types...")

        total_renamed = 0
        with self._session() as session:
            for old_type, new_type in self.config.relationship_type_mappings.items():
                result = session.run(f"""
                    MATCH (a)-[old:{old_type}]->(b)
                    CREATE (a)-[new:{new_type}]->(b)
                    SET new = properties(old)
                    WITH old, count(*) as count
                    DELETE old
                    RETURN count
                """)
                record = result.single()
                count = record["count"] if record else 0
                if count > 0:
                    logger.info(f"✓ '{old_type}' → '{new_type}' ({count} relationships)")
                    total_renamed += count

        if total_renamed > 0:
            logger.info(f"✓ Total relationships renamed: {total_renamed}")
        else:
            logger.info("  No relationship types to rename")

    def _apply_reverse_relationships(self):
        """Reverse relationship directions based on configuration."""
        if not self.config.reverse_relationships:
            return

        logger.info("\n" + "=" * 60)
        logger.info("Reversing relationships...")

        total_reversed = 0
        with self._session() as session:
            for old_type, new_type in self.config.reverse_relationships.items():
                result = session.run(f"""
                    MATCH (a)-[old:{old_type}]->(b)
                    CREATE (b)-[new:{new_type}]->(a)
                    SET new = properties(old)
                    WITH old, count(*) as count
                    DELETE old
                    RETURN count
                """)
                record = result.single()
                count = record["count"] if record else 0
                if count > 0:
                    logger.info(f"✓ Reversed '{old_type}' → '{new_type}' ({count} relationships)")
                    total_reversed += count

        if total_reversed > 0:
            logger.info(f"✓ Total relationships reversed: {total_reversed}")
        else:
            logger.info("  No relationships to reverse")

    def _apply_inclusion_flattening(self):
        """Flatten inclusion nodes into direct relationships."""
        if not self.config.inclusion_flattening:
            return

        logger.info("\n" + "=" * 60)
        logger.info("Flattening inclusion nodes into direct relationships...")

        total_flattened = 0
        with self._session() as session:
            for flatten_config in self.config.inclusion_flattening:
                inclusion_label = flatten_config.inclusion_node_label
                source_label = flatten_config.source_node_label
                target_label = flatten_config.target_node_label
                relationship_type = flatten_config.relationship_type
                property_mappings = flatten_config.relationship_property_mappings
                copy_target_properties = flatten_config.copy_target_properties

                logger.info(f"\n{flatten_config.description}")
                logger.info(f"  Pattern: ({source_label})-[]->({inclusion_label})-[]->({target_label})")
                logger.info(f"  New: ({source_label})-[{relationship_type}]->({target_label})")

                # Build property mapping SET clause
                property_set_clauses = []

                for old_prop, new_prop in property_mappings.items():
                    property_set_clauses.append(f"direct.{new_prop} = inclusion.{old_prop}")

                for old_prop, new_prop in copy_target_properties.items():
                    property_set_clauses.append(f"direct.{new_prop} = target.{old_prop}")

                set_clause = ", ".join(property_set_clauses) if property_set_clauses else ""

                # Execute flattening
                query = f"""
                    MATCH (source:{source_label}:{self.main_label})-[r1]->(inclusion:{inclusion_label}:{self.main_label})-[r2]->(target:{target_label}:{self.main_label})
                    CREATE (source)-[direct:{relationship_type}]->(target)
                    {('SET ' + set_clause) if set_clause else ''}
                    WITH inclusion, count(*) as rel_count
                    DETACH DELETE inclusion
                    RETURN rel_count as count
                """

                result = session.run(query)
                record = result.single()
                count = record["count"] if record else 0

                if count > 0:
                    logger.info(f"✓ Flattened {count} {inclusion_label} nodes")
                    if property_mappings:
                        for old_prop, new_prop in property_mappings.items():
                            logger.info(f"  Property: {old_prop} → {new_prop}")
                    total_flattened += count
                else:
                    logger.info(f"  No {inclusion_label} nodes found")

        if total_flattened > 0:
            logger.info(f"\n✓ Total inclusion nodes flattened: {total_flattened}")

    def _apply_camelcase_conversion(self):
        """Convert remaining camelCase relationship types to UPPER_CASE."""
        logger.info("\n" + "=" * 60)
        logger.info("Converting camelCase relationship types to Neo4j convention...")

        with self._session() as session:
            # Get all unique relationship types
            result = session.run("""
                MATCH ()-[r]->()
                RETURN DISTINCT type(r) as relType
                ORDER BY relType
            """)
            all_rel_types = [record["relType"] for record in result]

            # Get explicitly mapped types to skip
            explicit_mappings = self.config.relationship_type_mappings
            explicitly_set_types = set(explicit_mappings.values())

            total_renamed = 0
            for rel_type in all_rel_types:
                # Skip if already in UPPER_CASE format
                if rel_type == rel_type.upper() and '_' in rel_type or rel_type.isupper():
                    continue

                # Skip if explicitly set
                if rel_type in explicitly_set_types:
                    continue

                # Convert camelCase to UPPER_CASE
                new_type = camel_to_upper_snake(rel_type)

                result = session.run(f"""
                    MATCH (a)-[old:{rel_type}]->(b)
                    CREATE (a)-[new:{new_type}]->(b)
                    SET new = properties(old)
                    WITH old, count(*) as count
                    DELETE old
                    RETURN count
                """)
                record = result.single()
                count = record["count"] if record else 0

                if count > 0:
                    logger.info(f"✓ '{rel_type}' → '{new_type}' ({count} relationships)")
                    total_renamed += count

        if total_renamed > 0:
            logger.info(f"\n✓ Total relationships auto-converted: {total_renamed}")
        else:
            logger.info("  No camelCase relationships found to convert")

    def verify_export(self):
        """Verify the export and show statistics."""
        logger.info("\n" + "=" * 60)
        logger.info("Verifying export...")

        with self._session() as session:
            # Count total nodes
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            logger.info(f"✓ Total nodes in AuraDB: {node_count}")

            # Count by type label
            result = session.run(f"""
                MATCH (n:{self.main_label})
                WITH n, [label IN labels(n) WHERE label <> $main_label] as type_labels
                WITH CASE
                    WHEN size(type_labels) = 0 THEN '(no type)'
                    ELSE type_labels[0]
                END as type, count(*) as count
                RETURN type, count
                ORDER BY count DESC
            """, main_label=self.main_label)

            logger.info(f"\n{self.main_label} entity types:")
            for record in result:
                logger.info(f"  {record['type']}: {record['count']}")

            # Sample programmes
            logger.info("\nSample programmes:")
            result = session.run(f"""
                MATCH (p:Programme:{self.main_label})
                WHERE p.programmeTitle IS NOT NULL
                RETURN p.programmeTitle as title
                ORDER BY p.programmeTitle
                LIMIT 5
            """)
            for record in result:
                logger.info(f"  • {record['title']}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def camel_to_upper_snake(name: str) -> str:
    """
    Convert camelCase to UPPER_CASE_WITH_UNDERSCORES.

    Examples:
        hasYearGroup -> HAS_YEAR_GROUP
        isPartOf -> IS_PART_OF
        includesUnitVariantChoice -> INCLUDES_UNIT_VARIANT_CHOICE
    """
    # Insert underscore before uppercase letters (except at start)
    result = re.sub('(?<!^)(?=[A-Z])', '_', name)
    # Convert to uppercase
    return result.upper()


def clear_neo4j_data(auth_data: Dict[str, str], label: str):
    """
    Clear all nodes with specified label from Neo4j.

    Args:
        auth_data: Neo4j authentication data
        label: Label of nodes to delete
    """
    logger.info("\n" + "=" * 60)
    logger.info(f"⚠️  Clearing {label} data (--clear flag set)...")

    driver = GraphDatabase.driver(auth_data['uri'], auth=(auth_data['user'], auth_data['pwd']))

    try:
        with driver.session(database=auth_data['database']) as session:
            # Count nodes before clearing
            result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            label_count = result.single()["count"]

            if label_count > 0:
                logger.info(f"Deleting {label_count} existing {label} nodes...")
                session.run(f"MATCH (n:{label}) DETACH DELETE n")
                logger.info(f"✓ {label} data cleared!")
            else:
                logger.info(f"No existing {label} nodes to delete")

            # Show remaining nodes
            result = session.run("MATCH (n) RETURN count(n) as count")
            remaining_count = result.single()["count"]
            if remaining_count > 0:
                logger.info(f"  (Database still contains {remaining_count} nodes from other sources)")
    finally:
        driver.close()

    logger.info("-" * 60)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Export Oak Curriculum Ontology to Neo4j AuraDB."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Export Oak Curriculum Ontology to Neo4j AuraDB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export data (append to existing)
  python scripts/export_to_neo4j.py

  # Clear database first, then export
  python scripts/export_to_neo4j.py --clear
        """
    )
    parser.add_argument('--clear', action='store_true',
                        help='Clear all data from Neo4j database before import')
    args = parser.parse_args()

    try:
        # Load configuration
        project_root = Path(__file__).parent.parent
        config_path = project_root / "scripts" / "neo4j_export_config.json"

        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)

        logger.info("=" * 60)
        logger.info("Oak Curriculum Ontology → Neo4j AuraDB Export")
        logger.info("=" * 60)

        # Load and validate configuration
        export_config = ExportConfig(config_path)
        logger.info(f"✓ Configuration loaded and validated")
        logger.info(f"Target: {export_config.neo4j_uri}")
        logger.info(f"Database: {export_config.neo4j_database}")
        logger.info("-" * 60)

        # Clear data if requested
        if args.clear:
            clear_neo4j_data(
                export_config.get_auth_data(),
                export_config.config.label_mapping.target_label
            )

        # Discover TTL files
        rdf_loader = RDFLoader(export_config.config.rdf_source, project_root)
        ttl_files = rdf_loader.discover_files()

        logger.info(f"Found {len(ttl_files)} TTL files to export:")
        for f in ttl_files:
            logger.info(f"  - {f.relative_to(project_root)}")

        # Connect to Neo4j and load data (don't use context manager - keep store open)
        logger.info("\n" + "=" * 60)
        logger.info("Connecting to AuraDB...")

        # Create store config
        store_config = Neo4jStoreConfig(
            auth_data=export_config.get_auth_data(),
            custom_prefixes=export_config.config.rdf_source.namespaces,
            handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.MAP,
            batching=export_config.config.neo4j_connection.batching
        )

        # Create store and graph (like original)
        neo4j_store = Neo4jStore(config=store_config)
        neo4j_graph = Graph(store=neo4j_store, identifier=export_config.neo4j_uri)

        logger.info("✓ Connected to AuraDB!")

        # Load each TTL file
        total_triples = 0
        total_filtered = 0

        logger.info("\n" + "=" * 60)
        for ttl_file in ttl_files:
            logger.info(f"\nExporting: {ttl_file.name}")
            logger.info("-" * 40)

            try:
                # Load and filter
                filtered_graph, original_count, filtered_count = rdf_loader.load_and_filter(ttl_file)

                # Add to Neo4j
                for triple in filtered_graph:
                    neo4j_graph.add(triple)

                file_triple_count = len(filtered_graph)
                total_triples += file_triple_count
                total_filtered += filtered_count

                if filtered_count > 0:
                    logger.info(f"✓ Added {file_triple_count} triples (filtered {filtered_count} ontology triples)")
                else:
                    logger.info(f"✓ Added {file_triple_count} triples")
                logger.info(f"  Running total: {total_triples} triples")

            except Exception as e:
                logger.error(f"✗ Failed to export {ttl_file.name}: {e}")
                continue

        # Commit to Neo4j
        logger.info("\n" + "=" * 60)
        logger.info("Committing to AuraDB...")
        neo4j_graph.commit()
        logger.info(f"✓ Successfully exported {total_triples} triples to Neo4j!")
        if total_filtered > 0:
            logger.info(f"  (Filtered out {total_filtered} ontology declaration triples)")

        # Create separate driver for transformations (like original version)
        # IMPORTANT: Store stays open!
        driver = GraphDatabase.driver(
            export_config.neo4j_uri,
            auth=(export_config.neo4j_username, export_config.neo4j_password)
        )

        try:
            # Apply transformations
            transformer = Neo4jTransformer(driver, export_config.neo4j_database, export_config.config)
            transformer.apply_all_transformations()

            # Verify export
            transformer.verify_export()

        finally:
            driver.close()
            neo4j_store.close()  # Close store at the very end, like original

        logger.info("\n" + "=" * 60)
        logger.info("✅ EXPORT COMPLETE!")
        logger.info("\nNext steps:")
        logger.info("1. Open Neo4j Browser in Aura Console")
        logger.info("2. Run: MATCH (n) RETURN labels(n), count(n)")
        logger.info("3. Explore your Oak Curriculum data!")

    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
