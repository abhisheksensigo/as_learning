# Run tests for week4

When the user invokes this command, do the following:

1. Run pytest on the week4 backend tests. Use the repo root so this works from any subdirectory:
   ```
   cd "$(git rev-parse --show-toplevel)/week4" && make test
   ```
   Or equivalently: `cd "$(git rev-parse --show-toplevel)/week4" && PYTHONPATH=. pytest -q backend/tests`

2. Summarize the results:
   - Pass/fail status
   - Number of tests run
   - Any failure messages or stack traces

3. If there are failures, suggest next steps (e.g., which file/line to fix, or what might be wrong).

4. Optional: If tests pass, you may offer to run with coverage:
   ```
   cd "$(git rev-parse --show-toplevel)/week4" && PYTHONPATH=. pytest backend/tests --cov=backend --cov-report=term-missing
   ```
