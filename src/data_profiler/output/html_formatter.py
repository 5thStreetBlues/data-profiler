"""HTML output formatter.

This module provides HTML formatting for profiling results,
generating standalone HTML reports with styling.
"""

from __future__ import annotations

from typing import Any

from data_profiler.models.profile import FileProfile, DatasetProfile, ColumnProfile
from data_profiler.models.grouping import GroupingResult
from data_profiler.models.relationships import RelationshipGraph
from data_profiler.output.base import BaseFormatter


def _format_bytes(size: int) -> str:
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


def _format_number(value: Any) -> str:
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


def _format_ratio(value: float | None) -> str:
    """Format a ratio as percentage.

    Args:
        value: Ratio between 0 and 1.

    Returns:
        Formatted percentage string.
    """
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


_HTML_STYLES = """
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .summary {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .summary-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .summary-label {
            font-size: 0.85em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .summary-value {
            font-size: 1.4em;
            font-weight: 600;
            color: #2c3e50;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        th {
            background: #3498db;
            color: white;
            font-weight: 600;
            padding: 12px 15px;
            text-align: left;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:nth-child(even) { background: #f8f9fa; }
        tr:hover { background: #e8f4f8; }
        .number { text-align: right; font-family: 'SF Mono', Monaco, monospace; }
        .type-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .type-string { background: #e8f5e9; color: #2e7d32; }
        .type-integer, .type-float { background: #e3f2fd; color: #1565c0; }
        .type-datetime, .type-date { background: #fff3e0; color: #ef6c00; }
        .type-boolean { background: #f3e5f5; color: #7b1fa2; }
        .type-categorical { background: #fce4ec; color: #c2185b; }
        .type-unknown { background: #eceff1; color: #546e7a; }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }
        .warning-title { font-weight: 600; color: #856404; }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
            text-align: center;
        }
    </style>
"""


class HTMLFormatter(BaseFormatter):
    """Formatter for HTML output.

    Generates standalone HTML reports with embedded CSS styling.
    """

    def _get_type_class(self, dtype: str) -> str:
        """Get CSS class for column type badge.

        Args:
            dtype: Column data type.

        Returns:
            CSS class name.
        """
        dtype_lower = dtype.lower()
        if dtype_lower in ("string", "text"):
            return "type-string"
        if dtype_lower in ("integer", "int", "float", "numeric", "number"):
            return "type-integer"
        if dtype_lower in ("datetime", "date", "time", "timestamp"):
            return "type-datetime"
        if dtype_lower == "boolean":
            return "type-boolean"
        if dtype_lower == "categorical":
            return "type-categorical"
        return "type-unknown"

    def format_file_profile(self, profile: FileProfile) -> str:
        """Format file profile as HTML.

        Args:
            profile: FileProfile to format.

        Returns:
            HTML string.
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile: {profile.file_path.name}</title>
    {_HTML_STYLES}
</head>
<body>
    <h1>File Profile</h1>

    <div class="summary">
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">File</div>
                <div class="summary-value">{profile.file_path.name}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Format</div>
                <div class="summary-value">{profile.file_format.upper()}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Size</div>
                <div class="summary-value">{_format_bytes(profile.file_size_bytes)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Rows</div>
                <div class="summary-value">{profile.row_count:,}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Columns</div>
                <div class="summary-value">{profile.column_count}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Profiled At</div>
                <div class="summary-value" style="font-size: 1em;">{profile.profiled_at.strftime('%Y-%m-%d %H:%M')}</div>
            </div>
        </div>
    </div>

    <h2>Column Statistics</h2>
    <table>
        <thead>
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
        </thead>
        <tbody>
"""
        for col in profile.columns:
            type_class = self._get_type_class(col.dtype.value)
            html += f"""            <tr>
                <td><strong>{col.name}</strong></td>
                <td><span class="type-badge {type_class}">{col.dtype.value}</span></td>
                <td class="number">{col.count:,}</td>
                <td class="number">{col.null_count:,}</td>
                <td class="number">{_format_ratio(col.null_ratio)}</td>
                <td class="number">{col.unique_count:,}</td>
                <td class="number">{_format_ratio(col.unique_ratio)}</td>
                <td class="number">{_format_number(col.min_value)}</td>
                <td class="number">{_format_number(col.max_value)}</td>
                <td class="number">{_format_number(col.mean)}</td>
            </tr>
"""

        html += """        </tbody>
    </table>
"""

        if profile.warnings:
            html += """    <div class="warning">
        <div class="warning-title">Warnings</div>
        <ul>
"""
            for warning in profile.warnings:
                html += f"            <li>{warning}</li>\n"
            html += """        </ul>
    </div>
"""

        html += f"""    <div class="footer">
        Generated by data-profiler | Duration: {profile.duration_seconds:.2f}s
    </div>
</body>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dataset Profile: {profile.name}</title>
    {_HTML_STYLES}
</head>
<body>
    <h1>Dataset Profile: {profile.name}</h1>

    <div class="summary">
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">Files</div>
                <div class="summary-value">{profile.file_count}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Rows</div>
                <div class="summary-value">{profile.total_rows:,}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Size</div>
                <div class="summary-value">{_format_bytes(profile.total_size_bytes)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Schema Consistent</div>
                <div class="summary-value">{'Yes' if profile.schema_consistent else 'No'}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Profiled At</div>
                <div class="summary-value" style="font-size: 1em;">{profile.profiled_at.strftime('%Y-%m-%d %H:%M')}</div>
            </div>
        </div>
    </div>

    <h2>Files</h2>
    <table>
        <thead>
            <tr>
                <th>File</th>
                <th>Format</th>
                <th>Size</th>
                <th>Rows</th>
                <th>Columns</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody>
"""
        for fp in profile.files:
            html += f"""            <tr>
                <td><strong>{fp.file_path.name}</strong></td>
                <td>{fp.file_format.upper()}</td>
                <td class="number">{_format_bytes(fp.file_size_bytes)}</td>
                <td class="number">{fp.row_count:,}</td>
                <td class="number">{fp.column_count}</td>
                <td class="number">{fp.duration_seconds:.2f}s</td>
            </tr>
"""

        html += """        </tbody>
    </table>
"""

        if profile.schema_drift_details:
            html += """    <div class="warning">
        <div class="warning-title">Schema Drift Detected</div>
        <ul>
"""
            for detail in profile.schema_drift_details:
                html += f"            <li>{detail}</li>\n"
            html += """        </ul>
    </div>
"""

        html += """    <div class="footer">
        Generated by data-profiler
    </div>
</body>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grouping Result</title>
    {_HTML_STYLES}
</head>
<body>
    <h1>Grouping Result</h1>

    <div class="summary">
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">Group By</div>
                <div class="summary-value" style="font-size: 1em;">{', '.join(result.columns)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Rows</div>
                <div class="summary-value">{result.total_rows:,}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Groups</div>
                <div class="summary-value">{result.group_count}</div>
            </div>
        </div>
    </div>
"""

        if result.skipped:
            html += f"""    <div class="warning">
        <div class="warning-title">Skipped</div>
        <p>{result.warning}</p>
    </div>
</body>
</html>
"""
            return html

        html += """    <h2>Group Counts</h2>
    <table>
        <thead>
            <tr>
"""
        for col in result.columns:
            html += f"                <th>{col}</th>\n"
        html += """                <th>Count</th>
                <th>% of Total</th>
            </tr>
        </thead>
        <tbody>
"""

        for group in result.groups:
            html += "            <tr>\n"
            for col in result.columns:
                val = group.key.get(col)
                html += f"                <td>{val if val is not None else '(null)'}</td>\n"

            pct = (group.row_count / result.total_rows * 100) if result.total_rows > 0 else 0
            html += f"""                <td class="number">{group.row_count:,}</td>
                <td class="number">{pct:.1f}%</td>
            </tr>
"""

        html += """        </tbody>
    </table>

    <div class="footer">
        Generated by data-profiler
    </div>
</body>
</html>
"""
        return html

    def format_relationship_graph(self, graph: RelationshipGraph) -> str:
        """Format relationship graph as HTML.

        Args:
            graph: RelationshipGraph to format.

        Returns:
            HTML string.
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relationship Discovery</title>
    {_HTML_STYLES}
    <style>
        .mermaid-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        pre.mermaid-code {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>Relationship Discovery</h1>

    <div class="summary">
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">Entities</div>
                <div class="summary-value">{len(graph.entities)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Relationships</div>
                <div class="summary-value">{len(graph.relationships)}</div>
            </div>
        </div>
    </div>
"""

        if graph.entities:
            html += """    <h2>Entities</h2>
    <table>
        <thead>
            <tr>
                <th>Entity</th>
                <th>File</th>
                <th>Primary Key(s)</th>
                <th>Attributes</th>
            </tr>
        </thead>
        <tbody>
"""
            for entity in graph.entities:
                pk_cols = ", ".join(entity.primary_key_columns) if entity.primary_key_columns else "-"
                html += f"""            <tr>
                <td><strong>{entity.name}</strong></td>
                <td>{entity.file_path.name}</td>
                <td>{pk_cols}</td>
                <td>{len(entity.attribute_columns)} columns</td>
            </tr>
"""
            html += """        </tbody>
    </table>
"""

        if graph.relationships:
            html += """    <h2>Relationships</h2>
    <table>
        <thead>
            <tr>
                <th>Parent</th>
                <th>Parent Column</th>
                <th>Child</th>
                <th>Child Column</th>
                <th>Type</th>
                <th>Confidence</th>
                <th>Source</th>
            </tr>
        </thead>
        <tbody>
"""
            for rel in graph.relationships:
                html += f"""            <tr>
                <td><strong>{rel.parent_file.stem}</strong></td>
                <td>{rel.parent_column}</td>
                <td><strong>{rel.child_file.stem}</strong></td>
                <td>{rel.child_column}</td>
                <td>{rel.relationship_type.value.replace('_', ' ').title()}</td>
                <td class="number">{rel.confidence:.0%}</td>
                <td>{'Hint' if rel.is_hint else 'Detected'}</td>
            </tr>
"""
            html += """        </tbody>
    </table>

    <h2>Entity-Relationship Diagram</h2>
    <div class="mermaid-container">
        <pre class="mermaid-code">"""
            html += graph.to_mermaid()
            html += """</pre>
    </div>
"""

        html += """    <div class="footer">
        Generated by data-profiler
    </div>
</body>
</html>
"""
        return html
