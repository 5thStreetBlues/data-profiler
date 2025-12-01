"""Configuration management for data-profiler.

This module provides configuration loading, validation, and
precedence handling for the data-profiler library.
"""

from __future__ import annotations

from data_profiler.config.schema import (
    ProfilerConfig,
    OutputConfig,
    GroupingConfig,
    RelationshipConfig,
)
from data_profiler.config.loader import (
    load_config,
    load_config_file,
    get_default_config,
)

__all__ = [
    "ProfilerConfig",
    "OutputConfig",
    "GroupingConfig",
    "RelationshipConfig",
    "load_config",
    "load_config_file",
    "get_default_config",
]
