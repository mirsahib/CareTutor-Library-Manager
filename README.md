# Library Book Manager

A single-page web application enabling a librarian to manage a book repository and track book loans.

## Folder Structure

```
library-app/
├ docker-compose.yml          # Production stack (Coolify + tsdproxy)
├ backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                # Flask app instance, routes, and JSON error handlers
│   ├── database.py           # SQLite connection & database table initialization
│   ├── seed.py               # Script to insert 10 initial sample books
│   └── schema.py             # Marshmallow book validation schema
├ frontend/
│   ├── Dockerfile
│   ├── nginx.conf            # Serves the SPA and proxies /api to the backend
│   ├── index.html            # Single Page Application root with CDN dependencies
│   ├── app.js                # AngularJS module & ngRoute definitions
│   ├── services/
│   │   └── book.service.js   # All API $http calls in one place
│   ├── controllers/
│   │   ├── book-list.controller.js
│   │   └── book-form.controller.js
│   └── views/
│       ├── book-list.html
│       └── book-form.html
└── SPEC.md                   # Project specification
```

## API Details

**Base URL:** `http://localhost:5000/api`

### Endpoints

| HTTP Method | Endpoint | Description | Query/Payload | Success Code | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/books` | List books with optional filters | `search` (title/author), `category` | `200 OK` | - |
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

### Create Book Notes

- `category` defaults to `"Uncategorized"` if not provided (handled by `BookSchema` marshmallow schema)
- `created_at` is auto-generated on insertion and remains immutable
- `is_borrowed` and `borrower_name` are auto-set by borrow/return endpoints, not by create

## How to Install

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library-app
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Initialize the database and seed sample data**
   ```bash
   cd backend
   python seed.py
   ```

## How to Run

### Using Flask directly

```bash
cd backend
export FLASK_APP=app.py
flask run
```

The API will be available at `http://localhost:5000/api`

### Using Docker Compose

```bash
docker compose up --build
```

- Backend API: `http://localhost:5000/api`
- Frontend SPA: `http://localhost:3001`

The frontend calls the API through its own origin (`/api/books`), and `frontend/nginx.conf` proxies those requests to `backend:5000`. The backend also publishes port `5000` for direct API access.

## Deployment (Coolify + Tailscale/tsdproxy)

Coolify deploys the base `docker-compose.yml` as-is. The `frontend` container carries the tsdproxy labels, since nginx is the single public entrypoint:

```yaml
labels:
  - tsdproxy.enable=true
  - tsdproxy.name=library
  - "tsdproxy.port.1=443/https:3001/http,tailscale_funnel"
```

Configuration notes:

- **Labels go on `frontend`**, not `backend`. tsdproxy proxies the container's internal nginx port (`3001`).
- **`tailscale_funnel` is optional.** Remove it to expose the app only inside the Tailnet. For public exposure, the tsdproxy Docker provider must set `allowContainerFunnel: true` in `tsdproxy.yaml`.
- **Network:** tsdproxy must share a Docker network with the Coolify stack (e.g. `library_book_manager_default`) or be configured with `targetHostname`/`tryDockerInternalNetwork: true` so it can reach `frontend:3001`.
- **Persistence:** SQLite lives in the `library_data` volume at `/app/data/library.db` (`DATABASE_PATH`), so it survives redeploys.
- **Seed data:** on a fresh volume, run once inside the backend container:

  ```bash
  docker compose exec backend python seed.py
  ```

- **Ports:** `5000` and `3001` are published on the host for local access. If they might conflict with another service on the host, bind them to loopback (`127.0.0.1:5000:5000`) or remove the `ports` entries and reach the app only via the Tailscale hostname.

### Running Tests

```bash
cd backend
venv/bin/pytest -q
```

All 30+ tests should pass, covering book CRUD, borrow/return, search, category filtering, and error handling.

## API Reference Summary

- **GET /api/books** - List all books, support `search` (title/author) and `category` query params
- **POST /api/books** - Create a new book. Required: `title`, `author`, `published_year`. Optional: `category` (defaults to "Uncategorized")
- **GET /api/books/<id>** - Get a single book by ID
- **PUT /api/books/<id>** - Update a book. Only mutable fields (`title`, `author`, `category`, `published_year`) are updated; `created_at`, `is_borrowed`, `borrower_name` are preserved
- **DELETE /api/books/<id>** - Delete a book. Fails with 409 if book is currently borrowed
- **POST /api/books/<id>/borrow** - Borrow a book. Requires `borrower_name` (non-empty string). Fails with 409 if already borrowed
- **POST /api/books/<id>/return** - Return a borrowed book