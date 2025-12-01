"""Unit tests for cardinality protection module."""

from __future__ import annotations

from typing import Any

import pytest

from data_profiler.grouping.protection import (
    CardinalityAction,
    CardinalityProtection,
    CardinalityResult,
    ProtectionConfig,
    estimate_cardinality,
    format_cardinality_warning,
)


class TestProtectionConfig:
    """Tests for ProtectionConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ProtectionConfig()

        assert config.threshold == 100
        assert config.action == CardinalityAction.SKIP
        assert config.warn_threshold == 80  # 80% of 100
        assert config.sample_rate == 0.1
        assert config.limit_count == 10

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = ProtectionConfig(
            threshold=500,
            action=CardinalityAction.WARN,
            warn_threshold=400,
            sample_rate=0.2,
            limit_count=20,
        )

        assert config.threshold == 500
        assert config.action == CardinalityAction.WARN
        assert config.warn_threshold == 400
        assert config.sample_rate == 0.2
        assert config.limit_count == 20

    def test_auto_warn_threshold(self) -> None:
        """Test automatic warn threshold calculation."""
        config = ProtectionConfig(threshold=200, warn_threshold=None)

        assert config.warn_threshold == 160  # 80% of 200


class TestCardinalityResult:
    """Tests for CardinalityResult dataclass."""

    def test_should_proceed_not_exceeded(self) -> None:
        """Test should_proceed when threshold not exceeded."""
        result = CardinalityResult(
            cardinality=50,
            threshold=100,
            exceeded=False,
            action=CardinalityAction.WARN,
        )

        assert result.should_proceed is True

    def test_should_proceed_exceeded_skip(self) -> None:
        """Test should_proceed when threshold exceeded with SKIP action."""
        result = CardinalityResult(
            cardinality=150,
            threshold=100,
            exceeded=True,
            action=CardinalityAction.SKIP,
        )

        assert result.should_proceed is False

    def test_should_proceed_exceeded_warn(self) -> None:
        """Test should_proceed when threshold exceeded with WARN action."""
        result = CardinalityResult(
            cardinality=150,
            threshold=100,
            exceeded=True,
            action=CardinalityAction.WARN,
        )

        assert result.should_proceed is True


class TestCardinalityProtectionPolars:
    """Tests for CardinalityProtection with Polars backend."""

    @pytest.fixture
    def low_cardinality_df(self) -> Any:
        """Create DataFrame with low cardinality."""
        try:
            import polars as pl

            return pl.DataFrame({
                "category": ["A", "B", "C", "A", "B", "C"] * 100,
                "value": list(range(600)),
            })
        except ImportError:
            pytest.skip("Polars not available")

    @pytest.fixture
    def high_cardinality_df(self) -> Any:
        """Create DataFrame with high cardinality."""
        try:
            import polars as pl

            return pl.DataFrame({
                "user_id": list(range(1000)),
                "value": list(range(1000)),
            })
        except ImportError:
            pytest.skip("Polars not available")

    @pytest.fixture
    def protection(self) -> CardinalityProtection:
        """Create default cardinality protection."""
        return CardinalityProtection()

    def test_check_below_threshold(
        self,
        protection: CardinalityProtection,
        low_cardinality_df: Any,
    ) -> None:
        """Test check when cardinality is below threshold."""
        result = protection.check(low_cardinality_df, by=["category"])

        assert result.cardinality == 3
        assert result.exceeded is False
        assert result.should_proceed is True

    def test_check_above_threshold(
        self,
        protection: CardinalityProtection,
        high_cardinality_df: Any,
    ) -> None:
        """Test check when cardinality exceeds threshold."""
        result = protection.check(high_cardinality_df, by=["user_id"])

        assert result.cardinality == 1000
        assert result.exceeded is True
        assert result.action == CardinalityAction.SKIP
        assert "exceeds" in result.message

    def test_check_with_custom_threshold(
        self,
        protection: CardinalityProtection,
        high_cardinality_df: Any,
    ) -> None:
        """Test check with custom threshold override."""
        result = protection.check(
            high_cardinality_df,
            by=["user_id"],
            threshold=2000,
        )

        assert result.cardinality == 1000
        assert result.exceeded is False

    def test_check_warn_threshold(self, low_cardinality_df: Any) -> None:
        """Test warning when approaching threshold."""
        config = ProtectionConfig(threshold=5, warn_threshold=2)
        protection = CardinalityProtection(config)

        result = protection.check(low_cardinality_df, by=["category"])

        # 3 unique values, above warn_threshold (2) but below threshold (5)
        assert result.exceeded is False
        assert "approaching" in result.message

    def test_apply_protection_skip(
        self,
        protection: CardinalityProtection,
        high_cardinality_df: Any,
    ) -> None:
        """Test apply_protection with SKIP action."""
        result = protection.check(high_cardinality_df, by=["user_id"])

        modified_df, was_modified = protection.apply_protection(
            high_cardinality_df,
            by=["user_id"],
            result=result,
        )

        # SKIP doesn't modify the DataFrame
        assert was_modified is False

    def test_apply_protection_sample(self, high_cardinality_df: Any) -> None:
        """Test apply_protection with SAMPLE action."""
        config = ProtectionConfig(
            threshold=100,
            action=CardinalityAction.SAMPLE,
            sample_rate=0.1,
        )
        protection = CardinalityProtection(config)

        result = protection.check(high_cardinality_df, by=["user_id"])
        modified_df, was_modified = protection.apply_protection(
            high_cardinality_df,
            by=["user_id"],
            result=result,
        )

        assert was_modified is True
        # Sampled DataFrame should be smaller
        assert modified_df.height < high_cardinality_df.height

    def test_limit_results(self, protection: CardinalityProtection) -> None:
        """Test limiting results to top N groups."""
        groups = list(range(100))  # Simulate 100 groups

        # Create result with LIMIT action
        result = CardinalityResult(
            cardinality=100,
            threshold=50,
            exceeded=True,
            action=CardinalityAction.LIMIT,
        )

        limited = protection.limit_results(groups, result)

        assert len(limited) == 10  # Default limit_count


class TestCardinalityProtectionPandas:
    """Tests for CardinalityProtection with Pandas backend."""

    @pytest.fixture
    def sample_df(self) -> Any:
        """Create sample Pandas DataFrame."""
        import pandas as pd

        return pd.DataFrame({
            "category": ["A", "B", "C"] * 100,
            "value": list(range(300)),
        })

    @pytest.fixture
    def protection(self) -> CardinalityProtection:
        """Create default protection with pandas backend."""
        from data_profiler.readers.backend import set_backend
        set_backend("pandas")
        return CardinalityProtection()

    def test_check_pandas(
        self,
        protection: CardinalityProtection,
        sample_df: Any,
    ) -> None:
        """Test check with Pandas backend."""
        result = protection.check(sample_df, by=["category"])

        assert result.cardinality == 3
        assert result.exceeded is False


class TestEstimateCardinality:
    """Tests for estimate_cardinality function."""

    def test_estimate_small_dataset(self) -> None:
        """Test estimation on small dataset (returns exact count)."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "B", "C", "A", "B"],
            })

            estimate = estimate_cardinality(df, ["category"])
            assert estimate == 3

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "category": ["A", "B", "C", "A", "B"],
            })

            estimate = estimate_cardinality(df, ["category"])
            assert estimate == 3


class TestFormatCardinalityWarning:
    """Tests for format_cardinality_warning function."""

    def test_format_warning_single_column(self) -> None:
        """Test formatting warning for single column."""
        warning = format_cardinality_warning(
            cardinality=500,
            threshold=100,
            columns=["user_id"],
        )

        assert "user_id" in warning
        assert "500" in warning
        assert "100" in warning

    def test_format_warning_multiple_columns(self) -> None:
        """Test formatting warning for multiple columns."""
        warning = format_cardinality_warning(
            cardinality=1000,
            threshold=50,
            columns=["country", "city"],
        )

        assert "country, city" in warning
        assert "1,000" in warning
        assert "50" in warning
