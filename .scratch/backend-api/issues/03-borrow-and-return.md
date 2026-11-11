# 03: Borrow and return a book

**What to build:** A librarian can lend an available book to a named borrower and mark it returned later. Borrowing an already-borrowed book is refused with `409`; borrowing without a valid `borrower_name` is refused with `400`. Returning a book that is not currently borrowed is refused with `409`. Unknown ids return `404`. Success rewrites the loan state: borrowing sets `is_borrowed = 1` and stores the name, returning clears both.

**Blocked by:** 01 (create and read a book).

**Status:** ready-for-agent

- [ ] `POST /api/books/<id>/borrow` with `{borrower_name}` on an available book returns `200` and the book with `is_borrowed = 1` and the stored name.
- [ ] Missing, empty, or non-string `borrower_name` returns `400` with `{"error": "..."}`.
- [ ] Borrowing a book with `is_borrowed = 1` returns `409` with `{"error": "..."}`.
- [ ] `POST /api/books/<id>/return` on a borrowed book returns `200` with `is_borrowed = 0` and `borrower_name` cleared to null.
- [ ] Returning a book that is not borrowed returns `409` with `{"error": "..."}`.
- [ ] Unknown id on either endpoint returns `404` with `{"error": "..."}`.
- [ ] No malformed payload ever produces HTML or a `500`.
- [ ] `pytest` covers SPEC §5 mandatory case `test_borrow_already_borrowed_conflict` plus the 400/404/409 paths against an isolated temporary database.
