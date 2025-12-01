"""Configuration precedence smoke tests.

These tests verify that configuration loading and precedence
works correctly (CLI > config file > env > defaults).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from data_profiler.config.schema import (
    ProfilerConfig,
    OutputConfig,
    GroupingConfig,
    Backend,
    OutputFormat,
    StatsLevel,
)
from data_profiler.config.loader import (
    load_config,
    load_config_file,
    load_env_config,
    merge_configs,
    cli_args_to_config,
    get_default_config,
)


class TestDefaultConfig:
    """Tests for default configuration."""

    def test_default_config_values(self) -> None:
        """Test that default config has expected values."""
        config = get_default_config()

        assert config.backend == Backend.AUTO
        assert config.sample_rate is None
        assert config.recursive is False
        assert config.verbosity == 1
        assert config.output.format == OutputFormat.STDOUT
        assert config.grouping.max_groups == 100
        assert config.relationships.enabled is False

    def test_default_config_serialization(self) -> None:
        """Test that default config can be serialized."""
        config = get_default_config()
        config_dict = config.to_dict()

        assert "backend" in config_dict
        assert "output" in config_dict
        assert "grouping" in config_dict

        # Can reconstruct
        reconstructed = ProfilerConfig.from_dict(config_dict)
        assert reconstructed.backend == config.backend


class TestConfigFile:
    """Tests for configuration file loading."""

    def test_load_valid_config_file(self, tmp_path: Path) -> None:
        """Test loading a valid configuration file."""
        config_data = {
            "backend": "polars",
            "recursive": True,
            "output": {
                "format": "json",
            },
            "grouping": {
                "max_groups": 50,
            },
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        loaded = load_config_file(config_file)

        assert loaded["backend"] == "polars"
        assert loaded["recursive"] is True
        assert loaded["output"]["format"] == "json"
        assert loaded["grouping"]["max_groups"] == 50

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_config_file(tmp_path / "nonexistent.json")

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test loading invalid JSON raises error."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json {")

        with pytest.raises(json.JSONDecodeError):
            load_config_file(invalid_file)


class TestEnvironmentConfig:
    """Tests for environment variable configuration."""

    def test_load_env_backend(self) -> None:
        """Test loading backend from environment."""
        with patch.dict(os.environ, {"DATA_PROFILER_BACKEND": "pandas"}):
            env_config = load_env_config()
            assert env_config.get("backend") == "pandas"

    def test_load_env_recursive(self) -> None:
        """Test loading recursive from environment."""
        with patch.dict(os.environ, {"DATA_PROFILER_RECURSIVE": "true"}):
            env_config = load_env_config()
            assert env_config.get("recursive") is True

    def test_load_env_max_groups(self) -> None:
        """Test loading max_groups from environment."""
        with patch.dict(os.environ, {"DATA_PROFILER_MAX_GROUPS": "200"}):
            env_config = load_env_config()
            assert env_config.get("grouping", {}).get("max_groups") == 200

    def test_env_invalid_values_ignored(self) -> None:
        """Test that invalid environment values are ignored."""
        with patch.dict(os.environ, {
            "DATA_PROFILER_MAX_GROUPS": "not_a_number",
            "DATA_PROFILER_BACKEND": "polars",  # Valid
        }):
            env_config = load_env_config()
            # Invalid max_groups should be ignored
            assert "grouping" not in env_config or "max_groups" not in env_config.get("grouping", {})
            # Valid backend should be loaded
            assert env_config.get("backend") == "polars"


class TestConfigMerging:
    """Tests for configuration merging."""

    def test_merge_simple_configs(self) -> None:
        """Test merging simple configurations."""
        config1 = {"backend": "auto", "recursive": False}
        config2 = {"backend": "polars", "verbosity": 2}

        merged = merge_configs(config1, config2)

        assert merged["backend"] == "polars"  # Overridden
        assert merged["recursive"] is False  # From config1
        assert merged["verbosity"] == 2  # From config2

    def test_merge_nested_configs(self) -> None:
        """Test merging nested configurations."""
        config1 = {
            "output": {"format": "stdout", "pretty_print": True},
        }
        config2 = {
            "output": {"format": "json"},
        }

        merged = merge_configs(config1, config2)

        # Nested merge
        assert merged["output"]["format"] == "json"  # Overridden
        assert merged["output"]["pretty_print"] is True  # Preserved


class TestConfigPrecedence:
    """Tests for configuration precedence."""

    def test_cli_overrides_file(self, tmp_path: Path) -> None:
        """Test that CLI arguments override config file."""
        # Config file says polars
        config_data = {"backend": "polars"}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        # CLI says pandas
        cli_args = {"backend": "pandas"}

        config = load_config(config_file=config_file, cli_args=cli_args)

        # CLI should win
        assert config.backend == Backend.PANDAS

    def test_file_overrides_env(self, tmp_path: Path) -> None:
        """Test that config file overrides environment."""
        # Environment says pandas
        with patch.dict(os.environ, {"DATA_PROFILER_BACKEND": "pandas"}):
            # Config file says polars
            config_data = {"backend": "polars"}
            config_file = tmp_path / "config.json"
            config_file.write_text(json.dumps(config_data))

            config = load_config(config_file=config_file)

            # File should win over env
            assert config.backend == Backend.POLARS

    def test_env_overrides_defaults(self) -> None:
        """Test that environment overrides defaults."""
        with patch.dict(os.environ, {"DATA_PROFILER_VERBOSITY": "3"}):
            config = load_config()

            # Env should win over default (which is 1)
            assert config.verbosity == 3

    def test_full_precedence_chain(self, tmp_path: Path) -> None:
        """Test full precedence chain: CLI > file > env > defaults."""
        # Default: recursive=False

        # Environment: recursive=True
        with patch.dict(os.environ, {"DATA_PROFILER_RECURSIVE": "true"}):
            # File: recursive=False (overrides env)
            config_data = {"recursive": False, "verbosity": 2}
            config_file = tmp_path / "config.json"
            config_file.write_text(json.dumps(config_data))

            # CLI: recursive=True (overrides file)
            cli_args = {"recursive": True}

            config = load_config(
                config_file=config_file,
                cli_args=cli_args,
            )

            # CLI wins
            assert config.recursive is True
            # File wins for verbosity (not in CLI)
            assert config.verbosity == 2


class TestCLIArgsConversion:
    """Tests for CLI arguments to config conversion."""

    def test_convert_basic_args(self) -> None:
        """Test converting basic CLI arguments."""
        from argparse import Namespace

        args = Namespace(
            backend="polars",
            sample=0.5,
            recursive=True,
            verbosity=2,
        )

        config = cli_args_to_config(args)

        assert config["backend"] == "polars"
        assert config["sample_rate"] == 0.5
        assert config["recursive"] is True
        assert config["verbosity"] == 2

    def test_convert_output_args(self) -> None:
        """Test converting output CLI arguments."""
        from argparse import Namespace

        args = Namespace(
            format="json",
            output=Path("/output/file.json"),
            html_engine="ydata",
        )

        config = cli_args_to_config(args)

        assert config["output"]["format"] == "json"
        # Path may be converted to string with platform-specific separators
        assert "file.json" in config["output"]["output_path"]
        assert config["output"]["html_engine"] == "ydata"

    def test_convert_grouping_args(self) -> None:
        """Test converting grouping CLI arguments."""
        from argparse import Namespace

        args = Namespace(
            max_groups=50,
            stats="basic",
        )

        config = cli_args_to_config(args)

        assert config["grouping"]["max_groups"] == 50
        assert config["grouping"]["stats_level"] == "basic"

    def test_convert_missing_args(self) -> None:
        """Test converting when args are missing."""
        from argparse import Namespace

        # Empty namespace
        args = Namespace()

        config = cli_args_to_config(args)

        # Should return empty config (no None values)
        assert config == {}
