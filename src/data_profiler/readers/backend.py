"""Backend selection and abstraction for data-profiler.

This module provides abstraction over DataFrame libraries (Polars/Pandas)
with automatic backend detection and selection.

The preferred backend is Polars for performance, with Pandas as fallback.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl

# Module-level backend state
_current_backend: Backend | None = None
_polars_available: bool | None = None
_pandas_available: bool | None = None


class Backend(str, Enum):
    """Available DataFrame backends."""

    POLARS = "polars"
    PANDAS = "pandas"
    AUTO = "auto"


def _check_polars_available() -> bool:
    """Check if Polars is available."""
    global _polars_available
    if _polars_available is None:
        try:
            import polars  # noqa: F401

            _polars_available = True
        except ImportError:
            _polars_available = False
    return _polars_available


def _check_pandas_available() -> bool:
    """Check if Pandas is available."""
    global _pandas_available
    if _pandas_available is None:
        try:
            import pandas  # noqa: F401

            _pandas_available = True
        except ImportError:
            _pandas_available = False
    return _pandas_available


def get_available_backends() -> list[Backend]:
    """Get list of available backends.

    Returns:
        List of available Backend enum values.
    """
    available = []
    if _check_polars_available():
        available.append(Backend.POLARS)
    if _check_pandas_available():
        available.append(Backend.PANDAS)
    return available


def get_backend() -> Backend:
    """Get the current DataFrame backend.

    Returns:
        Current Backend (POLARS or PANDAS).

    Raises:
        RuntimeError: If no backend is available.
    """
    global _current_backend

    if _current_backend is None or _current_backend == Backend.AUTO:
        # Auto-detect: prefer Polars, fall back to Pandas
        if _check_polars_available():
            _current_backend = Backend.POLARS
        elif _check_pandas_available():
            _current_backend = Backend.PANDAS
        else:
            msg = (
                "No DataFrame backend available. "
                "Install polars (recommended) or pandas."
            )
            raise RuntimeError(msg)

    return _current_backend


def set_backend(backend: Backend | str) -> None:
    """Set the DataFrame backend preference.

    Args:
        backend: Backend to use (POLARS, PANDAS, or AUTO).

    Raises:
        ValueError: If the specified backend is not available.
    """
    global _current_backend

    if isinstance(backend, str):
        backend = Backend(backend.lower())

    if backend == Backend.AUTO:
        _current_backend = Backend.AUTO
        return

    if backend == Backend.POLARS and not _check_polars_available():
        msg = "Polars backend requested but polars is not installed."
        raise ValueError(msg)

    if backend == Backend.PANDAS and not _check_pandas_available():
        msg = "Pandas backend requested but pandas is not installed."
        raise ValueError(msg)

    _current_backend = backend


def is_polars_backend() -> bool:
    """Check if the current backend is Polars.

    Returns:
        True if using Polars backend.
    """
    return get_backend() == Backend.POLARS


def is_pandas_backend() -> bool:
    """Check if the current backend is Pandas.

    Returns:
        True if using Pandas backend.
    """
    return get_backend() == Backend.PANDAS


def reset_backend() -> None:
    """Reset the backend to auto-detect mode.

    This is useful for testing to ensure clean state between tests.
    """
    global _current_backend
    _current_backend = None


def is_polars_dataframe(df: Any) -> bool:
    """Check if a DataFrame is a Polars DataFrame.

    This checks the actual object type, NOT the global backend setting.

    Args:
        df: DataFrame to check.

    Returns:
        True if df is a Polars DataFrame.
    """
    return type(df).__module__.startswith("polars")


def is_polars_series(series: Any) -> bool:
    """Check if a Series is a Polars Series.

    This checks the actual object type, NOT the global backend setting.

    Args:
        series: Series to check.

    Returns:
        True if series is a Polars Series.
    """
    return type(series).__module__.startswith("polars")


# Type aliases for DataFrame abstractions
# These provide type hints that work with both backends


class DataFrame:
    """Type alias for DataFrame (Polars or Pandas).

    This is a placeholder for type hints. Actual DataFrames
    will be either polars.DataFrame or pandas.DataFrame.
    """

    pass


class LazyFrame:
    """Type alias for LazyFrame (Polars only).

    Polars LazyFrame enables query optimization and streaming.
    Not available with Pandas backend.
    """

    pass


class Series:
    """Type alias for Series (Polars or Pandas).

    This is a placeholder for type hints. Actual Series
    will be either polars.Series or pandas.Series.
    """

    pass


def to_polars(df: Any) -> pl.DataFrame:
    """Convert a DataFrame to Polars format.

    Args:
        df: DataFrame to convert (Polars or Pandas).

    Returns:
        Polars DataFrame.

    Raises:
        ValueError: If conversion is not possible.
    """
    import polars as pl

    if isinstance(df, pl.DataFrame):
        return df

    if _check_pandas_available():
        import pandas as pd

        if isinstance(df, pd.DataFrame):
            return pl.from_pandas(df)

    msg = f"Cannot convert {type(df).__name__} to Polars DataFrame."
    raise ValueError(msg)


def to_pandas(df: Any) -> pd.DataFrame:
    """Convert a DataFrame to Pandas format.

    Args:
        df: DataFrame to convert (Polars or Pandas).

    Returns:
        Pandas DataFrame.

    Raises:
        ValueError: If conversion is not possible.
    """
    import pandas as pd

    if isinstance(df, pd.DataFrame):
        return df

    if _check_polars_available():
        import polars as pl

        if isinstance(df, pl.DataFrame):
            return df.to_pandas()

    msg = f"Cannot convert {type(df).__name__} to Pandas DataFrame."
    raise ValueError(msg)


def get_row_count(df: Any) -> int:
    """Get row count from a DataFrame.

    Args:
        df: DataFrame (Polars or Pandas).

    Returns:
        Number of rows.
    """
    if hasattr(df, "height"):
        # Polars
        return df.height
    if hasattr(df, "shape"):
        # Pandas
        return df.shape[0]
    return len(df)


def get_column_names(df: Any) -> list[str]:
    """Get column names from a DataFrame.

    Args:
        df: DataFrame (Polars or Pandas).

    Returns:
        List of column names.
    """
    if hasattr(df, "columns"):
        return list(df.columns)
    return []


def get_column(df: Any, name: str) -> Any:
    """Get a column/series from a DataFrame.

    Args:
        df: DataFrame (Polars or Pandas).
        name: Column name.

    Returns:
        Series/column data.
    """
    return df[name]
