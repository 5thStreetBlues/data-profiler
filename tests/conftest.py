"""Pytest configuration and fixtures for data-profiler tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def reset_backend_after_test():
    """Reset backend to auto-detect mode after each test.

    This prevents backend state pollution between tests.
    Tests that set_backend("pandas") would otherwise affect subsequent tests.
    """
    yield  # Let test run

    # Reset after test completes
    from data_profiler.readers.backend import reset_backend

    reset_backend()


@pytest.fixture
def fixtures_dir() -> Path:
    """Get path to test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def sample_csv_path(fixtures_dir: Path) -> Path:
    """Get path to sample CSV file."""
    return fixtures_dir / "sample.csv"


@pytest.fixture
def sample_jsonl_path(fixtures_dir: Path) -> Path:
    """Get path to sample JSONL file."""
    return fixtures_dir / "sample.jsonl"


@pytest.fixture
def sample_parquet_path(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Create and return path to sample Parquet file."""
    # Create a parquet file from CSV for testing
    try:
        import polars as pl

        csv_path = fixtures_dir / "sample.csv"
        df = pl.read_csv(csv_path)
        parquet_path = tmp_path / "sample.parquet"
        df.write_parquet(parquet_path)
        return parquet_path
    except ImportError:
        try:
            import pandas as pd

            csv_path = fixtures_dir / "sample.csv"
            df = pd.read_csv(csv_path)
            parquet_path = tmp_path / "sample.parquet"
            df.to_parquet(parquet_path)
            return parquet_path
        except ImportError:
            pytest.skip("Neither polars nor pandas available for parquet creation")


@pytest.fixture
def sample_dataframe() -> Any:
    """Create a sample DataFrame for testing."""
    try:
        import polars as pl

        return pl.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "amount": [100.5, 200.75, 150.0, 300.25, 250.0],
                "is_active": [True, False, True, True, False],
            }
        )
    except ImportError:
        import pandas as pd

        return pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "amount": [100.5, 200.75, 150.0, 300.25, 250.0],
                "is_active": [True, False, True, True, False],
            }
        )


@pytest.fixture
def sample_numeric_series() -> Any:
    """Create a sample numeric series for testing."""
    try:
        import polars as pl

        return pl.Series("amount", [100.5, 200.75, 150.0, 300.25, 250.0, None])
    except ImportError:
        import pandas as pd

        return pd.Series([100.5, 200.75, 150.0, 300.25, 250.0, None], name="amount")


@pytest.fixture
def sample_string_series() -> Any:
    """Create a sample string series for testing."""
    try:
        import polars as pl

        return pl.Series("name", ["Alice", "Bob", "Charlie", "Diana", "Eve", None])
    except ImportError:
        import pandas as pd

        return pd.Series(["Alice", "Bob", "Charlie", "Diana", "Eve", None], name="name")


@pytest.fixture
def sample_datetime_series() -> Any:
    """Create a sample datetime series for testing."""
    from datetime import datetime

    try:
        import polars as pl

        return pl.Series(
            "created_at",
            [
                datetime(2024, 1, 15),
                datetime(2024, 2, 20),
                datetime(2024, 3, 10),
                datetime(2024, 4, 5),
                None,
            ],
        )
    except ImportError:
        import pandas as pd

        return pd.Series(
            [
                datetime(2024, 1, 15),
                datetime(2024, 2, 20),
                datetime(2024, 3, 10),
                datetime(2024, 4, 5),
                None,
            ],
            name="created_at",
        )


@pytest.fixture
def sample_categorical_series() -> Any:
    """Create a sample categorical series for testing."""
    try:
        import polars as pl

        return pl.Series("category", ["A", "B", "A", "C", "B", "A", "C", None])
    except ImportError:
        import pandas as pd

        return pd.Series(["A", "B", "A", "C", "B", "A", "C", None], name="category")


# Backend parametrization support
@pytest.fixture(params=["polars", "pandas"])
def backend(request: pytest.FixtureRequest) -> Any:
    """Parametrized fixture that sets backend for each test run.

    This fixture enables running tests with both Polars and Pandas backends.
    Tests using this fixture will run twice - once with each backend.
    """
    from data_profiler.readers.backend import (
        set_backend,
        get_backend,
        Backend,
        _check_polars_available,
        _check_pandas_available,
    )

    backend_name = request.param

    # Skip if backend not available
    if backend_name == "polars" and not _check_polars_available():
        pytest.skip("Polars not available")
    if backend_name == "pandas" and not _check_pandas_available():
        pytest.skip("Pandas not available")

    # Set the backend
    set_backend(backend_name)

    yield get_backend()

    # Reset to auto after test
    set_backend(Backend.AUTO)


@pytest.fixture
def polars_backend() -> Any:
    """Fixture that explicitly sets Polars backend."""
    from data_profiler.readers.backend import (
        set_backend,
        get_backend,
        Backend,
        _check_polars_available,
    )

    if not _check_polars_available():
        pytest.skip("Polars not available")

    set_backend(Backend.POLARS)
    yield get_backend()
    set_backend(Backend.AUTO)


@pytest.fixture
def pandas_backend() -> Any:
    """Fixture that explicitly sets Pandas backend."""
    from data_profiler.readers.backend import (
        set_backend,
        get_backend,
        Backend,
        _check_pandas_available,
    )

    if not _check_pandas_available():
        pytest.skip("Pandas not available")

    set_backend(Backend.PANDAS)
    yield get_backend()
    set_backend(Backend.AUTO)


# Backend-specific series fixtures
@pytest.fixture
def numeric_series_polars() -> Any:
    """Create a numeric series using Polars."""
    import polars as pl

    return pl.Series("amount", [100.5, 200.75, 150.0, 300.25, 250.0, None])


@pytest.fixture
def numeric_series_pandas() -> Any:
    """Create a numeric series using Pandas."""
    import pandas as pd

    return pd.Series([100.5, 200.75, 150.0, 300.25, 250.0, None], name="amount")


@pytest.fixture
def string_series_polars() -> Any:
    """Create a string series using Polars."""
    import polars as pl

    return pl.Series("name", ["Alice", "Bob", "Charlie", "Diana", "Eve", None])


@pytest.fixture
def string_series_pandas() -> Any:
    """Create a string series using Pandas."""
    import pandas as pd

    return pd.Series(["Alice", "Bob", "Charlie", "Diana", "Eve", None], name="name")


@pytest.fixture
def datetime_series_polars() -> Any:
    """Create a datetime series using Polars."""
    from datetime import datetime

    import polars as pl

    return pl.Series(
        "created_at",
        [
            datetime(2024, 1, 15),
            datetime(2024, 2, 20),
            datetime(2024, 3, 10),
            datetime(2024, 4, 5),
            None,
        ],
    )


@pytest.fixture
def datetime_series_pandas() -> Any:
    """Create a datetime series using Pandas."""
    from datetime import datetime

    import pandas as pd

    return pd.Series(
        [
            datetime(2024, 1, 15),
            datetime(2024, 2, 20),
            datetime(2024, 3, 10),
            datetime(2024, 4, 5),
            None,
        ],
        name="created_at",
    )


@pytest.fixture
def categorical_series_polars() -> Any:
    """Create a categorical series using Polars."""
    import polars as pl

    return pl.Series("category", ["A", "B", "A", "C", "B", "A", "C", None])


@pytest.fixture
def categorical_series_pandas() -> Any:
    """Create a categorical series using Pandas."""
    import pandas as pd

    return pd.Series(["A", "B", "A", "C", "B", "A", "C", None], name="category")


@pytest.fixture
def dataframe_polars() -> Any:
    """Create a DataFrame using Polars."""
    import polars as pl

    return pl.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "amount": [100.5, 200.75, 150.0, 300.25, 250.0],
            "is_active": [True, False, True, True, False],
        }
    )


@pytest.fixture
def dataframe_pandas() -> Any:
    """Create a DataFrame using Pandas."""
    import pandas as pd

    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "amount": [100.5, 200.75, 150.0, 300.25, 250.0],
            "is_active": [True, False, True, True, False],
        }
    )
