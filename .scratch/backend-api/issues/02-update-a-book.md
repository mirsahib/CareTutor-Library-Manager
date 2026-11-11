# 02: Update a book

**What to build:** A librarian can edit an existing book's title, author, category, and published year. The same validation as creation applies: title/author required and non-empty, year within 1900–2026. A successful update returns `200` with the refreshed book; bad input returns a JSON `400`; an unknown id returns a JSON `404`. The original `created_at` never changes.

**Blocked by:** 01 (create and read a book).

**Status:** ready-for-agent

- [ ] `PUT /api/books/<id>` with valid fields returns `200` and the updated book object.
- [ ] Missing/empty `title` or `author`, or a year outside 1900–2026, returns `400` with `{"error": "..."}`.
- [ ] Unknown id returns `404` with `{"error": "..."}`.
- [ ] `created_at` is byte-for-byte unchanged after an update.
- [ ] Loan fields (`is_borrowed`, `borrower_name`) are untouched by an update.
- [ ] Malformed JSON body returns `400`, never HTML or `500`.
- [ ] `pytest` covers success, validation failure, and not-found paths against an isolated temporary database.
