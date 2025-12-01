"""CLI module for data-profiler.

This module provides the command-line interface for the data-profiler tool.

Submodules:
    main: Main CLI entry point with profile and group subcommands
    common: Shared CLI utilities and argument parsers
"""

from data_profiler.cli.common import ExitCode

__all__ = ["ExitCode"]
