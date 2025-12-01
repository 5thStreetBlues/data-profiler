"""Grouping data models.

This module defines data structures for grouped row count operations,
including statistics levels and result containers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from data_profiler.models.profile import FileProfile


class StatsLevel(str, Enum):
    """Statistics level for grouped analysis.

    Attributes:
        COUNT: Row count only (default).
        BASIC: Row count + min, max, mean of numeric columns.
        FULL: Full column profile per group.
    """

    COUNT = "count"
    BASIC = "basic"
    FULL = "full"


@dataclass
class GroupStats:
    """Statistics for a single group.

    Attributes:
        key: Group key values (e.g., {"make": "Toyota", "model": "Camry"}).
        row_count: Number of rows in this group.
        basic_stats: Min, max, mean per numeric column (if stats_level >= basic).
        full_profile: Full column profile (if stats_level == full).
    """

    key: dict[str, Any]
    row_count: int
    basic_stats: dict[str, dict[str, float]] | None = None
    full_profile: "FileProfile | None" = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with group statistics.
        """
        result: dict[str, Any] = {
            "key": self.key,
            "row_count": self.row_count,
        }
        if self.basic_stats is not None:
            result["basic_stats"] = self.basic_stats
        if self.full_profile is not None:
            result["full_profile"] = self.full_profile.to_dict()
        return result


@dataclass
class GroupingResult:
    """Result of a grouped row count operation.

    Attributes:
        columns: Columns used for grouping.
        stats_level: Statistics level used ("count", "basic", or "full").
        groups: Statistics per group.
        skipped: True if exceeded max_groups threshold.
        warning: Warning message if skipped.
        total_rows: Total rows across all groups.
        group_count: Number of distinct groups.
    """

    columns: list[str]
    stats_level: StatsLevel
    groups: list[GroupStats] = field(default_factory=list)
    skipped: bool = False
    warning: str | None = None
    total_rows: int = 0
    group_count: int = 0

    def add_group(self, stats: GroupStats) -> None:
        """Add a group to the result.

        Args:
            stats: GroupStats to add.
        """
        self.groups.append(stats)
        self.total_rows += stats.row_count
        self.group_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with grouping results.
        """
        return {
            "columns": self.columns,
            "stats_level": self.stats_level.value,
            "groups": [g.to_dict() for g in self.groups],
            "skipped": self.skipped,
            "warning": self.warning,
            "total_rows": self.total_rows,
            "group_count": self.group_count,
        }
