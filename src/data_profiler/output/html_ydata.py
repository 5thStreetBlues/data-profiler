"""ydata-profiling HTML output integration.

This module provides integration with ydata-profiling (formerly pandas-profiling)
for generating comprehensive HTML profile reports.

Note: ydata-profiling is an optional dependency.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

from data_profiler.output.base import BaseFormatter
from data_profiler.output.html_formatter import HTMLFormatter

if TYPE_CHECKING:
    from data_profiler.models.profile import FileProfile, DatasetProfile
    from data_profiler.models.grouping import GroupingResult


def is_ydata_available() -> bool:
    """Check if ydata-profiling is installed.

    Returns:
        True if ydata-profiling is available, False otherwise.
    """
    try:
        import ydata_profiling  # noqa: F401
        return True
    except ImportError:
        return False


class YDataHTMLFormatter(BaseFormatter):
    """Formatter using ydata-profiling for comprehensive HTML reports.

    This formatter uses ydata-profiling to generate detailed HTML reports
    with interactive visualizations, correlation matrices, and more.

    Note: Falls back to standard HTMLFormatter if ydata-profiling is not installed.
    """

    def __init__(
        self,
        minimal: bool = False,
        explorative: bool = False,
        dark_mode: bool = False,
        title: str | None = None,
    ) -> None:
        """Initialize ydata HTML formatter.

        Args:
            minimal: Generate minimal report (faster).
            explorative: Generate explorative report (more visualizations).
            dark_mode: Use dark mode theme.
            title: Custom title for the report.
        """
        self.minimal = minimal
        self.explorative = explorative
        self.dark_mode = dark_mode
        self.title = title
        self._fallback = HTMLFormatter()

    def _get_dataframe(self, profile: FileProfile) -> Any:
        """Load file as DataFrame for ydata-profiling.

        Args:
            profile: FileProfile with file path to load.

        Returns:
            pandas DataFrame.
        """
        import pandas as pd

        path = profile.file_path
        suffix = path.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(path)
        elif suffix == ".parquet":
            return pd.read_parquet(path)
        elif suffix in (".json", ".jsonl"):
            if suffix == ".jsonl":
                return pd.read_json(path, lines=True)
            return pd.read_json(path)
        else:
            raise ValueError(f"Unsupported file format for ydata: {suffix}")

    def format_file_profile(self, profile: FileProfile) -> str:
        """Format file profile as HTML using ydata-profiling.

        Args:
            profile: FileProfile to format.

        Returns:
            HTML string.
        """
        if not is_ydata_available():
            warnings.warn(
                "ydata-profiling not installed, falling back to standard HTML formatter. "
                "Install with: pip install ydata-profiling",
                UserWarning,
                stacklevel=2,
            )
            return self._fallback.format_file_profile(profile)

        try:
            from ydata_profiling import ProfileReport

            # Load data
            df = self._get_dataframe(profile)

            # Determine mode
            if self.minimal:
                report = ProfileReport(
                    df,
                    minimal=True,
                    title=self.title or f"Profile: {profile.file_path.name}",
                    dark_mode=self.dark_mode,
                )
            elif self.explorative:
                report = ProfileReport(
                    df,
                    explorative=True,
                    title=self.title or f"Profile: {profile.file_path.name}",
                    dark_mode=self.dark_mode,
                )
            else:
                report = ProfileReport(
                    df,
                    title=self.title or f"Profile: {profile.file_path.name}",
                    dark_mode=self.dark_mode,
                )

            return report.to_html()

        except Exception as e:
            warnings.warn(
                f"ydata-profiling failed: {e}. Falling back to standard HTML formatter.",
                UserWarning,
                stacklevel=2,
            )
            return self._fallback.format_file_profile(profile)

    def format_dataset_profile(self, profile: DatasetProfile) -> str:
        """Format dataset profile as HTML.

        Note: ydata-profiling doesn't natively support multi-file datasets,
        so this falls back to standard HTML formatter.

        Args:
            profile: DatasetProfile to format.

        Returns:
            HTML string.
        """
        # ydata-profiling works on single DataFrames, not datasets
        # Fall back to standard formatter for datasets
        return self._fallback.format_dataset_profile(profile)

    def format_grouping_result(self, result: GroupingResult) -> str:
        """Format grouping result as HTML.

        Note: ydata-profiling doesn't support grouping results,
        so this falls back to standard HTML formatter.

        Args:
            result: GroupingResult to format.

        Returns:
            HTML string.
        """
        return self._fallback.format_grouping_result(result)

    def write_file_profile(
        self,
        profile: FileProfile,
        path: Path,
    ) -> None:
        """Format and write a file profile to a file.

        Uses ydata-profiling's native file writing when available
        for better performance.

        Args:
            profile: FileProfile to format and write.
            path: Output file path.
        """
        if not is_ydata_available():
            super().write_file_profile(profile, path)
            return

        try:
            from ydata_profiling import ProfileReport

            df = self._get_dataframe(profile)

            if self.minimal:
                report = ProfileReport(
                    df,
                    minimal=True,
                    title=self.title or f"Profile: {profile.file_path.name}",
                    dark_mode=self.dark_mode,
                )
            elif self.explorative:
                report = ProfileReport(
                    df,
                    explorative=True,
                    title=self.title or f"Profile: {profile.file_path.name}",
                    dark_mode=self.dark_mode,
                )
            else:
                report = ProfileReport(
                    df,
                    title=self.title or f"Profile: {profile.file_path.name}",
                    dark_mode=self.dark_mode,
                )

            # Use native to_file for efficiency
            report.to_file(path)

        except Exception:
            # Fall back to base implementation
            super().write_file_profile(profile, path)


def create_ydata_report(
    file_path: Path,
    output_path: Path | None = None,
    minimal: bool = False,
    explorative: bool = False,
    title: str | None = None,
) -> str:
    """Convenience function to create ydata-profiling report.

    Args:
        file_path: Path to data file.
        output_path: Optional output file path.
        minimal: Generate minimal report.
        explorative: Generate explorative report.
        title: Custom report title.

    Returns:
        HTML string of the report.

    Raises:
        ImportError: If ydata-profiling is not installed.
    """
    if not is_ydata_available():
        raise ImportError(
            "ydata-profiling is required for this feature. "
            "Install with: pip install ydata-profiling"
        )

    import pandas as pd
    from ydata_profiling import ProfileReport

    # Load data
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(file_path)
    elif suffix == ".parquet":
        df = pd.read_parquet(file_path)
    elif suffix in (".json", ".jsonl"):
        df = pd.read_json(file_path, lines=(suffix == ".jsonl"))
    else:
        raise ValueError(f"Unsupported file format: {suffix}")

    # Create report
    report = ProfileReport(
        df,
        minimal=minimal,
        explorative=explorative,
        title=title or f"Profile: {file_path.name}",
    )

    if output_path:
        report.to_file(output_path)

    return report.to_html()
