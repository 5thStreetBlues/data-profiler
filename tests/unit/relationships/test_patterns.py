"""Tests for naming convention patterns."""

from pathlib import Path

import pytest

from data_profiler.relationships.patterns import NamingPatterns


class TestNamingPatterns:
    """Tests for NamingPatterns class."""

    def test_is_potential_fk_with_suffix(self) -> None:
        """Test FK detection via suffix."""
        patterns = NamingPatterns()

        # Should be detected as FK
        assert patterns.is_potential_fk("customer_id") is True
        assert patterns.is_potential_fk("order_code") is True
        assert patterns.is_potential_fk("product_key") is True
        assert patterns.is_potential_fk("user_fk") is True
        assert patterns.is_potential_fk("account_ref") is True

        # Should not be detected as FK
        assert patterns.is_potential_fk("name") is False
        assert patterns.is_potential_fk("description") is False
        assert patterns.is_potential_fk("_id") is False  # Just the suffix

    def test_is_potential_fk_with_prefix(self) -> None:
        """Test FK detection via prefix."""
        patterns = NamingPatterns()

        assert patterns.is_potential_fk("fk_customer") is True
        assert patterns.is_potential_fk("ref_order") is True

    def test_is_potential_fk_case_insensitive(self) -> None:
        """Test FK detection is case insensitive by default."""
        patterns = NamingPatterns()

        assert patterns.is_potential_fk("Customer_ID") is True
        assert patterns.is_potential_fk("CUSTOMER_ID") is True
        assert patterns.is_potential_fk("customer_Id") is True

    def test_is_potential_fk_case_sensitive(self) -> None:
        """Test FK detection with case sensitivity enabled."""
        patterns = NamingPatterns(case_sensitive=True)

        assert patterns.is_potential_fk("customer_id") is True
        assert patterns.is_potential_fk("Customer_ID") is False  # No match

    def test_is_potential_pk(self) -> None:
        """Test PK detection."""
        patterns = NamingPatterns()

        assert patterns.is_potential_pk("id") is True
        assert patterns.is_potential_pk("pk") is True
        assert patterns.is_potential_pk("key") is True
        assert patterns.is_potential_pk("code") is True

        assert patterns.is_potential_pk("name") is False
        assert patterns.is_potential_pk("customer_id") is False

    def test_extract_entity_name(self) -> None:
        """Test entity name extraction from FK column names."""
        patterns = NamingPatterns()

        assert patterns.extract_entity_name("customer_id") == "customer"
        assert patterns.extract_entity_name("order_code") == "order"
        assert patterns.extract_entity_name("product_key") == "product"
        assert patterns.extract_entity_name("fk_user") == "user"

        assert patterns.extract_entity_name("name") is None
        assert patterns.extract_entity_name("_id") is None

    def test_find_matching_pk_column(self) -> None:
        """Test finding matching PK column for a FK."""
        patterns = NamingPatterns()

        candidates = ["id", "name", "email", "customer"]

        # customer_id should match "id" (generic PK)
        assert patterns.find_matching_pk_column("customer_id", candidates) == "id"

        # With the entity name available
        candidates2 = ["customer", "name", "email"]
        assert patterns.find_matching_pk_column("customer_id", candidates2) == "customer"

        # Direct match
        candidates3 = ["customer_id", "name", "email"]
        assert patterns.find_matching_pk_column("customer_id", candidates3) == "customer_id"

    def test_match_file_to_entity(self) -> None:
        """Test matching FK column to parent file."""
        patterns = NamingPatterns()

        files = [
            Path("customers.parquet"),
            Path("orders.parquet"),
            Path("products.csv"),
        ]

        # Direct singular match
        assert patterns.match_file_to_entity("customer_id", files) == Path("customers.parquet")

        # No match
        assert patterns.match_file_to_entity("user_id", files) is None

    def test_get_fk_candidates(self) -> None:
        """Test getting all FK candidate columns."""
        patterns = NamingPatterns()

        columns = ["id", "customer_id", "name", "order_code", "email", "product_key"]
        fk_candidates = patterns.get_fk_candidates(columns)

        assert set(fk_candidates) == {"customer_id", "order_code", "product_key"}

    def test_get_pk_candidates(self) -> None:
        """Test getting all PK candidate columns."""
        patterns = NamingPatterns()

        columns = ["id", "customer_id", "name", "pk", "code"]
        pk_candidates = patterns.get_pk_candidates(columns)

        # Both explicit PKs and FK-style columns are candidates
        assert "id" in pk_candidates
        assert "pk" in pk_candidates
        assert "code" in pk_candidates
        assert "customer_id" in pk_candidates  # Could be PK in customers table

    def test_from_config(self) -> None:
        """Test creating patterns from config dict."""
        config = {
            "fk_suffixes": ["_ref"],
            "match_by_name": False,
        }

        patterns = NamingPatterns.from_config(config)

        assert patterns.fk_suffixes == ["_ref"]
        assert patterns.match_by_name is False
        # Defaults preserved for non-specified values
        assert patterns.case_sensitive is False

    def test_custom_suffixes(self) -> None:
        """Test with custom FK suffixes."""
        patterns = NamingPatterns(fk_suffixes=["_fkey", "_reference"])

        assert patterns.is_potential_fk("customer_fkey") is True
        assert patterns.is_potential_fk("order_reference") is True
        assert patterns.is_potential_fk("customer_id") is False  # Not in custom list
