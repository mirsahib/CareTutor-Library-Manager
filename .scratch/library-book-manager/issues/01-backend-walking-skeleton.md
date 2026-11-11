# 01: Backend walking skeleton — API and database foundation

**Scope:** Backend only. No frontend changes.

**What to build:** A running Flask API backed by SQLite that can serve the book list. When no books exist it returns an empty array. Any unknown route, wrong method, or bad request gets a JSON error instead of an HTML page, and the frontend origin is allowed to call the API.

**Backend work:**
- Create the `books` table on startup; the database path comes from `DATABASE_PATH` with a local default.
- `GET /api/books` returns `200` with a bare JSON array, `[]` when empty.
- JSON handlers for unknown routes (`404`), wrong methods (`405`), malformed input, and unexpected errors; never HTML.
- Enable CORS so the AngularJS frontend can call the API.
- Use `sqlite3.Row` and `?` parameters in every query.

**Tests:**
- `GET /api/books` against an empty isolated database returns `200` and `[]`.

**Spec:** `SPEC.md` §3 (global requirements, list endpoint), §4 (database schema), §5 (testing).

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `GET /api/books` returns `200` and `[]` on an empty catalog.
- [x] The `books` table is created automatically on startup.
- [x] The database path is configurable via `DATABASE_PATH`.
- [x] Unknown routes and wrong methods return JSON, never HTML.
- [x] Bad input never causes a `500`.
- [x] Responses include CORS headers.
- [x] The empty-list test passes against a temporary database.
