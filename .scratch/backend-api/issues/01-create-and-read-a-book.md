# 01: Create and read a book

**What to build:** A librarian can add a book to the catalog and fetch it back by id. Creating a book with a missing or empty title/author, or a published year outside 1900–2026, is rejected with a JSON `400` explanation instead of a crash. Fetching an unknown id returns a JSON `404`. Successful creation returns `201` with the full book object, including an automatically generated, never client-supplied `created_at`.

**Blocked by:** `library-book-manager/01-backend-walking-skeleton` (done) — schema, connection handling, and JSON error handlers already exist.

**Status:** ready-for-agent

- [ ] `POST /api/books` with valid `{title, author, category, published_year}` returns `201` and the stored book (with `id`, `is_borrowed = 0`, `created_at`).
- [ ] Missing or empty `title`/`author` returns `400` with `{"error": "..."}`.
- [ ] `published_year` below `1900`, above `2026`, or non-integer returns `400` with `{"error": "..."}`.
- [ ] A client-supplied `created_at` or `is_borrowed` in the payload is ignored; server values win.
- [ ] `GET /api/books/<id>` returns `200` with the book for an existing id.
- [ ] `GET /api/books/<id>` for an unknown id returns `404` with `{"error": "..."}`.
- [ ] No malformed payload ever produces HTML or a `500`.
- [ ] `pytest` covers SPEC §5 mandatory cases `test_add_book_success` and `test_add_book_invalid_input` against an isolated temporary database.
