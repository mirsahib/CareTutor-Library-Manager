# 05: Search and category filter on the book list

**What to build:** The librarian can narrow the catalog from the list endpoint alone: `search` matches case-insensitively as a substring of either title or author, `category` matches case-insensitively as an exact category, and when both are supplied they combine with AND logic. Omitted or empty parameters return the full list. The endpoint still returns `200` with a bare JSON array in every case.

**Blocked by:** 01 (create and read a book).

**Status:** ready-for-agent

- [ ] `GET /api/books?search=term` returns only books whose title or author contains `term`, case-insensitively.
- [ ] `GET /api/books?category=Science` returns only books in that category, case-insensitively.
- [ ] Both parameters together return only books satisfying both (AND).
- [ ] Omitted or empty parameters return all books, unchanged from the unfiltered behaviour.
- [ ] A search matching nothing returns `200` with `[]`, not an error.
- [ ] `pytest` covers each filter, the combined case, and the empty-params case against an isolated temporary database.
