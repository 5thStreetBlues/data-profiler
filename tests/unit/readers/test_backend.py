"""Tests for the backend module."""

import pytest

from data_profiler.readers.backend import (
    Backend,
    get_available_backends,
    get_backend,
    set_backend,
    is_polars_backend,
    is_pandas_backend,
    get_row_count,
    get_column_names,
    get_column,
)


class TestBackendSelection:
    """Test backend selection functionality."""

    def test_backend_enum_values(self) -> None:
        """Test Backend enum has expected values."""
        assert Backend.POLARS == "polars"
        assert Backend.PANDAS == "pandas"
        assert Backend.AUTO == "auto"

    def test_get_available_backends(self) -> None:
        """Test getting available backends."""
        backends = get_available_backends()
        assert isinstance(backends, list)
        # At least one backend should be available
        assert len(backends) > 0

    def test_get_backend_returns_valid_backend(self) -> None:
        """Test get_backend returns a valid backend."""
        backend = get_backend()
        assert backend in [Backend.POLARS, Backend.PANDAS]

    def test_set_backend_auto(self) -> None:
        """Test setting backend to auto."""
        set_backend(Backend.AUTO)
        # Should resolve to an actual backend
        backend = get_backend()
        assert backend in [Backend.POLARS, Backend.PANDAS]

    def test_set_backend_string(self) -> None:
        """Test setting backend with string value."""
        available = get_available_backends()
        if Backend.POLARS in available:
            set_backend("polars")
            assert get_backend() == Backend.POLARS
        elif Backend.PANDAS in available:
            set_backend("pandas")
            assert get_backend() == Backend.PANDAS

    def test_set_backend_unavailable_raises(self) -> None:
        """Test setting unavailable backend raises error."""
        available = get_available_backends()
        if Backend.POLARS not in available:
            with pytest.raises(ValueError, match="polars is not installed"):
                set_backend(Backend.POLARS)
        elif Backend.PANDAS not in available:
            with pytest.raises(ValueError, match="pandas is not installed"):
                set_backend(Backend.PANDAS)

    def test_is_polars_backend(self) -> None:
        """Test is_polars_backend function."""
        available = get_available_backends()
        if Backend.POLARS in available:
            set_backend(Backend.POLARS)
            assert is_polars_backend() is True
            assert is_pandas_backend() is False

    def test_is_pandas_backend(self) -> None:
        """Test is_pandas_backend function."""
        available = get_available_backends()
        if Backend.PANDAS in available:
            set_backend(Backend.PANDAS)
            assert is_pandas_backend() is True
            assert is_polars_backend() is False


class TestDataFrameHelpers:
    """Test DataFrame helper functions."""

    def test_get_row_count(self, sample_dataframe) -> None:
        """Test getting row count from DataFrame."""
        count = get_row_count(sample_dataframe)
        assert count == 5

    def test_get_column_names(self, sample_dataframe) -> None:
        """Test getting column names from DataFrame."""
        names = get_column_names(sample_dataframe)
        assert "id" in names
        assert "name" in names
        assert "amount" in names
        assert "is_active" in names

    def test_get_column(self, sample_dataframe) -> None:
        """Test getting a column from DataFrame."""
        col = get_column(sample_dataframe, "name")
        assert col is not None
