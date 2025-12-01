"""Basic tests for data-profiler package."""

from data_profiler import __version__, simple_profile


def test_version() -> None:
    """Test version is a non-empty string."""
    assert isinstance(__version__, str) and __version__ != ""
    assert __version__ == "0.1.0"


def test_simple_profile_list() -> None:
    """Test simple_profile with a list."""
    out = simple_profile([1, 2, 3])
    assert out["type"] == "list"
    assert out["length"] == 3


def test_simple_profile_tuple() -> None:
    """Test simple_profile with a tuple."""
    out = simple_profile((1, 2))
    assert out["type"] == "tuple"
    assert out["length"] == 2


def test_simple_profile_set() -> None:
    """Test simple_profile with a set."""
    out = simple_profile({1, 2, 3, 4})
    assert out["type"] == "set"
    assert out["length"] == 4


def test_simple_profile_dict() -> None:
    """Test simple_profile with a dict (returns type only)."""
    out = simple_profile({"a": 1})
    assert out["type"] == "dict"
    assert "length" not in out


def test_simple_profile_string() -> None:
    """Test simple_profile with a string."""
    out = simple_profile("hello")
    assert out["type"] == "str"
