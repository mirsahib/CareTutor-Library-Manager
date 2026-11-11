# Ticket 06 — Implementation Details: Seed Data

## Files changed

### 1. `backend/seed.py` (created — was empty)

The seed script. Three parts:

- **`SAMPLE_BOOKS`** — a module-level list of 10 plain dictionaries, one per sample book:
  - 3 Fiction, 3 Science, 3 History, 1 Uncategorized (spreads across the three required categories plus the default one).
  - Exactly one entry (`A Brief History of Time`) carries `"is_borrowed": 1, "borrower_name": "Jane Doe"`; every other entry is `"is_borrowed": 0, "borrower_name": None`.
  - All `published_year` values sit inside the 1900–2026 rule from SPEC §2.
- **`seed(reset=False)`** — the reusable function:
  1. Calls `init_db()` so the script works standalone against a fresh database (the API normally creates the table on startup; `CREATE TABLE IF NOT EXISTS` makes the double-call in tests harmless).
  2. If `reset=True`: `DELETE FROM books` first.
  3. Otherwise: `SELECT COUNT(*)` — if the catalog already has rows it returns `0` and inserts nothing (**idempotency**).
  4. Inserts all 10 rows with one `executemany` using `?` placeholders (AGENTS.md §2 — no string-built SQL), omitting `created_at` so the column default fills it in.
  5. Returns how many rows were inserted.
- **`main()`** — CLI glue: `--reset` is detected from `sys.argv`, then a human-readable summary is printed (`Seeded 10 books.` / `Catalog already populated; nothing to seed.`).

Run it with:

```bash
DATABASE_PATH=backend/library.db python backend/seed.py
DATABASE_PATH=backend/library.db python backend/seed.py --reset
```

### 2. `backend/test_app.py` (appended)

- **Module-level imports:** `from database import get_connection` and `from seed import seed`. Both are side-effect-free at import time (the database path is read lazily inside `get_connection`), so importing before `monkeypatch` sets `DATABASE_PATH` is safe — unlike `import app`, which runs `create_app()` at module level.
- **`empty_db` fixture** — mirrors the existing `client` fixture but only sets `DATABASE_PATH` to a fresh `tmp_path` file and runs `init_db()`. Each seed test gets its own isolated database file; the production `backend/library.db` is never touched (AGENTS.md §4).
- **`fetch_all_books()`** — tiny helper that opens a connection via the context manager and returns every row, so tests read like assertions rather than plumbing.
- **5 new tests** — one per acceptance criterion, detailed below.

No other files were modified: `database.py`, `app.py`, and the existing 4 tests are untouched.

## Test walkthrough

Run everything with:

```bash
venv/bin/pytest backend/test_app.py -v
```

**Result: 9 passed** (4 pre-existing + 5 new).

### `test_seed_inserts_ten_books_across_categories`
*Proves: "inserts exactly 10 books across Fiction, Science, and History".*
Calls `seed()` and asserts it returned `10`, re-reads the table and asserts `len == 10`, then builds a `set` of every category and asserts it is a **superset** of `{"Fiction", "Science", "History"}` (using `issubset`, so the extra `Uncategorized` category doesn't fail the check).

### `test_seed_marks_exactly_one_book_borrowed`
*Proves: "exactly one seeded book has `is_borrowed = 1` with a non-null `borrower_name`".*
Filters all rows to those with `is_borrowed == 1` and asserts the filtered list has length exactly 1 — catching both "none marked borrowed" and "two marked borrowed". Then asserts that book's `borrower_name` is not `None`, so a borrowed flag can never exist without a borrower. This is the raw-database assertion agreed when we relaxed the ticket's blocking edge (no `/return` endpoint needed).

### `test_seed_includes_uncategorized_book`
*Proves: "one seeded book has the default Uncategorized category".*
Collects the `category` column of every row into a list and asserts `"Uncategorized"` is present. A plain list (not a set) is used so the assertion would still pass if multiple books shared the category.

### `test_seed_is_idempotent`
*Proves: "running the seed again on a populated catalog inserts nothing".*
Calls `seed()` twice in a row, then asserts the table still holds exactly 10 rows. If the count guard in `seed()` were removed, the second call would push the count to 20 and this test would fail.

### `test_seed_reset_replaces_existing_catalog`
*Proves: "the `--reset` flag deletes existing books before inserting the sample set".*
Three phases:
1. `seed()` normally → 10 books.
2. Manually insert an 11th row (`Extra Book`) directly through `get_connection` with `?` parameters → asserts 11, proving a non-seed row exists to be wiped.
3. `seed(reset=True)` → asserts back to 10 **and** that `"Extra Book"` is no longer among the titles. The count alone isn't enough: without the `DELETE`, a reset that merely skipped the idempotency guard would still leave 11 rows; the title check proves the old data was actually removed.

Each test starts from a brand-new file in pytest's `tmp_path` (via the `empty_db` fixture), so tests are order-independent and can never corrupt `backend/library.db`.

## Verification performed

- `venv/bin/pytest backend/test_app.py -q` → **9 passed**
- CLI smoke test against a scratch database:
  1. fresh DB → `Seeded 10 books.`
  2. rerun → `Catalog already populated; nothing to seed.`
  3. `--reset` → `Seeded 10 books.`
  4. SQL check → `10|1` (10 rows, 1 borrowed) and categories `Fiction, History, Science, Uncategorized`
