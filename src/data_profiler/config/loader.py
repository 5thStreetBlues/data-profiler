"""Configuration loading and merging.

This module provides functions for loading configuration from files
and environment variables, with proper precedence handling.

Configuration Precedence (highest to lowest):
1. CLI arguments
2. Configuration file
3. Environment variables
4. Default values
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

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


# Environment variable prefix
ENV_PREFIX = "DATA_PROFILER_"


def get_default_config() -> ProfilerConfig:
    """Get default configuration.

    Returns:
        ProfilerConfig with default values.
    """
    return ProfilerConfig()


def load_config_file(path: Path) -> dict[str, Any]:
    """Load configuration from a JSON file.

    Args:
        path: Path to configuration file.

    Returns:
        Dictionary with configuration values.

    Raises:
        FileNotFoundError: If file doesn't exist.
        json.JSONDecodeError: If file is not valid JSON.
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    content = path.read_text(encoding="utf-8")
    return json.loads(content)


def load_env_config() -> dict[str, Any]:
    """Load configuration from environment variables.

    Environment variables are prefixed with DATA_PROFILER_ and use
    underscores for nested keys. For example:
    - DATA_PROFILER_BACKEND=polars
    - DATA_PROFILER_OUTPUT_FORMAT=json
    - DATA_PROFILER_GROUPING_MAX_GROUPS=50

    Returns:
        Dictionary with configuration values from environment.
    """
    config: dict[str, Any] = {}

    # Simple top-level settings
    env_mappings = {
        "BACKEND": ("backend", str),
        "SAMPLE_RATE": ("sample_rate", float),
        "RECURSIVE": ("recursive", _parse_bool),
        "COMPUTE_FULL_STATS": ("compute_full_stats", _parse_bool),
        "VERBOSITY": ("verbosity", int),
    }

    for env_key, (config_key, converter) in env_mappings.items():
        full_key = f"{ENV_PREFIX}{env_key}"
        value = os.environ.get(full_key)
        if value is not None:
            try:
                config[config_key] = converter(value)
            except (ValueError, TypeError):
                pass  # Ignore invalid values

    # Output settings
    output_mappings = {
        "OUTPUT_FORMAT": ("format", str),
        "OUTPUT_PATH": ("output_path", str),
        "HTML_ENGINE": ("html_engine", str),
        "HTML_DARK_MODE": ("html_dark_mode", _parse_bool),
        "HTML_MINIMAL": ("html_minimal", _parse_bool),
        "PRETTY_PRINT": ("pretty_print", _parse_bool),
    }

    output_config: dict[str, Any] = {}
    for env_key, (config_key, converter) in output_mappings.items():
        full_key = f"{ENV_PREFIX}{env_key}"
        value = os.environ.get(full_key)
        if value is not None:
            try:
                output_config[config_key] = converter(value)
            except (ValueError, TypeError):
                pass

    if output_config:
        config["output"] = output_config

    # Grouping settings
    grouping_mappings = {
        "MAX_GROUPS": ("max_groups", int),
        "STATS_LEVEL": ("stats_level", str),
        "CARDINALITY_ACTION": ("cardinality_action", str),
    }

    grouping_config: dict[str, Any] = {}
    for env_key, (config_key, converter) in grouping_mappings.items():
        full_key = f"{ENV_PREFIX}{env_key}"
        value = os.environ.get(full_key)
        if value is not None:
            try:
                grouping_config[config_key] = converter(value)
            except (ValueError, TypeError):
                pass

    if grouping_config:
        config["grouping"] = grouping_config

    # Relationship settings
    rel_mappings = {
        "RELATIONSHIPS_ENABLED": ("enabled", _parse_bool),
        "RELATIONSHIPS_MIN_CONFIDENCE": ("min_confidence", float),
        "RELATIONSHIPS_HINTS_FILE": ("hints_file", str),
    }

    rel_config: dict[str, Any] = {}
    for env_key, (config_key, converter) in rel_mappings.items():
        full_key = f"{ENV_PREFIX}{env_key}"
        value = os.environ.get(full_key)
        if value is not None:
            try:
                rel_config[config_key] = converter(value)
            except (ValueError, TypeError):
                pass

    if rel_config:
        config["relationships"] = rel_config

    return config


def _parse_bool(value: str) -> bool:
    """Parse boolean from string.

    Args:
        value: String value.

    Returns:
        Boolean value.
    """
    return value.lower() in ("true", "1", "yes", "on")


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple configuration dictionaries.

    Later configs override earlier ones. Nested dictionaries are merged.

    Args:
        *configs: Configuration dictionaries to merge.

    Returns:
        Merged configuration dictionary.
    """
    result: dict[str, Any] = {}

    for config in configs:
        for key, value in config.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Merge nested dicts
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value

    return result


def load_config(
    config_file: Path | None = None,
    cli_args: dict[str, Any] | None = None,
    use_env: bool = True,
) -> ProfilerConfig:
    """Load configuration with proper precedence.

    Configuration is loaded and merged in this order:
    1. Default values
    2. Environment variables (if use_env=True)
    3. Configuration file (if provided)
    4. CLI arguments (if provided)

    Args:
        config_file: Path to configuration file (optional).
        cli_args: Dictionary of CLI arguments (optional).
        use_env: Whether to load from environment variables.

    Returns:
        Merged ProfilerConfig.
    """
    # Start with defaults
    config_dict = get_default_config().to_dict()

    # Layer 2: Environment variables
    if use_env:
        env_config = load_env_config()
        config_dict = merge_configs(config_dict, env_config)

    # Layer 3: Configuration file
    if config_file:
        try:
            file_config = load_config_file(config_file)
            config_dict = merge_configs(config_dict, file_config)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Ignore file errors, use other sources

    # Layer 4: CLI arguments
    if cli_args:
        config_dict = merge_configs(config_dict, cli_args)

    return ProfilerConfig.from_dict(config_dict)


def cli_args_to_config(args: Any) -> dict[str, Any]:
    """Convert argparse namespace to configuration dictionary.

    Args:
        args: argparse.Namespace from CLI parsing.

    Returns:
        Configuration dictionary.
    """
    config: dict[str, Any] = {}

    # Top-level options
    if hasattr(args, "backend") and args.backend:
        config["backend"] = args.backend
    if hasattr(args, "sample") and args.sample is not None:
        config["sample_rate"] = args.sample
    if hasattr(args, "columns") and args.columns:
        config["columns"] = args.columns
    if hasattr(args, "recursive"):
        config["recursive"] = args.recursive
    if hasattr(args, "verbosity") and args.verbosity is not None:
        config["verbosity"] = args.verbosity

    # Output options
    output: dict[str, Any] = {}
    if hasattr(args, "format") and args.format:
        output["format"] = args.format
    if hasattr(args, "output") and args.output:
        output["output_path"] = str(args.output)
    if hasattr(args, "html_engine") and args.html_engine:
        output["html_engine"] = args.html_engine
    if output:
        config["output"] = output

    # Grouping options
    grouping: dict[str, Any] = {}
    if hasattr(args, "max_groups") and args.max_groups is not None:
        grouping["max_groups"] = args.max_groups
    if hasattr(args, "stats") and args.stats:
        grouping["stats_level"] = args.stats
    if grouping:
        config["grouping"] = grouping

    # Relationship options
    relationships: dict[str, Any] = {}
    if hasattr(args, "relationships") and args.relationships:
        relationships["enabled"] = True
    if hasattr(args, "hints") and args.hints:
        relationships["hints_file"] = str(args.hints)
    if relationships:
        config["relationships"] = relationships

    return config


def write_config_file(config: ProfilerConfig, path: Path) -> None:
    """Write configuration to a JSON file.

    Args:
        config: ProfilerConfig to write.
        path: Output file path.
    """
    content = json.dumps(config.to_dict(), indent=2)
    path.write_text(content, encoding="utf-8")


def get_example_config() -> str:
    """Get example configuration file content.

    Returns:
        JSON string with example configuration.
    """
    example = {
        "backend": "auto",
        "sample_rate": None,
        "recursive": False,
        "compute_full_stats": True,
        "verbosity": 1,
        "output": {
            "format": "stdout",
            "output_path": None,
            "html_engine": "custom",
            "html_dark_mode": False,
            "pretty_print": True,
        },
        "grouping": {
            "max_groups": 100,
            "stats_level": "count",
            "cardinality_action": "skip",
        },
        "relationships": {
            "enabled": False,
            "min_confidence": 0.8,
            "hints_file": None,
            "detect_naming_patterns": True,
            "detect_value_overlap": True,
        },
    }
    return json.dumps(example, indent=2)
