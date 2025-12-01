"""Output formatters for CLI.

This module provides formatters for displaying profiling results
in various formats: table (stdout), JSON, and HTML.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from data_profiler.models.profile import ColumnProfile, FileProfile, DatasetProfile
from data_profiler.models.grouping import GroupingResult, GroupStats
from data_profiler.models.relationships import RelationshipGraph

console = Console()


def format_bytes(size: int) -> str:
    """Format bytes as human-readable string.

    Args:
        size: Size in bytes.

    Returns:
        Human-readable size string.
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size) < 1024.0:
            return f"{size:,.1f} {unit}"
        size /= 1024.0  # type: ignore
    return f"{size:,.1f} PB"


def format_number(value: Any) -> str:
    """Format a number for display.

    Args:
        value: Number to format.

    Returns:
        Formatted string.
    """
    if value is None:
        return "-"
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value:,.2f}"
        return f"{value:.4f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def format_ratio(value: float | None) -> str:
    """Format a ratio as percentage.

    Args:
        value: Ratio between 0 and 1.

    Returns:
        Formatted percentage string.
    """
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


class TableFormatter:
    """Formatter for Rich table output to stdout."""

    def format_file_profile(self, profile: FileProfile) -> None:
        """Display file profile as a formatted table.

        Args:
            profile: FileProfile to display.
        """
        # File summary panel
        summary = Text()
        summary.append(f"File: ", style="bold")
        summary.append(f"{profile.file_path}\n")
        summary.append(f"Format: ", style="bold")
        summary.append(f"{profile.file_format.upper()}  ")
        summary.append(f"Size: ", style="bold")
        summary.append(f"{format_bytes(profile.file_size_bytes)}  ")
        summary.append(f"Rows: ", style="bold")
        summary.append(f"{profile.row_count:,}  ")
        summary.append(f"Columns: ", style="bold")
        summary.append(f"{profile.column_count}")

        if profile.duration_seconds > 0:
            summary.append(f"\nProfiled in: ", style="bold")
            summary.append(f"{profile.duration_seconds:.2f}s")

        console.print(Panel(summary, title="File Profile", border_style="blue"))

        # Columns table
        table = Table(
            title="Column Statistics",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Column", style="bold")
        table.add_column("Type")
        table.add_column("Count", justify="right")
        table.add_column("Nulls", justify="right")
        table.add_column("Null %", justify="right")
        table.add_column("Unique", justify="right")
        table.add_column("Unique %", justify="right")
        table.add_column("Min")
        table.add_column("Max")
        table.add_column("Mean")

        for col in profile.columns:
            table.add_row(
                col.name,
                col.dtype.value,
                format_number(col.count),
                format_number(col.null_count),
                format_ratio(col.null_ratio),
                format_number(col.unique_count),
                format_ratio(col.unique_ratio),
                format_number(col.min_value),
                format_number(col.max_value),
                format_number(col.mean),
            )

        console.print(table)

        # Warnings
        if profile.warnings:
            console.print()
            for warning in profile.warnings:
                console.print(f"[yellow]WARNING:[/yellow] {warning}")

    def format_dataset_profile(self, profile: DatasetProfile) -> None:
        """Display dataset profile as formatted tables.

        Args:
            profile: DatasetProfile to display.
        """
        # Dataset summary
        summary = Text()
        summary.append(f"Dataset: ", style="bold")
        summary.append(f"{profile.name}\n")
        summary.append(f"Files: ", style="bold")
        summary.append(f"{profile.file_count}  ")
        summary.append(f"Total Rows: ", style="bold")
        summary.append(f"{profile.total_rows:,}  ")
        summary.append(f"Total Size: ", style="bold")
        summary.append(f"{format_bytes(profile.total_size_bytes)}")

        if not profile.schema_consistent:
            summary.append(f"\n[yellow]Schema inconsistent![/yellow]")

        console.print(Panel(summary, title="Dataset Profile", border_style="green"))

        # Files table
        table = Table(
            title="Files",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("File", style="bold")
        table.add_column("Format")
        table.add_column("Size", justify="right")
        table.add_column("Rows", justify="right")
        table.add_column("Columns", justify="right")
        table.add_column("Duration", justify="right")

        for file_profile in profile.files:
            table.add_row(
                file_profile.file_path.name,
                file_profile.file_format.upper(),
                format_bytes(file_profile.file_size_bytes),
                format_number(file_profile.row_count),
                format_number(file_profile.column_count),
                f"{file_profile.duration_seconds:.2f}s",
            )

        console.print(table)

        # Schema drift details
        if profile.schema_drift_details:
            console.print()
            console.print("[bold yellow]Schema Drift Details:[/bold yellow]")
            for detail in profile.schema_drift_details:
                console.print(f"  - {detail}")

    def format_grouping_result(self, result: GroupingResult) -> None:
        """Display grouping result as a formatted table.

        Args:
            result: GroupingResult to display.
        """
        # Summary
        summary = Text()
        summary.append(f"Group By: ", style="bold")
        summary.append(f"{', '.join(result.columns)}\n")
        summary.append(f"Total Rows: ", style="bold")
        summary.append(f"{result.total_rows:,}  ")
        summary.append(f"Groups: ", style="bold")
        summary.append(f"{result.group_count}")

        if result.skipped:
            summary.append(f"\n[yellow]Skipped: {result.warning}[/yellow]")

        console.print(Panel(summary, title="Grouping Result", border_style="magenta"))

        if result.skipped:
            return

        # Groups table
        table = Table(
            title="Group Counts",
            show_header=True,
            header_style="bold cyan",
        )

        # Add columns for group keys
        for col in result.columns:
            table.add_column(col, style="bold")

        table.add_column("Count", justify="right")
        table.add_column("% of Total", justify="right")

        # Add basic stats columns if present
        if result.groups and result.groups[0].basic_stats:
            stats_cols = list(result.groups[0].basic_stats.keys())
            for col in stats_cols:
                table.add_column(f"{col} (min)", justify="right")
                table.add_column(f"{col} (max)", justify="right")
                table.add_column(f"{col} (mean)", justify="right")
        else:
            stats_cols = []

        for group in result.groups:
            row: list[str] = []

            # Key values
            for col in result.columns:
                val = group.key.get(col)
                row.append(str(val) if val is not None else "(null)")

            # Count and percentage
            row.append(format_number(group.row_count))
            pct = (group.row_count / result.total_rows * 100) if result.total_rows > 0 else 0
            row.append(f"{pct:.1f}%")

            # Basic stats
            if stats_cols and group.basic_stats:
                for col in stats_cols:
                    stats = group.basic_stats.get(col, {})
                    row.append(format_number(stats.get("min")))
                    row.append(format_number(stats.get("max")))
                    row.append(format_number(stats.get("mean")))

            table.add_row(*row)

        console.print(table)

    def format_relationship_graph(self, graph: RelationshipGraph) -> None:
        """Display relationship graph as formatted tables.

        Args:
            graph: RelationshipGraph to display.
        """
        # Summary
        summary = Text()
        summary.append(f"Entities: ", style="bold")
        summary.append(f"{len(graph.entities)}  ")
        summary.append(f"Relationships: ", style="bold")
        summary.append(f"{len(graph.relationships)}")

        console.print(Panel(summary, title="Relationship Discovery", border_style="cyan"))

        # Entities table
        if graph.entities:
            entity_table = Table(
                title="Entities",
                show_header=True,
                header_style="bold cyan",
            )
            entity_table.add_column("Entity", style="bold")
            entity_table.add_column("File")
            entity_table.add_column("Primary Key(s)")
            entity_table.add_column("Attributes")

            for entity in graph.entities:
                pk_cols = ", ".join(entity.primary_key_columns) if entity.primary_key_columns else "-"
                attr_count = len(entity.attribute_columns)
                entity_table.add_row(
                    entity.name,
                    entity.file_path.name,
                    pk_cols,
                    f"{attr_count} columns",
                )

            console.print(entity_table)

        # Relationships table
        if graph.relationships:
            rel_table = Table(
                title="Relationships",
                show_header=True,
                header_style="bold cyan",
            )
            rel_table.add_column("Parent", style="bold")
            rel_table.add_column("Parent Column")
            rel_table.add_column("Child", style="bold")
            rel_table.add_column("Child Column")
            rel_table.add_column("Type")
            rel_table.add_column("Confidence", justify="right")
            rel_table.add_column("Source")

            for rel in graph.relationships:
                rel_table.add_row(
                    rel.parent_file.stem,
                    rel.parent_column,
                    rel.child_file.stem,
                    rel.child_column,
                    rel.relationship_type.value.replace("_", " ").title(),
                    f"{rel.confidence:.0%}",
                    "Hint" if rel.is_hint else "Detected",
                )

            console.print(rel_table)

        # Mermaid diagram
        if graph.relationships:
            console.print()
            console.print("[bold]Entity-Relationship Diagram (Mermaid):[/bold]")
            mermaid = graph.to_mermaid()
            console.print(Panel(mermaid, title="Mermaid ER Diagram", border_style="dim"))


class JSONFormatter:
    """Formatter for JSON output."""

    def __init__(self, pretty: bool = True) -> None:
        """Initialize JSON formatter.

        Args:
            pretty: Whether to use pretty-printing (indentation).
        """
        self.pretty = pretty
        self.indent = 2 if pretty else None

    def format_file_profile(self, profile: FileProfile) -> str:
        """Format file profile as JSON string.

        Args:
            profile: FileProfile to format.

        Returns:
            JSON string.
        """
        return json.dumps(profile.to_dict(), indent=self.indent, default=str)

    def format_dataset_profile(self, profile: DatasetProfile) -> str:
        """Format dataset profile as JSON string.

        Args:
            profile: DatasetProfile to format.

        Returns:
            JSON string.
        """
        return json.dumps(profile.to_dict(), indent=self.indent, default=str)

    def format_grouping_result(self, result: GroupingResult) -> str:
        """Format grouping result as JSON string.

        Args:
            result: GroupingResult to format.

        Returns:
            JSON string.
        """
        return json.dumps(result.to_dict(), indent=self.indent, default=str)


class HTMLFormatter:
    """Formatter for HTML output."""

    def format_file_profile(self, profile: FileProfile) -> str:
        """Format file profile as HTML.

        Args:
            profile: FileProfile to format.

        Returns:
            HTML string.
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>File Profile: {profile.file_path.name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary-item {{ margin: 5px 0; }}
        .label {{ font-weight: bold; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th {{ background: #4a90d9; color: white; padding: 10px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #f1f1f1; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin-top: 20px; }}
        .number {{ text-align: right; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>File Profile</h1>
    <div class="summary">
        <div class="summary-item"><span class="label">File:</span> {profile.file_path}</div>
        <div class="summary-item"><span class="label">Format:</span> {profile.file_format.upper()}</div>
        <div class="summary-item"><span class="label">Size:</span> {format_bytes(profile.file_size_bytes)}</div>
        <div class="summary-item"><span class="label">Rows:</span> {profile.row_count:,}</div>
        <div class="summary-item"><span class="label">Columns:</span> {profile.column_count}</div>
        <div class="summary-item"><span class="label">Profiled at:</span> {profile.profiled_at}</div>
    </div>

    <h2>Column Statistics</h2>
    <table>
        <tr>
            <th>Column</th>
            <th>Type</th>
            <th>Count</th>
            <th>Nulls</th>
            <th>Null %</th>
            <th>Unique</th>
            <th>Unique %</th>
            <th>Min</th>
            <th>Max</th>
            <th>Mean</th>
        </tr>
"""
        for col in profile.columns:
            html += f"""        <tr>
            <td>{col.name}</td>
            <td>{col.dtype.value}</td>
            <td class="number">{col.count:,}</td>
            <td class="number">{col.null_count:,}</td>
            <td class="number">{format_ratio(col.null_ratio)}</td>
            <td class="number">{col.unique_count:,}</td>
            <td class="number">{format_ratio(col.unique_ratio)}</td>
            <td class="number">{format_number(col.min_value)}</td>
            <td class="number">{format_number(col.max_value)}</td>
            <td class="number">{format_number(col.mean)}</td>
        </tr>
"""

        html += """    </table>
"""

        if profile.warnings:
            html += """    <div class="warning">
        <strong>Warnings:</strong>
        <ul>
"""
            for warning in profile.warnings:
                html += f"            <li>{warning}</li>\n"
            html += """        </ul>
    </div>
"""

        html += """</body>
</html>
"""
        return html

    def format_dataset_profile(self, profile: DatasetProfile) -> str:
        """Format dataset profile as HTML.

        Args:
            profile: DatasetProfile to format.

        Returns:
            HTML string.
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dataset Profile: {profile.name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary-item {{ margin: 5px 0; }}
        .label {{ font-weight: bold; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th {{ background: #28a745; color: white; padding: 10px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #f1f1f1; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin-top: 20px; }}
        .number {{ text-align: right; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>Dataset Profile: {profile.name}</h1>
    <div class="summary">
        <div class="summary-item"><span class="label">Files:</span> {profile.file_count}</div>
        <div class="summary-item"><span class="label">Total Rows:</span> {profile.total_rows:,}</div>
        <div class="summary-item"><span class="label">Total Size:</span> {format_bytes(profile.total_size_bytes)}</div>
        <div class="summary-item"><span class="label">Schema Consistent:</span> {'Yes' if profile.schema_consistent else 'No'}</div>
        <div class="summary-item"><span class="label">Profiled at:</span> {profile.profiled_at}</div>
    </div>

    <h2>Files</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Format</th>
            <th>Size</th>
            <th>Rows</th>
            <th>Columns</th>
            <th>Duration</th>
        </tr>
"""
        for file_profile in profile.files:
            html += f"""        <tr>
            <td>{file_profile.file_path.name}</td>
            <td>{file_profile.file_format.upper()}</td>
            <td class="number">{format_bytes(file_profile.file_size_bytes)}</td>
            <td class="number">{file_profile.row_count:,}</td>
            <td class="number">{file_profile.column_count}</td>
            <td class="number">{file_profile.duration_seconds:.2f}s</td>
        </tr>
"""

        html += """    </table>
"""

        if profile.schema_drift_details:
            html += """    <div class="warning">
        <strong>Schema Drift:</strong>
        <ul>
"""
            for detail in profile.schema_drift_details:
                html += f"            <li>{detail}</li>\n"
            html += """        </ul>
    </div>
"""

        html += """</body>
</html>
"""
        return html

    def format_grouping_result(self, result: GroupingResult) -> str:
        """Format grouping result as HTML.

        Args:
            result: GroupingResult to format.

        Returns:
            HTML string.
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Grouping Result</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary-item {{ margin: 5px 0; }}
        .label {{ font-weight: bold; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th {{ background: #9c27b0; color: white; padding: 10px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #f1f1f1; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin-top: 20px; }}
        .number {{ text-align: right; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>Grouping Result</h1>
    <div class="summary">
        <div class="summary-item"><span class="label">Group By:</span> {', '.join(result.columns)}</div>
        <div class="summary-item"><span class="label">Total Rows:</span> {result.total_rows:,}</div>
        <div class="summary-item"><span class="label">Groups:</span> {result.group_count}</div>
    </div>
"""

        if result.skipped:
            html += f"""    <div class="warning">
        <strong>Skipped:</strong> {result.warning}
    </div>
</body>
</html>
"""
            return html

        html += """    <h2>Group Counts</h2>
    <table>
        <tr>
"""
        for col in result.columns:
            html += f"            <th>{col}</th>\n"
        html += """            <th>Count</th>
            <th>% of Total</th>
        </tr>
"""

        for group in result.groups:
            html += "        <tr>\n"
            for col in result.columns:
                val = group.key.get(col)
                html += f"            <td>{val if val is not None else '(null)'}</td>\n"

            pct = (group.row_count / result.total_rows * 100) if result.total_rows > 0 else 0
            html += f"""            <td class="number">{group.row_count:,}</td>
            <td class="number">{pct:.1f}%</td>
        </tr>
"""

        html += """    </table>
</body>
</html>
"""
        return html
