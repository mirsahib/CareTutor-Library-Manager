# 04: Delete a book

**What to build:** A librarian can remove an available book from the catalog, receiving `204` with no body. A book that is currently borrowed cannot be deleted until it is returned — that attempt returns `409`. Unknown ids return `404`.

**Blocked by:** 03 (borrow and return a book) — the conflict test borrows through the API, then attempts deletion, so the 409 is verified end-to-end rather than by poking the database directly. (03 itself gates on 01.)

**Status:** ready-for-agent

- [ ] `DELETE /api/books/<id>` on an available book returns `204` with an empty body.
- [ ] The book is actually gone afterwards: `GET /api/books/<id>` returns `404`.
- [ ] Deleting a book with `is_borrowed = 1` returns `409` with `{"error": "..."}` and the book still exists.
- [ ] Unknown id returns `404` with `{"error": "..."}`.
- [ ] `pytest` covers success, borrowed-conflict, and not-found paths against an isolated temporary database.
