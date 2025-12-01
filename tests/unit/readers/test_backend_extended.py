"""Extended tests for the backend module.

These tests ensure comprehensive coverage of backend selection and conversion.
"""

from typing import Any

import pytest

from data_profiler.readers.backend import (
    Backend,
    get_backend,
    set_backend,
    is_polars_backend,
    is_pandas_backend,
    get_available_backends,
    get_row_count,
    get_column_names,
    get_column,
    to_polars,
    to_pandas,
)


class TestBackendSelection:
    """Test backend selection functionality."""

    def test_get_available_backends(self) -> None:
        """Test getting list of available backends."""
        backends = get_available_backends()

        # At least one backend should be available
        assert len(backends) > 0
        assert all(isinstance(b, Backend) for b in backends)

    def test_set_backend_polars(self, polars_backend: Backend) -> None:
        """Test setting Polars backend."""
        assert is_polars_backend() is True
        assert is_pandas_backend() is False

    def test_set_backend_pandas(self, pandas_backend: Backend) -> None:
        """Test setting Pandas backend."""
        assert is_pandas_backend() is True
        assert is_polars_backend() is False

    def test_set_backend_auto(self) -> None:
        """Test setting backend to AUTO."""
        set_backend(Backend.AUTO)
        # AUTO should pick one of the available backends
        backend = get_backend()
        assert backend in [Backend.POLARS, Backend.PANDAS]
        set_backend(Backend.AUTO)

    def test_set_backend_string(self) -> None:
        """Test setting backend with string value."""
        set_backend("polars")
        assert get_backend() == Backend.POLARS

        set_backend("pandas")
        assert get_backend() == Backend.PANDAS

        set_backend("auto")
        # Reset
        set_backend(Backend.AUTO)

    def test_set_backend_invalid_raises(self) -> None:
        """Test setting invalid backend raises error."""
        with pytest.raises(ValueError):
            set_backend("invalid_backend")


class TestBackendConversion:
    """Test DataFrame conversion between backends."""

    def test_to_polars_from_polars(self, dataframe_polars: Any) -> None:
        """Test converting Polars DataFrame to Polars (no-op)."""
        import polars as pl

        result = to_polars(dataframe_polars)
        assert isinstance(result, pl.DataFrame)

    def test_to_polars_from_pandas(self, dataframe_pandas: Any) -> None:
        """Test converting Pandas DataFrame to Polars."""
        import polars as pl

        result = to_polars(dataframe_pandas)
        assert isinstance(result, pl.DataFrame)
        assert len(result) == len(dataframe_pandas)

    def test_to_pandas_from_pandas(self, dataframe_pandas: Any) -> None:
        """Test converting Pandas DataFrame to Pandas (no-op)."""
        import pandas as pd

        result = to_pandas(dataframe_pandas)
        assert isinstance(result, pd.DataFrame)

    def test_to_pandas_from_polars(self, dataframe_polars: Any) -> None:
        """Test converting Polars DataFrame to Pandas."""
        import pandas as pd

        result = to_pandas(dataframe_polars)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(dataframe_polars)

    def test_to_polars_invalid_raises(self) -> None:
        """Test converting invalid type to Polars raises error."""
        with pytest.raises(ValueError):
            to_polars([1, 2, 3])  # type: ignore

    def test_to_pandas_invalid_raises(self) -> None:
        """Test converting invalid type to Pandas raises error."""
        with pytest.raises(ValueError):
            to_pandas([1, 2, 3])  # type: ignore


class TestBackendUtilities:
    """Test backend utility functions."""

    def test_get_row_count_polars(self, dataframe_polars: Any) -> None:
        """Test get_row_count with Polars DataFrame."""
        count = get_row_count(dataframe_polars)
        assert count == 5

    def test_get_row_count_pandas(self, dataframe_pandas: Any) -> None:
        """Test get_row_count with Pandas DataFrame."""
        count = get_row_count(dataframe_pandas)
        assert count == 5

    def test_get_column_names_polars(self, dataframe_polars: Any) -> None:
        """Test get_column_names with Polars DataFrame."""
        names = get_column_names(dataframe_polars)
        assert "id" in names
        assert "name" in names

    def test_get_column_names_pandas(self, dataframe_pandas: Any) -> None:
        """Test get_column_names with Pandas DataFrame."""
        names = get_column_names(dataframe_pandas)
        assert "id" in names
        assert "name" in names

    def test_get_column_polars(self, dataframe_polars: Any) -> None:
        """Test get_column with Polars DataFrame."""
        import polars as pl

        column = get_column(dataframe_polars, "id")
        assert isinstance(column, pl.Series)

    def test_get_column_pandas(self, dataframe_pandas: Any) -> None:
        """Test get_column with Pandas DataFrame."""
        import pandas as pd

        column = get_column(dataframe_pandas, "id")
        assert isinstance(column, pd.Series)


class TestBackendEnumeration:
    """Test Backend enum."""

    def test_backend_values(self) -> None:
        """Test Backend enum values."""
        assert Backend.POLARS.value == "polars"
        assert Backend.PANDAS.value == "pandas"
        assert Backend.AUTO.value == "auto"

    def test_backend_is_str_enum(self) -> None:
        """Test Backend inherits from str, allowing string comparison."""
        # Backend is a str Enum, so values are equal to their string form
        assert Backend.POLARS == "polars"
        assert Backend.PANDAS == "pandas"
