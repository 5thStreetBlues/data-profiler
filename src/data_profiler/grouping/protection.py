"""Cardinality protection for grouping operations.

This module provides functionality to protect against high-cardinality
grouping operations that could cause performance or memory issues.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from data_profiler.readers.backend import is_polars_backend


class CardinalityAction(str, Enum):
    """Action to take when cardinality exceeds threshold.

    Attributes:
        WARN: Issue a warning but continue processing.
        SKIP: Skip the grouping operation entirely.
        SAMPLE: Sample the data to reduce cardinality.
        LIMIT: Limit results to top N groups.
    """

    WARN = "warn"
    SKIP = "skip"
    SAMPLE = "sample"
    LIMIT = "limit"


@dataclass
class CardinalityResult:
    """Result of cardinality check.

    Attributes:
        cardinality: Actual number of unique groups.
        threshold: Configured threshold.
        exceeded: Whether threshold was exceeded.
        action: Recommended action to take.
        message: Human-readable message.
    """

    cardinality: int
    threshold: int
    exceeded: bool
    action: CardinalityAction
    message: str | None = None

    @property
    def should_proceed(self) -> bool:
        """Check if operation should proceed.

        Returns:
            True if operation should continue, False if it should be skipped.
        """
        return not self.exceeded or self.action != CardinalityAction.SKIP


@dataclass
class ProtectionConfig:
    """Configuration for cardinality protection.

    Attributes:
        threshold: Maximum number of groups before taking action.
        action: Action to take when threshold exceeded.
        warn_threshold: Threshold for warning (before skip threshold).
        sample_rate: Sample rate to use if action is SAMPLE.
        limit_count: Number of groups to keep if action is LIMIT.
    """

    threshold: int = 100
    action: CardinalityAction = CardinalityAction.SKIP
    warn_threshold: int | None = None
    sample_rate: float = 0.1
    limit_count: int = 10

    def __post_init__(self) -> None:
        """Set default warn threshold if not specified."""
        if self.warn_threshold is None:
            self.warn_threshold = int(self.threshold * 0.8)


class CardinalityProtection:
    """Protects against high-cardinality grouping operations.

    Checks the cardinality of grouping columns before performing
    expensive group-by operations, and takes appropriate action
    when thresholds are exceeded.

    Example:
        >>> protection = CardinalityProtection(threshold=100)
        >>> result = protection.check(df, by=["user_id"])
        >>> if not result.should_proceed:
        ...     print(f"Skipping: {result.message}")
    """

    def __init__(self, config: ProtectionConfig | None = None) -> None:
        """Initialize cardinality protection.

        Args:
            config: Optional configuration. Defaults to ProtectionConfig().
        """
        self.config = config or ProtectionConfig()

    def check(
        self,
        df: Any,
        by: list[str],
        threshold: int | None = None,
    ) -> CardinalityResult:
        """Check cardinality of grouping columns.

        Args:
            df: DataFrame to check.
            by: Columns to group by.
            threshold: Override config threshold.

        Returns:
            CardinalityResult with check results.
        """
        actual_threshold = threshold if threshold is not None else self.config.threshold

        # Get actual cardinality
        cardinality = self._count_unique(df, by)

        # Determine if exceeded and what action to take
        exceeded = cardinality > actual_threshold

        if exceeded:
            action = self.config.action
            message = (
                f"Cardinality ({cardinality:,}) exceeds threshold ({actual_threshold:,}). "
                f"Action: {action.value}"
            )
        elif self.config.warn_threshold and cardinality > self.config.warn_threshold:
            action = CardinalityAction.WARN
            message = (
                f"Cardinality ({cardinality:,}) approaching threshold ({actual_threshold:,})"
            )
            exceeded = False  # Not actually exceeded, just warning
        else:
            action = CardinalityAction.WARN  # Default, but won't be used
            message = None

        return CardinalityResult(
            cardinality=cardinality,
            threshold=actual_threshold,
            exceeded=exceeded,
            action=action if exceeded else CardinalityAction.WARN,
            message=message,
        )

    def _count_unique(self, df: Any, columns: list[str]) -> int:
        """Count unique combinations of columns.

        Args:
            df: DataFrame.
            columns: Columns to check.

        Returns:
            Number of unique combinations.
        """
        # Check DataFrame type directly instead of backend setting
        df_type = type(df).__module__
        if df_type.startswith("polars"):
            return df.select(columns).n_unique()
        else:
            return df[columns].drop_duplicates().shape[0]

    def apply_protection(
        self,
        df: Any,
        by: list[str],
        result: CardinalityResult,
    ) -> tuple[Any, bool]:
        """Apply protection action to DataFrame if needed.

        Args:
            df: DataFrame to potentially modify.
            by: Grouping columns.
            result: CardinalityResult from check().

        Returns:
            Tuple of (modified_df, was_modified).
        """
        if not result.exceeded:
            return df, False

        if result.action == CardinalityAction.SKIP:
            return df, False  # Return original, caller should skip

        if result.action == CardinalityAction.SAMPLE:
            return self._apply_sampling(df), True

        if result.action == CardinalityAction.LIMIT:
            return df, False  # Limiting happens after grouping

        # WARN action - no modification
        return df, False

    def _apply_sampling(self, df: Any) -> Any:
        """Apply sampling to reduce data size.

        Args:
            df: DataFrame to sample.

        Returns:
            Sampled DataFrame.
        """
        # Check DataFrame type directly instead of backend setting
        df_type = type(df).__module__
        if df_type.startswith("polars"):
            return df.sample(fraction=self.config.sample_rate)
        else:
            return df.sample(frac=self.config.sample_rate)

    def limit_results(
        self,
        groups: list[Any],
        result: CardinalityResult,
    ) -> list[Any]:
        """Limit results to top N groups if action is LIMIT.

        Args:
            groups: List of group results.
            result: CardinalityResult from check().

        Returns:
            Potentially limited list of groups.
        """
        if result.action == CardinalityAction.LIMIT:
            return groups[: self.config.limit_count]
        return groups


def estimate_cardinality(
    df: Any,
    columns: list[str],
    sample_size: int = 10000,
) -> int:
    """Estimate cardinality using sampling for large datasets.

    Args:
        df: DataFrame.
        columns: Columns to check.
        sample_size: Number of rows to sample.

    Returns:
        Estimated cardinality.
    """
    # Check DataFrame type directly instead of backend setting
    df_type = type(df).__module__
    if df_type.startswith("polars"):
        total_rows = df.height
        if total_rows <= sample_size:
            return df.select(columns).n_unique()

        # Sample and extrapolate
        sample_df = df.sample(n=min(sample_size, total_rows))
        sample_unique = sample_df.select(columns).n_unique()

        # Simple linear extrapolation (conservative estimate)
        return int(sample_unique * (total_rows / sample_size))
    else:
        total_rows = len(df)
        if total_rows <= sample_size:
            return df[columns].drop_duplicates().shape[0]

        # Sample and extrapolate
        sample_df = df.sample(n=min(sample_size, total_rows))
        sample_unique = sample_df[columns].drop_duplicates().shape[0]

        return int(sample_unique * (total_rows / sample_size))


def format_cardinality_warning(
    cardinality: int,
    threshold: int,
    columns: list[str],
) -> str:
    """Format a human-readable cardinality warning message.

    Args:
        cardinality: Actual cardinality.
        threshold: Configured threshold.
        columns: Grouping columns.

    Returns:
        Formatted warning message.
    """
    columns_str = ", ".join(columns)
    return (
        f"High cardinality warning: grouping by [{columns_str}] "
        f"produces {cardinality:,} unique groups, "
        f"exceeding the threshold of {threshold:,}. "
        f"Consider increasing --max-groups or using --sample."
    )
