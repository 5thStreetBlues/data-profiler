# data-profiler

Small data profiling utilities and experiment for quick dataset summaries.

Quick start

1. Create and activate a Python virtualenv (recommended).

   powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1

2. Install test deps and run tests:

   pip install -r requirements.txt
   pytest -q

3. To create a GitHub repository and push (optional, requires `gh`):

   gh repo create data-profiler --public --source=. --remote=origin --push

If `gh` is not available, create a repository on GitHub and add the remote:

   git remote add origin https://github.com/<your-username>/data-profiler.git
   git push -u origin main

License: MIT

Distribution metadata check
---------------------------

This repository includes a diagnostic script at `tools/check_dist_versions.py` that scans the current Python environment for installed distributions that are missing packaging metadata (notably an empty or missing Version field). Missing metadata can cause `pip` to raise errors when performing resolution or conflict checks.

How to run locally:

```powershell
Set-Location -Path 'D:\dev\projects\data-profiler'
python tools/check_dist_versions.py
```

CI integration
--------------

The GitHub Actions workflow runs this diagnostic after the test job to catch malformed installed metadata early. If the check fails in CI, inspect the runner environment for stray `.egg-info` or `.dist-info` directories and ensure the corresponding projects publish correct `METADATA` files (use `pyproject.toml` or `setup.cfg` with a `version` and `name`).

If you maintain local editable installs of other projects, run the script before CI or include the check in your pre-commit hooks.
