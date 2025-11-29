from data_profiler import __version__, simple_profile


def test_version():
    assert isinstance(__version__, str) and __version__ != ""


def test_simple_profile_list():
    out = simple_profile([1, 2, 3])
    assert out["type"] == "list" and out["length"] == 3
