# Graph Report - Library_Book_Manager  (2026-11-11)

## Corpus Check
- 22 files · ~4,685 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .db 1)

## Summary
- 124 nodes · 171 edges · 19 communities (9 shown, 10 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4c1bebdd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- backend
- Project Specification: Library Book Manager (Caretutors Assessment Part 1)
- Coding Guidelines & Best Practices for AI Agents
- app.py
- get_connection
- seed
- test_app.py
- Project Context & Candidate Assessment Guide
- Ticket 06 — Implementation Details: Seed Data
- README.md
- 02-update-a-book.md
- 03-borrow-and-return.md
- 04-delete-a-book.md
- 05-search-and-category-filter.md
- 06-seed-data.md

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 16 edges
2. `create_app()` - 13 edges
3. `seed()` - 13 edges
4. `init_db()` - 11 edges
5. `fetch_all_books()` - 9 edges
6. `2. `backend/test_app.py` (appended)` - 7 edges
7. `BookSchema` - 6 edges
8. `Project Specification: Library Book Manager (Caretutors Assessment Part 1)` - 6 edges
9. `Test walkthrough` - 6 edges
10. `client()` - 5 edges

## Surprising Connections (you probably didn't know these)
- ``test_seed_reset_replaces_existing_catalog`` --references--> `get_connection()`  [INFERRED]
  docs/06-implementation-details.md → backend/database.py
- `1. `backend/seed.py` (created — was empty)` --references--> `init_db()`  [INFERRED]
  docs/06-implementation-details.md → backend/database.py
- `1. `backend/seed.py` (created — was empty)` --references--> `main()`  [INFERRED]
  docs/06-implementation-details.md → backend/seed.py
- ``test_seed_reset_replaces_existing_catalog`` --references--> `empty_db()`  [INFERRED]
  docs/06-implementation-details.md → backend/test_app.py
- `2. `backend/test_app.py` (appended)` --references--> `fetch_all_books()`  [INFERRED]
  docs/06-implementation-details.md → backend/test_app.py

## Import Cycles
- None detected.

## Communities (19 total, 10 thin omitted)

### Community 0 - "backend"
Cohesion: 0.17
Nodes (11): build, environment, ports, volumes, build, depends_on, ports, services (+3 more)

### Community 1 - "Project Specification: Library Book Manager (Caretutors Assessment Part 1)"
Cohesion: 0.17
Nodes (11): 1. Project Overview, 2. Business Rules & Domain Logic, 3. Backend API Contract (Flask + SQLite), 4. Frontend Specifications (AngularJS 1.8), Base URL: `http://localhost:5000/api`, Database Schema (`library.db`), Endpoints Detail, Frontend Architecture Rules (+3 more)

### Community 2 - "Coding Guidelines & Best Practices for AI Agents"
Cohesion: 0.20
Nodes (9): 1. General Agent Rules, 2. Backend Rules: Python 3.10 & Flask, 3. Frontend Rules: AngularJS 1.8, 4. Testing Rules (`pytest`), Coding Guidelines & Best Practices for AI Agents, Controller Best Practices, Database Access (SQLite), Route & Validation Rules (+1 more)

### Community 3 - "app.py"
Cohesion: 0.19
Nodes (3): create_book(), format_validation_error(), BookSchema

### Community 4 - "get_connection"
Cohesion: 0.21
Nodes (9): create_app(), get_book(), get_books(), get_connection(), get_database_path(), init_db(), client(), empty_db() (+1 more)

### Community 5 - "seed"
Cohesion: 0.23
Nodes (14): main(), seed(), fetch_all_books(), test_seed_includes_uncategorized_book(), test_seed_inserts_ten_books_across_categories(), test_seed_is_idempotent(), test_seed_marks_exactly_one_book_borrowed(), test_seed_reset_replaces_existing_catalog() (+6 more)

### Community 6 - "test_app.py"
Cohesion: 0.14
Nodes (4): test_add_book_invalid_input(), test_add_book_success(), 01: Create and read a book, 5. Required Automated Testing Strategy

### Community 11 - "Project Context & Candidate Assessment Guide"
Cohesion: 0.29
Nodes (6): 1. Candidate Context, 2. Assessment Structure Overview, 3. Evaluation Criteria (What Reviewers Look For), Part 1: Home Task (Current Phase), Part 2: In-Person Office Session (50 Minutes), Project Context & Candidate Assessment Guide

### Community 12 - "Ticket 06 — Implementation Details: Seed Data"
Cohesion: 0.40
Nodes (4): 1. `backend/seed.py` (created — was empty), Files changed, Ticket 06 — Implementation Details: Seed Data, Verification performed

## Knowledge Gaps
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `5. Required Automated Testing Strategy` connect `test_app.py` to `Project Specification: Library Book Manager (Caretutors Assessment Part 1)`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `get_connection()` (e.g. with `2. `backend/test_app.py` (appended)` and ``test_seed_reset_replaces_existing_catalog``) actually correct?**
  _`get_connection()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14166666666666666 - nodes in this community are weakly interconnected._
- **Why does `Project Specification: Library Book Manager (Caretutors Assessment Part 1)` connect `Project Specification: Library Book Manager (Caretutors Assessment Part 1)` to `test_app.py`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `seed()` (e.g. with ``test_seed_inserts_ten_books_across_categories`` and ``test_seed_is_idempotent``) actually correct?**
  _`seed()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Why does `create_app()` connect `get_connection` to `app.py`, `test_app.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `init_db()` (e.g. with `1. `backend/seed.py` (created — was empty)` and `2. `backend/test_app.py` (appended)`) actually correct?**
  _`init_db()` has 2 INFERRED edges - model-reasoned connections that need verification._