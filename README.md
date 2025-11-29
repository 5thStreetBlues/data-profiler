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
