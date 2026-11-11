# Ticket 03 — Implementation Details: Borrow and Return a Book

## What was built

Two loan-state endpoints:

- `POST /api/books/<id>/borrow` — lends an available book to a named borrower.
- `POST /api/books/<id>/return` — clears the loan from a borrowed book.

Both return the refreshed book object with `200`, and both leave `created_at` untouched. Borrowing sets `is_borrowed = 1` and stores the borrower; returning sets `is_borrowed = 0` and clears `borrower_name` to `NULL`.

## Files changed

### 1. `backend/app.py` — borrow and return routes

#### `borrow_book` — `backend/app.py:128`

```python
@app.route("/api/books/<int:book_id>/borrow", methods=["POST"])
def borrow_book(book_id):
    ...
```

Flow:

1. **Parse the body safely.** `request.get_json(silent=True)` returns `None` for missing, malformed, or non-JSON bodies. Anything that is not a JSON object (including a top-level array) is rejected with `400 {"error": ...}` before any database work.
2. **Validate `borrower_name` explicitly.** The value must be present, a string, and non-empty after trimming. `None`, numbers, lists, `""`, and whitespace-only strings all return `400 {"error": "borrower_name is required"}`. The stored value is the trimmed name.
3. **Look up the book.** `SELECT * FROM books WHERE id = ?` uses a bound parameter. A missing row returns `404 {"error": "Book not found"}`.
4. **Refuse a second loan.** If `is_borrowed` is truthy, return `409 {"error": "Book is already borrowed"}` without writing anything.
5. **Write the loan state.** Parameterized `UPDATE books SET is_borrowed = 1, borrower_name = ? WHERE id = ?`, then re-read the row and return it with `200`.

No schema is needed for this endpoint: the payload contains one field and the rule ("non-empty string") is simpler than a marshmallow schema. `BookSchema` remains the source of truth for the book catalog fields used by create/update.

#### `return_book` — `backend/app.py:160`

```python
@app.route("/api/books/<int:book_id>/return", methods=["POST"])
def return_book(book_id):
    ...
```

Flow:

1. **Look up the book.** A missing row returns `404 {"error": "Book not found"}`.
2. **Refuse a meaningless return.** If `is_borrowed` is falsy, return `409 {"error": "Book is not currently borrowed"}` without writing anything.
3. **Clear the loan.** Parameterized `UPDATE books SET is_borrowed = 0, borrower_name = NULL WHERE id = ?`, then re-read and return the row with `200`.

This endpoint has no request body, so it never parses JSON. A client that sends a malformed body is simply ignored rather than causing an HTML error or a `500`.

No changes were required in `database.py` or `schema.py`.

### 2. `backend/test_app.py` — eight new tests

Added at `backend/test_app.py:381`, all using the existing isolated `client` fixture (`tmp_path` database via `DATABASE_PATH`):

1. `create_book` — small helper that creates a book and returns its JSON; not a test.
2. `test_borrow_book_success`
3. `test_borrow_book_invalid_borrower_name`
4. `test_borrow_already_borrowed_conflict` (the SPEC §5 mandatory case)
5. `test_borrow_unknown_book_returns_json_404`
6. `test_borrow_malformed_body_returns_json_400`
7. `test_return_book_success`
8. `test_return_book_not_borrowed_conflict`
9. `test_return_unknown_book_returns_json_404`

No existing test was modified.

## Test walkthrough

Run the suite with:

```bash
venv/bin/pytest backend/test_app.py -q
```

**Result: 29 passed** (21 previous + 8 new).

### `test_borrow_book_success`
*Proves: "borrowing an available book returns `200` with `is_borrowed = 1` and the stored name."*

Creates a book, posts `{"borrower_name": "Jane Doe"}`, and asserts `200`, correct `id`, `is_borrowed == 1`, `borrower_name == "Jane Doe"`, and an unchanged `created_at`. It then fetches the book through `GET` and asserts it matches the borrow response, proving persistence.

### `test_borrow_book_invalid_borrower_name`
*Proves: "missing, empty, or non-string `borrower_name` returns `400`."*

Loops over six invalid payloads:

| Payload | Case |
| :--- | :--- |
| `{}` | missing field |
| `{"borrower_name": ""}` | empty string |
| `{"borrower_name": "   "}` | whitespace-only string |
| `{"borrower_name": 123}` | number |
| `{"borrower_name": null}` | null |
| `{"borrower_name": ["Jane"]}` | list |

Each must return `400`, be JSON, and include `error`. The book is re-fetched afterwards and must equal the original create response, proving no rejected request mutated the loan state.

### `test_borrow_already_borrowed_conflict`
*Proves: SPEC §5 mandatory `test_borrow_already_borrowed_conflict` and the ticket's "second borrow returns `409`."*

Creates a book, borrows it as `Jane Doe`, then attempts to borrow it again as `John Smith`. Asserts `409`, JSON, and an `error` key. It then fetches the book and asserts the original loan is intact: `is_borrowed == 1` and `borrower_name == "Jane Doe"`, not `"John Smith"`.

### `test_borrow_unknown_book_returns_json_404`
*Proves: "unknown id on borrow returns `404`."*

Posts a valid borrower to `/api/books/9999/borrow` and asserts `404`, JSON, and an `error` key.

### `test_borrow_malformed_body_returns_json_400`
*Proves: "no malformed payload produces HTML or a `500`."*

Sends three malformed variants to an existing book's borrow URL:

1. plain text (`text/plain`) — not JSON,
2. a JSON array — valid JSON but not an object,
3. broken JSON with `application/json` — unparseable.

All three must return `400`, be JSON, and contain `error`. `get_json(silent=True)` plus the `isinstance(payload, dict)` guard prevent Flask's HTML parsing errors and the generic `500` handler.

### `test_return_book_success`
*Proves: "returning a borrowed book returns `200` with `is_borrowed = 0` and `borrower_name` cleared to null."*

Creates and borrows a book, then posts to `/return`. Asserts `200`, `is_borrowed == 0`, `borrower_name is None`, an unchanged `created_at`, and that a subsequent `GET` matches the return response.

### `test_return_book_not_borrowed_conflict`
*Proves: "returning a book that is not borrowed returns `409`."*

Creates a book (never borrowed), posts to `/return`, and asserts `409`, JSON, and an `error` key. The re-fetched book must still equal the original, proving a rejected return writes nothing.

### `test_return_unknown_book_returns_json_404`
*Proves: "unknown id on return returns `404`."*

Posts to `/api/books/9999/return` and asserts `404`, JSON, and an `error` key.

## Verification performed

- `venv/bin/pytest backend/test_app.py -q` → **29 passed**
- Manual route check against a scratch database:
  - create → `201`
  - borrow as `Jane Doe` → `200`, `is_borrowed = 1`, name stored
  - borrow again → `409`
  - return → `200`, `is_borrowed = 0`, `borrower_name = None`
  - return again → `409`
  - borrow with `borrower_name = ""` → `400`
  - borrow unknown id → `404`
