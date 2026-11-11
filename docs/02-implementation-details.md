# Ticket 02 — Implementation Details: Update a Book

## What was built

`PUT /api/books/<id>` updates an existing book's mutable catalog fields and returns the refreshed row.

- `title`, `author`, `category`, and `published_year` are updated.
- `id` and `created_at` are never written by the update.
- `is_borrowed` and `borrower_name` are never written by the update.
- Validation is delegated to `BookSchema` from `backend/schema.py`, so creation and update share one rule set.
- Client-supplied readonly fields are discarded via `BookSchema(unknown=EXCLUDE)`.

## Files changed

### 1. `backend/app.py` — new `update_book` route

Added at `backend/app.py:87`:

```python
@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    ...
```

The handler follows the same shape as `create_book`:

1. **Parse the body safely.** `request.get_json(silent=True)` returns `None` for missing, malformed, or non-JSON bodies. A non-dict value (including a JSON array) is rejected with `400 {"error": ...}`. Because parsing is silent, malformed input can never produce Flask's HTML `415`/`400` pages or reach the generic `500` handler.
2. **Validate with the shared schema.** `BookSchema(unknown=EXCLUDE).load(payload)` rejects missing/empty `title` or `author`, non-integer `published_year`, and years outside `1900`–`2026`. `ValidationError` is converted by the existing `format_validation_error` helper into `400 {"error": "..."}`. `unknown=EXCLUDE` prevents a client from trying to set `id`, `created_at`, `is_borrowed`, or `borrower_name`.
3. **Look up the book.** `SELECT * FROM books WHERE id = ?` runs with parameter substitution. If no row exists, the handler returns `404 {"error": "Book not found"}`.
4. **Update only mutable columns.**

   ```sql
   UPDATE books
   SET title = ?, author = ?, category = ?, published_year = ?
   WHERE id = ?
   ```

   `created_at`, `is_borrowed`, and `borrower_name` are deliberately absent from the `SET` clause, so their stored values are untouched.
5. **Return the refreshed object.** The row is re-read after the update and returned as JSON with `200`.

No changes were needed in `database.py`, `schema.py`, or the frontend. The route reuses the connection context manager, `sqlite3.Row` conversion, and the existing HTTP error handlers.

### 2. `backend/test_app.py` — five new tests

Appended at `backend/test_app.py:236`, all using the existing isolated `client` fixture (`tmp_path` database via `DATABASE_PATH`):

1. `test_update_book_success`
2. `test_update_book_invalid_input`
3. `test_update_book_preserves_created_at_and_loan_fields`
4. `test_update_unknown_book_returns_json_404`
5. `test_update_book_malformed_body_returns_json_400`

No existing test was modified.

## Test walkthrough

Run the suite with:

```bash
venv/bin/pytest backend/test_app.py -q
```

**Result: 21 passed** (16 previous + 5 new).

### `test_update_book_success`
*Proves: "valid fields return `200` and the updated book object."*

Creates a book, sends a `PUT` with new title/author/category/year, and asserts:

- status is `200` and the response is JSON,
- `id` is unchanged,
- all four mutable fields hold the new values,
- `created_at` equals the value captured from the create response.

It then performs `GET /api/books/<id>` and asserts the fetched body equals the update response, proving the change was actually persisted rather than only echoed.

### `test_update_book_invalid_input`
*Proves: "missing/empty title or author, or a year outside 1900–2026, returns `400`."*

Creates one book, then loops over eight invalid payloads:

| Payload | Rule exercised |
| :--- | :--- |
| no `title` | required field |
| `title: ""` | minimum length |
| no `author` | required field |
| `author: ""` | minimum length |
| `published_year: 1899` | lower bound |
| `published_year: 2027` | upper bound |
| `published_year: "not-a-year"` | strict integer |
| `published_year: 2000.5` | strict integer (float is not truncated) |

Each request must return `400`, be JSON, and include an `error` key. After the loop the test re-fetches the book and asserts it equals the original create response, proving rejected updates never partially write.

### `test_update_book_preserves_created_at_and_loan_fields`
*Proves: "`created_at` never changes" and "loan fields are untouched."*

Creates an available book, then marks it borrowed directly through `get_connection` (`is_borrowed = 1`, `borrower_name = "Jane Doe"`), since the borrow endpoint belongs to a later ticket. It captures the original `created_at`, performs a valid `PUT`, and asserts:

- `created_at` is identical to the pre-update value,
- `is_borrowed` is still `1`,
- `borrower_name` is still `"Jane Doe"`.

This fails if either readonly field is accidentally added to the `SET` clause.

### `test_update_unknown_book_returns_json_404`
*Proves: "unknown id returns `404` with `{"error": ...}`."*

Sends a valid `PUT` to `/api/books/9999` (no such row) and asserts `404`, JSON content type, and an `error` key.

### `test_update_book_malformed_body_returns_json_400`
*Proves: "malformed JSON body returns `400`, never HTML or `500`."*

Creates a book, then sends three malformed variants to its URL:

1. plain text (`text/plain`) — not JSON,
2. a JSON array — valid JSON but not an object,
3. broken JSON with `application/json` — unparseable.

All three must return `400`, be JSON, and contain `error`. The use of `get_json(silent=True)` plus the `isinstance(payload, dict)` guard is what makes this pass instead of raising.

## Verification performed

- `venv/bin/pytest backend/test_app.py -q` → **21 passed**
- Manual route check against a scratch database:
  - create → `201`
  - update with valid fields → `200`, changed fields, same `created_at`
  - update with empty title → `400 {"error": ...}`
  - update unknown id → `404 {"error": ...}`
