# 06: Seed data script

**What to build:** A fresh checkout can be populated with sample books in one command, so the catalog is immediately demoable. The seed inserts 10 books spread across Fiction, Science, and History, including one book already marked as borrowed (to exercise the borrowed badge and return flow) and one with no category defaulting to "Uncategorized". Re-running the seed on a non-empty catalog is a no-op, and a `--reset` flag clears all books first. The script shares the same schema and database path as the running API.

**Blocked by:** 01 (create and read a book) — the schema and database path must exist. The pre-borrowed book is asserted on raw database state, so the return endpoint is not required.

**Status:** ready-for-agent

- [ ] Running the seed against an empty database inserts exactly 10 books across Fiction, Science, and History.
- [ ] Exactly one seeded book has `is_borrowed = 1` with a non-null `borrower_name` (verified on database state).
- [ ] One seeded book has the default "Uncategorized" category.
- [ ] Running the seed again on a populated catalog inserts nothing (idempotent).
- [ ] The `--reset` flag deletes existing books before inserting the sample set.
- [ ] `pytest` verifies seeding, idempotency, and reset against an isolated temporary database.
