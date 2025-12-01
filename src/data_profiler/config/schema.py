"""Configuration schema definitions.

This module defines the configuration schema using dataclasses
for type-safe configuration management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal


class Backend(str, Enum):
    """DataFrame backend options."""

    AUTO = "auto"
    POLARS = "polars"
    PANDAS = "pandas"


class OutputFormat(str, Enum):
    """Output format options."""

    STDOUT = "stdout"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"


class HTMLEngine(str, Enum):
    """HTML generation engine options."""

    CUSTOM = "custom"
    YDATA = "ydata"


class StatsLevel(str, Enum):
    """Statistics level for grouping."""

    COUNT = "count"
    BASIC = "basic"
    FULL = "full"


@dataclass
class OutputConfig:
    """Configuration for output formatting.

    Attributes:
        format: Output format (stdout, json, html, markdown).
        output_path: Path for output file (None for stdout).
        html_engine: HTML generation engine (custom or ydata).
        html_dark_mode: Use dark mode for HTML output.
        html_minimal: Generate minimal HTML report (ydata only).
        pretty_print: Pretty-print JSON output.
        include_toc: Include table of contents in Markdown.
    """

    format: OutputFormat = OutputFormat.STDOUT
    output_path: Path | None = None
    html_engine: HTMLEngine = HTMLEngine.CUSTOM
    html_dark_mode: bool = False
    html_minimal: bool = False
    pretty_print: bool = True
    include_toc: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "format": self.format.value,
            "output_path": str(self.output_path) if self.output_path else None,
            "html_engine": self.html_engine.value,
            "html_dark_mode": self.html_dark_mode,
            "html_minimal": self.html_minimal,
            "pretty_print": self.pretty_print,
            "include_toc": self.include_toc,
        }


@dataclass
class GroupingConfig:
    """Configuration for grouping operations.

    Attributes:
        max_groups: Maximum groups before warning/skip.
        stats_level: Statistics level (count, basic, full).
        cardinality_action: Action when exceeding threshold (warn, skip, sample).
        sample_rate: Sample rate when using sample action.
    """

    max_groups: int = 100
    stats_level: StatsLevel = StatsLevel.COUNT
    cardinality_action: Literal["warn", "skip", "sample"] = "skip"
    sample_rate: float = 0.1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "max_groups": self.max_groups,
            "stats_level": self.stats_level.value,
            "cardinality_action": self.cardinality_action,
            "sample_rate": self.sample_rate,
        }


@dataclass
class RelationshipConfig:
    """Configuration for relationship discovery.

    Attributes:
        enabled: Enable relationship discovery.
        min_confidence: Minimum confidence for detected relationships.
        hints_file: Path to relationship hints file.
        detect_naming_patterns: Detect FK by naming patterns (_id, _code, etc).
        detect_value_overlap: Detect FK by value overlap analysis.
    """

    enabled: bool = False
    min_confidence: float = 0.8
    hints_file: Path | None = None
    detect_naming_patterns: bool = True
    detect_value_overlap: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "enabled": self.enabled,
            "min_confidence": self.min_confidence,
            "hints_file": str(self.hints_file) if self.hints_file else None,
            "detect_naming_patterns": self.detect_naming_patterns,
            "detect_value_overlap": self.detect_value_overlap,
        }


@dataclass
class ProfilerConfig:
    """Main configuration for data-profiler.

    Attributes:
        backend: DataFrame backend (auto, polars, pandas).
        sample_rate: Sample rate for large files (None for no sampling).
        columns: Specific columns to profile (None for all).
        recursive: Scan directories recursively.
        compute_full_stats: Compute full statistics.
        verbosity: Verbosity level (0-3).
        output: Output configuration.
        grouping: Grouping configuration.
        relationships: Relationship discovery configuration.
    """

    backend: Backend = Backend.AUTO
    sample_rate: float | None = None
    columns: list[str] | None = None
    recursive: bool = False
    compute_full_stats: bool = True
    verbosity: int = 1
    output: OutputConfig = field(default_factory=OutputConfig)
    grouping: GroupingConfig = field(default_factory=GroupingConfig)
    relationships: RelationshipConfig = field(default_factory=RelationshipConfig)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "backend": self.backend.value,
            "sample_rate": self.sample_rate,
            "columns": self.columns,
            "recursive": self.recursive,
            "compute_full_stats": self.compute_full_stats,
            "verbosity": self.verbosity,
            "output": self.output.to_dict(),
            "grouping": self.grouping.to_dict(),
            "relationships": self.relationships.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProfilerConfig:
        """Create configuration from dictionary.

        Args:
            data: Dictionary with configuration values.

        Returns:
            ProfilerConfig instance.
        """
        # Parse nested configs
        output_data = data.get("output", {})
        output_config = OutputConfig(
            format=OutputFormat(output_data.get("format", "stdout")),
            output_path=Path(output_data["output_path"]) if output_data.get("output_path") else None,
            html_engine=HTMLEngine(output_data.get("html_engine", "custom")),
            html_dark_mode=output_data.get("html_dark_mode", False),
            html_minimal=output_data.get("html_minimal", False),
            pretty_print=output_data.get("pretty_print", True),
            include_toc=output_data.get("include_toc", False),
        )

        grouping_data = data.get("grouping", {})
        grouping_config = GroupingConfig(
            max_groups=grouping_data.get("max_groups", 100),
            stats_level=StatsLevel(grouping_data.get("stats_level", "count")),
            cardinality_action=grouping_data.get("cardinality_action", "skip"),
            sample_rate=grouping_data.get("sample_rate", 0.1),
        )

        rel_data = data.get("relationships", {})
        rel_config = RelationshipConfig(
            enabled=rel_data.get("enabled", False),
            min_confidence=rel_data.get("min_confidence", 0.8),
            hints_file=Path(rel_data["hints_file"]) if rel_data.get("hints_file") else None,
            detect_naming_patterns=rel_data.get("detect_naming_patterns", True),
            detect_value_overlap=rel_data.get("detect_value_overlap", True),
        )

        return cls(
            backend=Backend(data.get("backend", "auto")),
            sample_rate=data.get("sample_rate"),
            columns=data.get("columns"),
            recursive=data.get("recursive", False),
            compute_full_stats=data.get("compute_full_stats", True),
            verbosity=data.get("verbosity", 1),
            output=output_config,
            grouping=grouping_config,
            relationships=rel_config,
        )
