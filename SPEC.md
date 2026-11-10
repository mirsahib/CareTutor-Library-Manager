# Project Specification: Library Book Manager (Caretutors Assessment Part 1)

## 1. Project Overview
A single-page web application enabling a librarian to manage a book repository and track book loans. 
- **Backend:** Python 3.10+, Flask, SQLite (raw SQL via `sqlite3` driver).
- **Frontend:** AngularJS 1.8 (Single Page App with `ngRoute`), Bootstrap CSS.
- **Delivery Format:** Dockerized multi-container setup via Docker Compose.

---

## 2. Business Rules & Domain Logic

1. **Book Required Fields:** `title` (string, required, non-empty), `author` (string, required, non-empty).
2. **Published Year Constraints:** Integer between `1900` and `2026` inclusive.
3. **Borrowing Restrictions:**
   - A book currently marked as `is_borrowed = 1` CANNOT be borrowed again.
   - Borrowing requires a valid `borrower_name` string.
4. **Deletion Restrictions:**
   - A book currently marked as `is_borrowed = 1` CANNOT be deleted until it is returned.
5. **Data Immutability Rules:**
   - `created_at` timestamp must be automatically generated at insertion and remain immutable.

---

## 3. Backend API Contract (Flask + SQLite)

**Global Requirement:** All API responses (successes and errors) MUST return valid JSON. HTML error pages or stack traces are strictly prohibited (HTTP status 500 must never occur due to malformed user input).

### Base URL: `http://localhost:5000/api`

### Endpoints Detail

| HTTP Method | Endpoint | Description | Request Payload | Success Code | Error Codes & Triggers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/books` | List books with optional filters | Query params: `search` (title/author), `category` | `200 OK` | - |
| `POST` | `/books` | Create a new book | `{ "title": str, "author": str, "category": str, "published_year": int }` | `201 Created` | `400 Bad Request` (Missing fields or invalid year) |
| `GET` | `/books/<id>` | Fetch single book detail | None | `200 OK` | `404 Not Found` |
| `PUT` | `/books/<id>` | Update existing book details | `{ "title": str, "author": str, "category": str, "published_year": int }` | `200 OK` | `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/books/<id>` | Delete a book | None | `204 No Content` | `404 Not Found`, `409 Conflict` (If book is currently borrowed) |
| `POST` | `/books/<id>/borrow` | Mark book as borrowed | `{ "borrower_name": str }` | `200 OK` | `400 Bad Request` (Missing name), `404 Not Found`, `409 Conflict` (Already borrowed) |
| `POST` | `/books/<id>/return` | Mark book as returned | None | `200 OK` | `404 Not Found`, `409 Conflict` (Not currently borrowed) |

### JSON Error Standard Format
```json
{
  "error": "Human readable explanation of the failure"
}
```

### Database Schema (`library.db`)
```sql
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    published_year INTEGER NOT NULL,
    is_borrowed BOOLEAN NOT NULL DEFAULT 0,
    borrower_name TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Frontend Specifications (AngularJS 1.8)

### Views & Routing Layout
- `#/books` -> **Book List Screen**
  - Text search bar (filters title and author via client-side or backend query).
  - Category dropdown filter (e.g., All, Fiction, Science, History).
  - Data table/cards listing all fields, displaying badges: `[Available]` (green) or `[Borrowed by Name]` (yellow/red).
  - Action items per row: `[Edit]`, `[Delete]`, `[Borrow]`, `[Return]`.
  - Borrow button opens a modal/prompt for `borrower_name`.
- `#/books/new` -> **Add Book Screen**
  - Form fields: Title, Author, Category, Published Year.
  - Client-side validation: Required inputs and year range [1900 - 2026].
  - Save and Cancel buttons.
- `#/books/:id/edit` -> **Edit Book Screen**
  - Prefilled form fields for updating book information.
  - Inline error validation messages.

### Frontend Architecture Rules
- All HTTP calls MUST reside inside a single service module (`BookService`). Direct `$http` calls inside controllers are forbidden.
- Global UI spinner/loading indicator during HTTP activity.
- Toast alert or clear message box when API calls fail (especially handling 409 Conflict alerts).

---

## 5. Required Automated Testing Strategy
- Unit & integration tests written with `pytest` inside `backend/test_app.py`.
- **Mandatory Test Cases:**
  1. `test_add_book_success`: Verify creating a book returns `201 Created` with valid body.
  2. `test_borrow_already_borrowed_conflict`: Verify attempting to borrow an already borrowed book returns `409 Conflict`.
  3. `test_add_book_invalid_input`: Verify missing `title` or year `< 1900` returns `400 Bad Request`.