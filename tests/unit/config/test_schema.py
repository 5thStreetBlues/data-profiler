"""Unit tests for configuration schema.

Tests for ProfilerConfig, OutputConfig, GroupingConfig, and RelationshipConfig.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from data_profiler.config.schema import (
    ProfilerConfig,
    OutputConfig,
    GroupingConfig,
    RelationshipConfig,
    Backend,
    OutputFormat,
    HTMLEngine,
    StatsLevel,
)


class TestOutputConfig:
    """Tests for OutputConfig."""

    def test_default_values(self) -> None:
        """Test default OutputConfig values."""
        config = OutputConfig()

        assert config.format == OutputFormat.STDOUT
        assert config.output_path is None
        assert config.html_engine == HTMLEngine.CUSTOM
        assert config.html_dark_mode is False
        assert config.pretty_print is True

    def test_custom_values(self) -> None:
        """Test custom OutputConfig values."""
        config = OutputConfig(
            format=OutputFormat.JSON,
            output_path=Path("/output/report.json"),
            html_engine=HTMLEngine.YDATA,
            html_dark_mode=True,
        )

        assert config.format == OutputFormat.JSON
        assert config.output_path == Path("/output/report.json")
        assert config.html_engine == HTMLEngine.YDATA
        assert config.html_dark_mode is True

    def test_to_dict(self) -> None:
        """Test OutputConfig serialization."""
        config = OutputConfig(
            format=OutputFormat.HTML,
            output_path=Path("/output/report.html"),
        )

        data = config.to_dict()

        assert data["format"] == "html"
        assert "report.html" in data["output_path"]


class TestGroupingConfig:
    """Tests for GroupingConfig."""

    def test_default_values(self) -> None:
        """Test default GroupingConfig values."""
        config = GroupingConfig()

        assert config.max_groups == 100
        assert config.stats_level == StatsLevel.COUNT
        assert config.cardinality_action == "skip"
        assert config.sample_rate == 0.1

    def test_custom_values(self) -> None:
        """Test custom GroupingConfig values."""
        config = GroupingConfig(
            max_groups=50,
            stats_level=StatsLevel.BASIC,
            cardinality_action="warn",
            sample_rate=0.2,
        )

        assert config.max_groups == 50
        assert config.stats_level == StatsLevel.BASIC
        assert config.cardinality_action == "warn"
        assert config.sample_rate == 0.2

    def test_to_dict(self) -> None:
        """Test GroupingConfig serialization."""
        config = GroupingConfig(
            max_groups=200,
            stats_level=StatsLevel.FULL,
        )

        data = config.to_dict()

        assert data["max_groups"] == 200
        assert data["stats_level"] == "full"


class TestRelationshipConfig:
    """Tests for RelationshipConfig."""

    def test_default_values(self) -> None:
        """Test default RelationshipConfig values."""
        config = RelationshipConfig()

        assert config.enabled is False
        assert config.min_confidence == 0.8
        assert config.hints_file is None
        assert config.detect_naming_patterns is True
        assert config.detect_value_overlap is True

    def test_custom_values(self) -> None:
        """Test custom RelationshipConfig values."""
        config = RelationshipConfig(
            enabled=True,
            min_confidence=0.9,
            hints_file=Path("/hints/relationships.json"),
        )

        assert config.enabled is True
        assert config.min_confidence == 0.9
        assert config.hints_file == Path("/hints/relationships.json")

    def test_to_dict(self) -> None:
        """Test RelationshipConfig serialization."""
        config = RelationshipConfig(enabled=True)

        data = config.to_dict()

        assert data["enabled"] is True


class TestProfilerConfig:
    """Tests for ProfilerConfig."""

    def test_default_values(self) -> None:
        """Test default ProfilerConfig values."""
        config = ProfilerConfig()

        assert config.backend == Backend.AUTO
        assert config.sample_rate is None
        assert config.columns is None
        assert config.recursive is False
        assert config.verbosity == 1
        assert isinstance(config.output, OutputConfig)
        assert isinstance(config.grouping, GroupingConfig)
        assert isinstance(config.relationships, RelationshipConfig)

    def test_custom_values(self) -> None:
        """Test custom ProfilerConfig values."""
        config = ProfilerConfig(
            backend=Backend.POLARS,
            sample_rate=0.5,
            columns=["id", "name"],
            recursive=True,
            verbosity=2,
        )

        assert config.backend == Backend.POLARS
        assert config.sample_rate == 0.5
        assert config.columns == ["id", "name"]
        assert config.recursive is True
        assert config.verbosity == 2

    def test_to_dict(self) -> None:
        """Test ProfilerConfig serialization."""
        config = ProfilerConfig(
            backend=Backend.PANDAS,
            recursive=True,
        )

        data = config.to_dict()

        assert data["backend"] == "pandas"
        assert data["recursive"] is True
        assert "output" in data
        assert "grouping" in data
        assert "relationships" in data

    def test_from_dict(self) -> None:
        """Test ProfilerConfig deserialization."""
        data = {
            "backend": "polars",
            "sample_rate": 0.3,
            "recursive": True,
            "verbosity": 3,
            "output": {
                "format": "json",
                "html_engine": "ydata",
            },
            "grouping": {
                "max_groups": 50,
                "stats_level": "basic",
            },
            "relationships": {
                "enabled": True,
                "min_confidence": 0.95,
            },
        }

        config = ProfilerConfig.from_dict(data)

        assert config.backend == Backend.POLARS
        assert config.sample_rate == 0.3
        assert config.recursive is True
        assert config.verbosity == 3
        assert config.output.format == OutputFormat.JSON
        assert config.output.html_engine == HTMLEngine.YDATA
        assert config.grouping.max_groups == 50
        assert config.grouping.stats_level == StatsLevel.BASIC
        assert config.relationships.enabled is True
        assert config.relationships.min_confidence == 0.95

    def test_roundtrip(self) -> None:
        """Test serialization roundtrip."""
        original = ProfilerConfig(
            backend=Backend.POLARS,
            sample_rate=0.5,
            columns=["a", "b"],
            output=OutputConfig(format=OutputFormat.HTML),
            grouping=GroupingConfig(max_groups=200),
        )

        data = original.to_dict()
        restored = ProfilerConfig.from_dict(data)

        assert restored.backend == original.backend
        assert restored.sample_rate == original.sample_rate
        assert restored.output.format == original.output.format
        assert restored.grouping.max_groups == original.grouping.max_groups


class TestEnums:
    """Tests for configuration enums."""

    def test_backend_values(self) -> None:
        """Test Backend enum values."""
        assert Backend.AUTO.value == "auto"
        assert Backend.POLARS.value == "polars"
        assert Backend.PANDAS.value == "pandas"

    def test_output_format_values(self) -> None:
        """Test OutputFormat enum values."""
        assert OutputFormat.STDOUT.value == "stdout"
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.HTML.value == "html"
        assert OutputFormat.MARKDOWN.value == "markdown"

    def test_html_engine_values(self) -> None:
        """Test HTMLEngine enum values."""
        assert HTMLEngine.CUSTOM.value == "custom"
        assert HTMLEngine.YDATA.value == "ydata"

    def test_stats_level_values(self) -> None:
        """Test StatsLevel enum values."""
        assert StatsLevel.COUNT.value == "count"
        assert StatsLevel.BASIC.value == "basic"
        assert StatsLevel.FULL.value == "full"
