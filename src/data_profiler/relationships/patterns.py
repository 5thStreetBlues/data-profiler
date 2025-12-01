"""Naming convention patterns for FK detection.

This module provides pattern matching for identifying foreign key
columns based on common naming conventions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class NamingPatterns:
    """Naming convention patterns for FK detection.

    Attributes:
        fk_suffixes: Suffixes that indicate a foreign key column (e.g., "_id", "_code").
        fk_prefixes: Prefixes that indicate a foreign key column (e.g., "fk_").
        pk_names: Common primary key column names (e.g., "id", "pk").
        match_by_name: Whether to match by column name similarity.
        case_sensitive: Whether pattern matching is case-sensitive.
    """

    fk_suffixes: list[str] = field(
        default_factory=lambda: ["_id", "_code", "_key", "_fk", "_ref"]
    )
    fk_prefixes: list[str] = field(default_factory=lambda: ["fk_", "ref_"])
    pk_names: list[str] = field(
        default_factory=lambda: ["id", "pk", "key", "code"]
    )
    match_by_name: bool = True
    case_sensitive: bool = False

    def is_potential_fk(self, column_name: str) -> bool:
        """Check if a column name looks like a foreign key.

        Args:
            column_name: Name of the column to check.

        Returns:
            True if the column name matches FK naming patterns.
        """
        name = column_name if self.case_sensitive else column_name.lower()

        # Check suffixes
        for suffix in self.fk_suffixes:
            suffix_check = suffix if self.case_sensitive else suffix.lower()
            if name.endswith(suffix_check) and name != suffix_check:
                return True

        # Check prefixes
        for prefix in self.fk_prefixes:
            prefix_check = prefix if self.case_sensitive else prefix.lower()
            if name.startswith(prefix_check) and name != prefix_check:
                return True

        return False

    def is_potential_pk(self, column_name: str) -> bool:
        """Check if a column name looks like a primary key.

        Args:
            column_name: Name of the column to check.

        Returns:
            True if the column name matches PK naming patterns.
        """
        name = column_name if self.case_sensitive else column_name.lower()

        for pk_name in self.pk_names:
            pk_check = pk_name if self.case_sensitive else pk_name.lower()
            if name == pk_check:
                return True

        return False

    def extract_entity_name(self, column_name: str) -> str | None:
        """Extract the entity name from a FK column name.

        For example, "customer_id" -> "customer", "order_code" -> "order".

        Args:
            column_name: Name of the FK column.

        Returns:
            Extracted entity name, or None if not extractable.
        """
        name = column_name if self.case_sensitive else column_name.lower()

        # Try suffixes
        for suffix in self.fk_suffixes:
            suffix_check = suffix if self.case_sensitive else suffix.lower()
            if name.endswith(suffix_check) and len(name) > len(suffix_check):
                return name[: -len(suffix_check)]

        # Try prefixes
        for prefix in self.fk_prefixes:
            prefix_check = prefix if self.case_sensitive else prefix.lower()
            if name.startswith(prefix_check) and len(name) > len(prefix_check):
                return name[len(prefix_check) :]

        return None

    def find_matching_pk_column(
        self, fk_column: str, candidate_columns: list[str]
    ) -> str | None:
        """Find a matching PK column for a FK column.

        Uses naming conventions to find potential matches.

        Args:
            fk_column: Name of the foreign key column.
            candidate_columns: List of potential PK columns to match against.

        Returns:
            Name of the matching PK column, or None if no match found.
        """
        if not self.match_by_name:
            return None

        # Extract entity name from FK
        entity_name = self.extract_entity_name(fk_column)

        for col in candidate_columns:
            col_check = col if self.case_sensitive else col.lower()

            # Direct match (e.g., fk "customer_id" matches pk "customer_id")
            fk_check = fk_column if self.case_sensitive else fk_column.lower()
            if col_check == fk_check:
                return col

            # PK name match (e.g., fk "customer_id" matches pk "id")
            if self.is_potential_pk(col):
                return col

            # Entity name match (e.g., fk "customer_id" matches pk "customer")
            if entity_name and col_check == entity_name:
                return col

            # Entity + pk suffix match (e.g., fk "customer_id" matches pk "customer_key")
            if entity_name:
                for pk_name in self.pk_names:
                    pk_check = pk_name if self.case_sensitive else pk_name.lower()
                    if col_check == f"{entity_name}_{pk_check}":
                        return col

        return None

    def match_file_to_entity(
        self, fk_column: str, file_paths: list[Path]
    ) -> Path | None:
        """Find a file that might contain the parent entity for a FK.

        Uses naming conventions to match FK column names to file names.

        Args:
            fk_column: Name of the foreign key column.
            file_paths: List of file paths to search.

        Returns:
            Path to the matching file, or None if no match found.
        """
        entity_name = self.extract_entity_name(fk_column)
        if not entity_name:
            return None

        for file_path in file_paths:
            file_stem = file_path.stem
            stem_check = file_stem if self.case_sensitive else file_stem.lower()
            entity_check = entity_name if self.case_sensitive else entity_name.lower()

            # Direct match (e.g., "customer_id" -> "customer.parquet")
            if stem_check == entity_check:
                return file_path

            # Plural match (e.g., "customer_id" -> "customers.parquet")
            if stem_check == f"{entity_check}s":
                return file_path

            # Singular match (e.g., "customers_id" -> "customer.parquet")
            if entity_check.endswith("s") and stem_check == entity_check[:-1]:
                return file_path

        return None

    def get_fk_candidates(self, columns: list[str]) -> list[str]:
        """Get all columns that look like foreign keys.

        Args:
            columns: List of column names to check.

        Returns:
            List of column names that match FK patterns.
        """
        return [col for col in columns if self.is_potential_fk(col)]

    def get_pk_candidates(self, columns: list[str]) -> list[str]:
        """Get all columns that look like primary keys.

        Args:
            columns: List of column names to check.

        Returns:
            List of column names that match PK patterns.
        """
        # PK candidates include explicit PK names and columns with _id suffix
        # that don't reference another entity
        candidates = []
        for col in columns:
            if self.is_potential_pk(col):
                candidates.append(col)
            elif self.is_potential_fk(col):
                # Check if this might be a composite PK
                entity_name = self.extract_entity_name(col)
                if entity_name:
                    # Columns like "order_id" in an "orders" table are PKs
                    candidates.append(col)

        return candidates

    @classmethod
    def from_config(cls, config: dict) -> "NamingPatterns":
        """Create NamingPatterns from configuration dictionary.

        Args:
            config: Configuration dictionary with pattern settings.

        Returns:
            Configured NamingPatterns instance.
        """
        return cls(
            fk_suffixes=config.get("fk_suffixes", cls().fk_suffixes),
            fk_prefixes=config.get("fk_prefixes", cls().fk_prefixes),
            pk_names=config.get("pk_names", cls().pk_names),
            match_by_name=config.get("match_by_name", True),
            case_sensitive=config.get("case_sensitive", False),
        )
