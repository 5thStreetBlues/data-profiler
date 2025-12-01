#!/usr/bin/env python
"""data-profiler CLI - Multi-file dataset profiling tool.

Profile datasets for structure, quality, and relationships.
Supports CSV, JSON, and Parquet formats.

Usage:
    data-profiler [OPTIONS] [FILES/DIRECTORIES]
    data-profiler profile [OPTIONS] [FILES/DIRECTORIES]
    data-profiler group [OPTIONS] FILE --by COLUMNS

Examples:
    # Profile a single file
    data-profiler data/instruments.parquet

    # Profile multiple files with output
    data-profiler data/*.parquet --output report.json

    # Profile a directory recursively
    data-profiler data/ --recursive --format html

    # Get grouped row counts
    data-profiler group data/cars.parquet --by make,model

    # Show help
    data-profiler --help
    data-profiler profile --help
    data-profiler group --help

Exit Codes:
    0:  Success
    1:  General failure
    2:  Usage error (invalid arguments)
    10: File not found
    11: Invalid file format
    12: Schema error
    13: Cardinality warning (groups exceeded threshold)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from data_profiler import __version__
from data_profiler.cli.common import (
    ExitCode,
    console,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from data_profiler.cli.formatters import HTMLFormatter, JSONFormatter, TableFormatter


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands.

    Returns:
        Configured ArgumentParser with profile and group subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="data-profiler",
        description="Multi-file dataset profiling for structure, quality, and relationships.",
        epilog="Use 'data-profiler <command> --help' for command-specific help.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="show program's version number and exit",
    )

    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available commands (use 'data-profiler <command> --help' for details)",
        metavar="<command>",
    )

    # Profile subcommand (also the default when no subcommand given)
    _create_profile_parser(subparsers)

    # Group subcommand
    _create_group_parser(subparsers)

    return parser


def _create_profile_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> argparse.ArgumentParser:
    """Create the profile subcommand parser.

    Args:
        subparsers: Parent subparsers action.

    Returns:
        Configured profile subcommand parser.
    """
    profile_parser = subparsers.add_parser(
        "profile",
        help="Profile one or more data files",
        description="Profile datasets for structure, quality metrics, and column statistics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Positional arguments
    profile_parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        metavar="PATH",
        help="Files or directories to profile (supports wildcards)",
    )

    # Input options
    input_group = profile_parser.add_argument_group("input options")
    input_group.add_argument(
        "-f",
        "--files",
        nargs="+",
        type=Path,
        metavar="FILE",
        help="specific files to profile (supports wildcards)",
    )
    input_group.add_argument(
        "-d",
        "--directories",
        nargs="+",
        type=Path,
        metavar="DIR",
        help="directories to scan for data files",
    )
    input_group.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="scan directories recursively",
    )
    input_group.add_argument(
        "--config",
        type=Path,
        metavar="FILE",
        help="configuration file (JSON format)",
    )

    # Output options
    output_group = profile_parser.add_argument_group("output options")
    output_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="PATH",
        help="output file or directory path",
    )
    output_group.add_argument(
        "--format",
        choices=["json", "html", "markdown", "stdout"],
        default="stdout",
        help="output format (default: stdout)",
    )
    output_group.add_argument(
        "--stdout",
        action="store_true",
        help="print summary to stdout (in addition to output file)",
    )
    output_group.add_argument(
        "-v",
        "--verbosity",
        type=int,
        choices=[0, 1, 2, 3],
        default=1,
        help="verbosity level: 0=quiet, 1=normal, 2=detailed, 3=debug (default: 1)",
    )

    # Profiling options
    profile_options = profile_parser.add_argument_group("profiling options")
    profile_options.add_argument(
        "--columns",
        nargs="+",
        metavar="COL",
        help="profile only specific columns",
    )
    profile_options.add_argument(
        "--relationships",
        action="store_true",
        help="enable relationship/FK discovery",
    )
    profile_options.add_argument(
        "--hints",
        type=Path,
        metavar="FILE",
        help="relationship hints file (JSON format)",
    )
    profile_options.add_argument(
        "--sample",
        type=float,
        metavar="RATE",
        help="sample rate for large files (0.0-1.0)",
    )
    profile_options.add_argument(
        "--backend",
        choices=["auto", "polars", "pandas"],
        default="auto",
        help="DataFrame backend (default: auto)",
    )
    profile_options.add_argument(
        "--html-engine",
        choices=["custom", "ydata"],
        default="custom",
        help="HTML generation engine: custom (built-in) or ydata (ydata-profiling)",
    )

    return profile_parser


def _create_group_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> argparse.ArgumentParser:
    """Create the group subcommand parser.

    Args:
        subparsers: Parent subparsers action.

    Returns:
        Configured group subcommand parser.
    """
    group_parser = subparsers.add_parser(
        "group",
        help="Get row counts grouped by specified columns",
        description="Compute row counts (and optional statistics) grouped by column values.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic grouping
    data-profiler group data/cars.parquet --by make,model

    # With basic statistics
    data-profiler group data/cars.parquet --by make --stats basic

    # Full profile per group (with higher cardinality threshold)
    data-profiler group data/*.parquet --by exchange --stats full --max-groups 50

Statistics levels:
    count  - Row count only (default)
    basic  - Row count + min, max, mean of numeric columns
    full   - Full column profile per group
        """,
    )

    # Positional arguments
    group_parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        metavar="FILE",
        help="files to analyze (supports wildcards)",
    )

    # Required grouping options
    group_options = group_parser.add_argument_group("grouping options")
    group_options.add_argument(
        "-b",
        "--by",
        required=True,
        metavar="COLUMNS",
        help="columns to group by (comma-separated)",
    )
    group_options.add_argument(
        "-s",
        "--stats",
        choices=["count", "basic", "full"],
        default="count",
        help="statistics level: count, basic, full (default: count)",
    )
    group_options.add_argument(
        "--max-groups",
        type=int,
        default=10,
        metavar="N",
        help="maximum groups before warning/skip (default: 10)",
    )
    group_options.add_argument(
        "--cross-file",
        action="store_true",
        help="enable cross-file grouping via relationships",
    )

    # Output options
    output_group = group_parser.add_argument_group("output options")
    output_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="FILE",
        help="output file path",
    )
    output_group.add_argument(
        "--format",
        choices=["json", "csv", "stdout"],
        default="stdout",
        help="output format (default: stdout)",
    )

    return group_parser


def run_profile(args: argparse.Namespace) -> ExitCode:
    """Execute the profile command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code indicating success or failure.
    """
    from data_profiler.core.profiler import DataProfiler
    from data_profiler.models.profile import FileProfile, DatasetProfile
    from data_profiler.output.json_formatter import JSONFormatter as OutputJSONFormatter
    from data_profiler.output.html_formatter import HTMLFormatter as OutputHTMLFormatter
    from data_profiler.output.html_ydata import YDataHTMLFormatter
    from data_profiler.output.markdown_formatter import MarkdownFormatter

    # Collect all input paths
    paths: list[Path] = []
    if args.paths:
        paths.extend(args.paths)
    if args.files:
        paths.extend(args.files)
    if args.directories:
        paths.extend(args.directories)

    if not paths and not args.config:
        print_error("No input files or directories specified.")
        print_info("Use 'data-profiler profile --help' for usage information.")
        return ExitCode.USAGE_ERROR

    # Display header
    if args.verbosity >= 1:
        console.print(f"[bold]Data Profiler v{__version__}[/bold]")
        console.print()

    # Get backend from args
    backend = getattr(args, "backend", "auto")

    # Initialize profiler
    profiler = DataProfiler(
        backend=backend,
        compute_full_stats=True,
    )

    # Initialize formatters
    table_formatter = TableFormatter()
    json_formatter = JSONFormatter()
    # Choose HTML formatter based on --html-engine option
    html_engine = getattr(args, "html_engine", "custom")
    if html_engine == "ydata":
        html_formatter = YDataHTMLFormatter()
    else:
        html_formatter = OutputHTMLFormatter()
    markdown_formatter = MarkdownFormatter()

    # Collect profiles
    file_profiles: list[FileProfile] = []
    directories: list[Path] = []
    exit_code = ExitCode.SUCCESS

    # Separate files and directories
    for path in paths:
        if not path.exists():
            print_warning(f"Path not found: {path}")
            exit_code = ExitCode.FILE_NOT_FOUND
            continue
        if path.is_dir():
            directories.append(path)
        else:
            file_profiles.append(path)  # Store path, profile later

    # Process directories
    dataset_profiles: list[DatasetProfile] = []
    for dir_path in directories:
        if args.verbosity >= 1:
            console.print(f"Profiling directory: [cyan]{dir_path}[/cyan]")
        try:
            dataset = profiler.profile_directory(
                dir_path,
                recursive=args.recursive,
            )
            dataset_profiles.append(dataset)
        except Exception as e:
            print_error(f"Failed to profile directory {dir_path}: {e}")
            exit_code = ExitCode.FAILURE

    # Process individual files
    profiles: list[FileProfile] = []
    for file_path in file_profiles:
        if args.verbosity >= 1:
            console.print(f"Profiling file: [cyan]{file_path}[/cyan]")
        try:
            profile = profiler.profile(
                file_path,
                columns=args.columns,
                sample_rate=args.sample,
            )
            profiles.append(profile)
        except FileNotFoundError:
            print_error(f"File not found: {file_path}")
            exit_code = ExitCode.FILE_NOT_FOUND
        except ValueError as e:
            print_error(f"Invalid file format: {file_path} - {e}")
            exit_code = ExitCode.INVALID_FORMAT
        except Exception as e:
            print_error(f"Failed to profile {file_path}: {e}")
            exit_code = ExitCode.FAILURE

    # Discover relationships if requested
    relationship_graph = None
    if args.relationships:
        if args.verbosity >= 1:
            console.print("[bold]Discovering relationships...[/bold]")

        # Collect all profiled files
        all_files = [p.file_path for p in profiles]
        for ds in dataset_profiles:
            all_files.extend([fp.file_path for fp in ds.files])

        if all_files:
            try:
                relationship_graph = profiler.discover_relationships(
                    all_files,
                    hints_file=args.hints,
                )
                if args.verbosity >= 1:
                    console.print(
                        f"Found [green]{len(relationship_graph.relationships)}[/green] "
                        f"relationships across [green]{len(relationship_graph.entities)}[/green] entities"
                    )
                    console.print()
            except Exception as e:
                print_warning(f"Failed to discover relationships: {e}")

    # Output results
    if args.format == "stdout" or args.stdout:
        console.print()
        for profile in profiles:
            table_formatter.format_file_profile(profile)
            console.print()
        for dataset in dataset_profiles:
            table_formatter.format_dataset_profile(dataset)
            console.print()

        # Display relationships if discovered
        if relationship_graph and relationship_graph.relationships:
            table_formatter.format_relationship_graph(relationship_graph)
            console.print()

    # Write to file if output specified
    if args.output:
        output_path = args.output

        if args.format == "json":
            content_parts = []
            if profiles:
                for profile in profiles:
                    content_parts.append(json_formatter.format_file_profile(profile))
            if dataset_profiles:
                for dataset in dataset_profiles:
                    content_parts.append(json_formatter.format_dataset_profile(dataset))
            content = "\n".join(content_parts)
        elif args.format == "html":
            content_parts = []
            if profiles:
                for profile in profiles:
                    content_parts.append(html_formatter.format_file_profile(profile))
            if dataset_profiles:
                for dataset in dataset_profiles:
                    content_parts.append(html_formatter.format_dataset_profile(dataset))
            content = "\n".join(content_parts)
        elif args.format == "markdown":
            content_parts = []
            if profiles:
                for profile in profiles:
                    content_parts.append(markdown_formatter.format_file_profile(profile))
            if dataset_profiles:
                for dataset in dataset_profiles:
                    content_parts.append(markdown_formatter.format_dataset_profile(dataset))
            content = "\n\n".join(content_parts)
        else:
            # Default to JSON
            content_parts = []
            if profiles:
                for profile in profiles:
                    content_parts.append(json_formatter.format_file_profile(profile))
            if dataset_profiles:
                for dataset in dataset_profiles:
                    content_parts.append(json_formatter.format_dataset_profile(dataset))
            content = "\n".join(content_parts)

        output_path.write_text(content)
        print_success(f"Output written to: {output_path}")

    return exit_code


def run_group(args: argparse.Namespace) -> ExitCode:
    """Execute the group command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code indicating success or failure.
    """
    from data_profiler.core.profiler import DataProfiler
    from data_profiler.models.grouping import StatsLevel

    # Parse columns
    columns = [col.strip() for col in args.by.split(",")]

    if not columns:
        print_error("No grouping columns specified.")
        return ExitCode.USAGE_ERROR

    console.print(f"[bold]Grouped Row Counts[/bold]")
    console.print()

    # Initialize profiler and formatters
    profiler = DataProfiler(backend="auto")
    table_formatter = TableFormatter()
    json_formatter = JSONFormatter()

    exit_code = ExitCode.SUCCESS

    # Process each file
    for path in args.paths:
        if not path.exists():
            print_warning(f"Path not found: {path}")
            exit_code = ExitCode.FILE_NOT_FOUND
            continue

        console.print(f"File: [cyan]{path}[/cyan]")
        console.print(f"Group by: {', '.join(columns)}")
        console.print()

        try:
            result = profiler.group(
                path,
                by=columns,
                stats_level=args.stats,
                max_groups=args.max_groups,
            )

            # Output based on format
            if args.format == "stdout":
                table_formatter.format_grouping_result(result)
                console.print()
            elif args.format == "json":
                json_output = json_formatter.format_grouping_result(result)
                if args.output:
                    args.output.write_text(json_output)
                    print_success(f"Output written to: {args.output}")
                else:
                    console.print(json_output)
            elif args.format == "csv":
                # Simple CSV output
                csv_lines = [",".join(columns + ["count"])]
                for group in result.groups:
                    values = [str(group.key.get(col, "")) for col in columns]
                    values.append(str(group.row_count))
                    csv_lines.append(",".join(values))
                csv_output = "\n".join(csv_lines)
                if args.output:
                    args.output.write_text(csv_output)
                    print_success(f"Output written to: {args.output}")
                else:
                    console.print(csv_output)

            # Warn if skipped due to cardinality
            if result.skipped:
                print_warning(result.warning or "Group count exceeded threshold")
                exit_code = ExitCode.CARDINALITY_WARNING

        except FileNotFoundError:
            print_error(f"File not found: {path}")
            exit_code = ExitCode.FILE_NOT_FOUND
        except ValueError as e:
            print_error(f"Error: {e}")
            exit_code = ExitCode.FAILURE
        except Exception as e:
            print_error(f"Failed to group {path}: {e}")
            exit_code = ExitCode.FAILURE

    return exit_code


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code as integer.
    """
    parser = create_parser()

    # Parse arguments
    args = parser.parse_args(argv)

    # Handle no command (default to profile with empty paths shows help)
    if args.command is None:
        # Check if any positional args were given (they would be for profile)
        # Since we have no subcommand, show help
        parser.print_help()
        return ExitCode.SUCCESS

    # Dispatch to subcommand
    if args.command == "profile":
        return run_profile(args)
    elif args.command == "group":
        return run_group(args)
    else:
        print_error(f"Unknown command: {args.command}")
        return ExitCode.USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())
