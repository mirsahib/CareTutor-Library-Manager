# Ticket 05 — Implementation Details: Search and Category Filter

## What was built

`GET /api/books` now accepts two optional query parameters:

- `search` — case-insensitive substring match against `title` or `author`.
- `category` — case-insensitive exact match against `category`.

When both are supplied they combine with `AND`. Omitted or empty parameters leave the result set unfiltered, and the endpoint always returns `200` with a bare JSON array, including `[]` when nothing matches.

## Files changed

### 1. `backend/app.py` — filtered list query

Rewrote `get_books` at `backend/app.py:37`:

```python
@app.route("/api/books", methods=["GET"])
def get_books():
    search = (request.args.get("search") or "").strip()
    category = (request.args.get("category") or "").strip()

    clauses = []
    params = []

    if search:
        clauses.append(
            "(instr(lower(title), lower(?)) > 0"
            " OR instr(lower(author), lower(?)) > 0)"
        )
        params.extend([search, search])

    if category:
        clauses.append("lower(category) = lower(?)")
        params.append(category)

    query = "SELECT * FROM books"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY title"
    ...
```

Key decisions:

1. **Substring matching uses `instr`, not `LIKE`.** `instr(lower(column), lower(?)) > 0` treats the search term literally, so `%` and `_` in user input are ordinary characters rather than SQL wildcards. It is also case-insensitive via `lower()` and reads clearly as "contains".
2. **Both search branches are bound parameters.** `params.extend([search, search])` supplies the same term for title and author; no user input is concatenated into SQL (AGENTS.md §2).
3. **Category is an exact match.** `lower(category) = lower(?)` is case-insensitive but deliberately not a substring match, so `Sci` does not match `Science`.
4. **Clauses combine with `AND`.** Appending each active clause to `clauses` and joining with `" AND "` gives the required intersection semantics automatically.
5. **Empty filters vanish.** `(request.args.get(...) or "").strip()` turns a missing, empty, or whitespace-only parameter into a falsy value, so no clause is added and the query behaves exactly as before.
6. **Ordering is preserved.** `ORDER BY title` still applies to filtered and unfiltered results.
7. **The response shape is unchanged.** `jsonify([dict(row) for row in rows]), 200` still returns a bare JSON array; an empty result is simply `[]`.

No changes were needed in `database.py`, `schema.py`, or the frontend.

### 2. `backend/test_app.py` — fixture plus five tests

Added at `backend/test_app.py:573`:

- `catalog` — fixture that creates five books spanning Fiction, Science, and History, with titles/authors chosen to exercise case-insensitive and partial matching.
- `book_titles` — helper that extracts titles from a response without hiding status-code assertions.
- Five tests, one per acceptance criterion.

The existing isolated `client` fixture (`tmp_path` database via `DATABASE_PATH`) is reused, so every test starts from an empty catalog.

## Test walkthrough

Run the suite with:

```bash
venv/bin/pytest backend/test_app.py -q
```

**Result: 37 passed** (32 previous + 5 new).

### `test_list_books_search_matches_title_or_author_case_insensitively`
*Proves: "`search` matches title or author as a case-insensitive substring."*

With the five-book catalog it makes three requests:

- `?search=ORWELL` → `["1984"]` (author match, uppercase query),
- `?search=gatsby` → `["The Great Gatsby"]` (title match, lowercase query),
- `?search=history` → `["A Brief History of Time", "SPQR: A History of Ancient Rome"]` (partial match in two titles).

The last assertion proves substring matching rather than prefix or exact matching.

### `test_list_books_category_filter_is_case_insensitive_exact`
*Proves: "`category` matches case-insensitively as an exact category."*

- `?category=SCIENCE` → the two Science books, proving case-insensitivity.
- `?category=Fiction` → the two Fiction books, proving another category works.
- `?category=Sci` → `[]`, proving the match is exact and not a substring.

### `test_list_books_search_and_category_combine_with_and`
*Proves: "both parameters together return only books satisfying both (AND)."*

- `?search=THE&category=science` → only `"The Selfish Gene"`. The other Science book does not contain "the"; the other "the" title is Fiction, so both filters are required to produce this single result.
- `?search=gatsby&category=Science` → `[]`. "Gatsby" exists in Fiction only, so the intersection is empty.

If the code used `OR` instead of `AND`, the first request would return every Science book and the second would return `"The Great Gatsby"`.

### `test_list_books_empty_params_return_all`
*Proves: "omitted or empty parameters return all books, unchanged from the unfiltered behaviour."*

Captures the response for `GET /api/books` as a baseline and asserts it contains all five catalog entries. It then repeats the request with:

- no query string,
- `?search=`,
- `?category=`,
- `?search=&category=`.

Each response must be `200` and exactly equal to the baseline JSON, so empty values cannot accidentally become filters.

### `test_list_books_search_with_no_match_returns_empty_array`
*Proves: "a search matching nothing returns `200` with `[]`, not an error."*

Requests `?search=zzzzz`, asserts `200`, JSON content type, and an empty list. This catches implementations that treat a zero-row result as a `404`.

## Verification performed

- `venv/bin/pytest backend/test_app.py -q` → **37 passed**
- Manual route check against a scratch catalog:
  - all books → 3 rows
  - `search=ORWELL` → `1984`
  - `category=science` → `A Brief History of Time`
  - `search=the&category=SCIENCE` → `[]` for that catalog
  - `search=&category=` → all 3 rows
  - `search=zzz` → `[]`
