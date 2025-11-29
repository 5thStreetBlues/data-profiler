"""Very small data profiler helpers."""
from typing import Any, Dict


def simple_profile(data: Any) -> Dict[str, Any]:
    """Return a tiny profile dict for common types.

    - For pandas DataFrame (if available) returns row/col counts.
    - For list/tuple returns length.
    - Otherwise returns type name.
    """
    try:
        import pandas as pd

        if isinstance(data, pd.DataFrame):
            return {"type": "DataFrame", "rows": int(data.shape[0]), "cols": int(data.shape[1])}
    except Exception:
        # pandas isn't required for the package to work
        pass

    if isinstance(data, (list, tuple, set)):
        return {"type": type(data).__name__, "length": len(data)}

    return {"type": type(data).__name__}
