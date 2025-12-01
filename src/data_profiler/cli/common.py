"""Shared CLI utilities and argument parsers.

This module provides common functionality used across CLI subcommands,
including exit codes, output formatting, and shared argument definitions.
"""

from enum import IntEnum
from typing import TextIO

from rich.console import Console

# Rich console for formatted output
console = Console()
error_console = Console(stderr=True)


class ExitCode(IntEnum):
    """CLI exit codes following standard conventions.

    Exit codes 0-2 follow standard Unix conventions.
    Exit codes 10+ are application-specific.
    """

    SUCCESS = 0
    FAILURE = 1
    USAGE_ERROR = 2

    # Application-specific codes
    FILE_NOT_FOUND = 10
    INVALID_FORMAT = 11
    SCHEMA_ERROR = 12
    CARDINALITY_WARNING = 13


def print_error(message: str, *, file: TextIO | None = None) -> None:
    """Print an error message to stderr.

    Args:
        message: Error message to display.
        file: Optional file to write to (defaults to stderr via error_console).
    """
    if file is not None:
        print(f"ERROR: {message}", file=file)
    else:
        error_console.print(f"[red]ERROR:[/red] {message}")


def print_warning(message: str, *, file: TextIO | None = None) -> None:
    """Print a warning message to stderr.

    Args:
        message: Warning message to display.
        file: Optional file to write to (defaults to stderr via error_console).
    """
    if file is not None:
        print(f"WARNING: {message}", file=file)
    else:
        error_console.print(f"[yellow]WARNING:[/yellow] {message}")


def print_success(message: str) -> None:
    """Print a success message to stdout.

    Args:
        message: Success message to display.
    """
    console.print(f"[green]SUCCESS:[/green] {message}")


def print_info(message: str) -> None:
    """Print an info message to stdout.

    Args:
        message: Info message to display.
    """
    console.print(f"[blue]INFO:[/blue] {message}")
