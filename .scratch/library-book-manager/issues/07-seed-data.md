# Seed Data

Insert 10 sample books at startup via `seed.py`:
- Spread across Fiction, Science, History categories
- One book pre-marked as borrowed (to demonstrate Borrowed badge/Return flow immediately)
- One book with no category (defaults to "Uncategorized")
- Idempotent: skips insertion if table already has books
- `--reset` flag clears all books before inserting

Backend: Runs on app startup before first request.