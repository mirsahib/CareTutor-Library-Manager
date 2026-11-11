# Ticket 04 — Implementation Details: Delete a Book

## What was built

`DELETE /api/books/<id>` removes an available book from the catalog and returns `204` with no body. A borrowed book is protected: the delete is refused with `409` and the row is left untouched. Unknown ids return `404`.

## Files changed

### 1. `backend/app.py` — delete route

Added at `backend/app.py:183`:

```python
@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    ...
```

Flow:

1. **Look up the book.** `SELECT * FROM books WHERE id = ?` uses a bound parameter. If no row exists, return `404 {"error": "Book not found"}`.
2. **Enforce the loan rule.** If `is_borrowed` is truthy, return `409 {"error": "Book is currently borrowed and cannot be deleted"}` before any `DELETE` runs. The book therefore remains in the catalog with its loan state intact.
3. **Delete the available book.** Parameterized `DELETE FROM books WHERE id = ?`.
4. **Return an empty `204`.** The handler returns `"", 204`, so the response has no body, matching the API contract. The existing generic error handlers are not involved.

The route uses the same connection context manager as the rest of the API, so the lookup and delete happen on one connection and the transaction commits on exit. No changes were needed in `database.py`, `schema.py`, or the frontend.

### 2. `backend/test_app.py` — three new tests

Added at `backend/test_app.py:532`, using the existing isolated `client` fixture and the `create_book` helper from ticket 3:

1. `test_delete_book_success`
2. `test_delete_borrowed_book_conflict`
3. `test_delete_unknown_book_returns_json_404`

No existing test was modified.

## Test walkthrough

Run the suite with:

```bash
venv/bin/pytest backend/test_app.py -q
```

**Result: 32 passed** (29 previous + 3 new).

### `test_delete_book_success`
*Proves: "deleting an available book returns `204` with an empty body" and "the book is actually gone."*

Creates a book, sends `DELETE`, and asserts:

- status is `204`,
- the raw body is exactly `b""` (no JSON or HTML payload),
- a follow-up `GET /api/books/<id>` returns `404`, proving the row was removed rather than merely hidden from the delete response.

### `test_delete_borrowed_book_conflict`
*Proves: "deleting a borrowed book returns `409` and the book still exists."*

Creates a book, borrows it through the real `POST /borrow` endpoint (so the conflict is verified end-to-end rather than by writing to SQLite directly), then attempts `DELETE`. It asserts:

- status is `409` and the response is JSON with an `error` key,
- `GET /api/books/<id>` still returns `200`,
- the fetched book is identical to the borrow response, so the row and its loan state were not altered.

This fails if the borrowed check is removed or if the `DELETE` runs before the check.

### `test_delete_unknown_book_returns_json_404`
*Proves: "unknown id returns `404` with `{"error": ...}`."*

Sends `DELETE /api/books/9999` (no such row) and asserts `404`, JSON content type, and an `error` key.

## Verification performed

- `venv/bin/pytest backend/test_app.py -q` → **32 passed**
- Manual route check against a scratch database:
  - delete an available book → `204`, body `b""`
  - `GET` the deleted id → `404`
  - borrow a second book, then delete it → `409 {"error": ...}`
  - `GET` the borrowed book → still `200`
  - delete unknown id → `404`
