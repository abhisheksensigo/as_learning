# Inspect database schema for week4

When the user invokes this command, do the following:

1. Read and display the schema from `week4/data/seed.sql` (CREATE TABLE statements).

2. Optionally read `week4/backend/app/models.py` and show the SQLAlchemy models (tables, columns, types).

3. Summarize the schema:
   - Table names
   - Columns per table with types
   - Primary keys, constraints

4. If the user wants to see the live DB schema (and `week4/data/app.db` exists), you may run:
   ```
   cd "$(git rev-parse --show-toplevel)/week4" && sqlite3 data/app.db ".schema"
   ```
   This shows the actual schema in the SQLite database.

5. Output a clear summary suitable for understanding the data model or planning schema changes.
