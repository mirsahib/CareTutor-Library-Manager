import pytest

from database import get_connection
from seed import seed


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))

    from app import create_app
    from database import init_db

    init_db()
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_get_books_empty_returns_200_and_empty_array(client):
    response = client.get("/api/books")

    assert response.status_code == 200
    assert response.get_json() == []


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.is_json
    assert "error" in response.get_json()


def test_wrong_method_returns_json_405(client):
    response = client.delete("/api/books")

    assert response.status_code == 405
    assert response.is_json
    assert "error" in response.get_json()


def test_cors_headers_present(client):
    response = client.get(
        "/api/books", headers={"Origin": "http://localhost:3001"}
    )

    assert (
        response.headers.get("Access-Control-Allow-Origin")
        == "http://localhost:3001"
    )


@pytest.fixture
def empty_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "seed.db"))

    from database import init_db

    init_db()


def fetch_all_books():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM books ORDER BY id").fetchall()


def test_seed_inserts_ten_books_across_categories(empty_db):
    inserted = seed()

    assert inserted == 10
    books = fetch_all_books()
    assert len(books) == 10
    categories = {book["category"] for book in books}
    assert {"Fiction", "Science", "History"}.issubset(categories)


def test_seed_marks_exactly_one_book_borrowed(empty_db):
    seed()

    borrowed = [book for book in fetch_all_books() if book["is_borrowed"] == 1]

    assert len(borrowed) == 1
    assert borrowed[0]["borrower_name"] is not None


def test_seed_includes_uncategorized_book(empty_db):
    seed()

    categories = [book["category"] for book in fetch_all_books()]

    assert "Uncategorized" in categories


def test_seed_is_idempotent(empty_db):
    seed()
    seed()

    assert len(fetch_all_books()) == 10


def test_seed_reset_replaces_existing_catalog(empty_db):
    seed()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO books (title, author, category, published_year)"
            " VALUES (?, ?, ?, ?)",
            ("Extra Book", "Someone", "Fiction", 2000),
        )
    assert len(fetch_all_books()) == 11

    seed(reset=True)

    books = fetch_all_books()
    assert len(books) == 10
    assert "Extra Book" not in [book["title"] for book in books]


def test_add_book_success(client):
    response = client.post(
        "/api/books",
        json={
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
            "category": "Technology",
            "published_year": 1999,
        },
    )

    assert response.status_code == 201
    assert response.is_json
    book = response.get_json()
    assert isinstance(book["id"], int)
    assert book["title"] == "The Pragmatic Programmer"
    assert book["author"] == "Andrew Hunt"
    assert book["category"] == "Technology"
    assert book["published_year"] == 1999
    assert book["is_borrowed"] == 0
    assert book["borrower_name"] is None
    assert book["created_at"]

    fetched = client.get(f"/api/books/{book['id']}")
    assert fetched.status_code == 200
    assert fetched.get_json() == book


def test_add_book_defaults_category_to_uncategorized(client):
    response = client.post(
        "/api/books",
        json={"title": "Untitled", "author": "Anonymous", "published_year": 2020},
    )

    assert response.status_code == 201
    assert response.get_json()["category"] == "Uncategorized"


def test_add_book_invalid_input(client):
    invalid_payloads = [
        {"author": "A", "published_year": 2000},
        {"title": "", "author": "A", "published_year": 2000},
        {"title": "T", "published_year": 2000},
        {"title": "T", "author": "", "published_year": 2000},
        {"title": "T", "author": "A", "published_year": 1899},
        {"title": "T", "author": "A", "published_year": 2027},
        {"title": "T", "author": "A", "published_year": "not-a-year"},
        {"title": "T", "author": "A", "published_year": 2000.5},
    ]

    for payload in invalid_payloads:
        response = client.post("/api/books", json=payload)

        assert response.status_code == 400, payload
        assert response.is_json
        assert "error" in response.get_json()

    assert fetch_all_books() == []


def test_add_book_ignores_client_supplied_server_fields(client):
    response = client.post(
        "/api/books",
        json={
            "title": "Server Wins",
            "author": "Trust Me",
            "category": "Fiction",
            "published_year": 2010,
            "is_borrowed": 1,
            "borrower_name": "Mallory",
            "created_at": "1999-01-01T00:00:00",
        },
    )

    assert response.status_code == 201
    book = response.get_json()
    assert book["is_borrowed"] == 0
    assert book["borrower_name"] is None
    assert not book["created_at"].startswith("1999-01-01")


def test_add_book_malformed_body_returns_json_400(client):
    responses = [
        client.post("/api/books", data="not json", content_type="text/plain"),
        client.post("/api/books", json=[1, 2, 3]),
        client.post("/api/books", data="{bad json", content_type="application/json"),
    ]

    for response in responses:
        assert response.status_code == 400
        assert response.is_json
        assert "error" in response.get_json()


def test_get_book_by_id_returns_200(client):
    created = client.post(
        "/api/books",
        json={"title": "Dune", "author": "Frank Herbert", "published_year": 1965},
    ).get_json()

    response = client.get(f"/api/books/{created['id']}")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == created


def test_get_unknown_book_returns_json_404(client):
    response = client.get("/api/books/9999")

    assert response.status_code == 404
    assert response.is_json
    assert "error" in response.get_json()


def test_update_book_success(client):
    created = client.post(
        "/api/books",
        json={
            "title": "Old Title",
            "author": "Old Author",
            "category": "Fiction",
            "published_year": 1990,
        },
    ).get_json()

    response = client.put(
        f"/api/books/{created['id']}",
        json={
            "title": "New Title",
            "author": "New Author",
            "category": "History",
            "published_year": 2005,
        },
    )

    assert response.status_code == 200
    assert response.is_json
    updated = response.get_json()
    assert updated["id"] == created["id"]
    assert updated["title"] == "New Title"
    assert updated["author"] == "New Author"
    assert updated["category"] == "History"
    assert updated["published_year"] == 2005
    assert updated["created_at"] == created["created_at"]

    fetched = client.get(f"/api/books/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.get_json() == updated


def test_update_book_invalid_input(client):
    created = client.post(
        "/api/books",
        json={
            "title": "Untouched",
            "author": "Original",
            "category": "Fiction",
            "published_year": 1990,
        },
    ).get_json()

    invalid_payloads = [
        {"author": "A", "published_year": 2000},
        {"title": "", "author": "A", "published_year": 2000},
        {"title": "T", "published_year": 2000},
        {"title": "T", "author": "", "published_year": 2000},
        {"title": "T", "author": "A", "published_year": 1899},
        {"title": "T", "author": "A", "published_year": 2027},
        {"title": "T", "author": "A", "published_year": "not-a-year"},
        {"title": "T", "author": "A", "published_year": 2000.5},
    ]

    for payload in invalid_payloads:
        response = client.put(f"/api/books/{created['id']}", json=payload)

        assert response.status_code == 400, payload
        assert response.is_json
        assert "error" in response.get_json()

    fetched = client.get(f"/api/books/{created['id']}").get_json()
    assert fetched == created


def test_update_book_preserves_created_at_and_loan_fields(client):
    created = client.post(
        "/api/books",
        json={
            "title": "Borrowed Book",
            "author": "A. Writer",
            "category": "Fiction",
            "published_year": 2001,
        },
    ).get_json()

    with get_connection() as conn:
        conn.execute(
            "UPDATE books SET is_borrowed = 1, borrower_name = ? WHERE id = ?",
            ("Jane Doe", created["id"]),
        )

    response = client.put(
        f"/api/books/{created['id']}",
        json={
            "title": "Borrowed Book",
            "author": "A. Writer",
            "category": "Science",
            "published_year": 2002,
        },
    )

    assert response.status_code == 200
    updated = response.get_json()
    assert updated["created_at"] == created["created_at"]
    assert updated["is_borrowed"] == 1
    assert updated["borrower_name"] == "Jane Doe"


def test_update_unknown_book_returns_json_404(client):
    response = client.put(
        "/api/books/9999",
        json={
            "title": "Ghost",
            "author": "Nobody",
            "category": "Fiction",
            "published_year": 2000,
        },
    )

    assert response.status_code == 404
    assert response.is_json
    assert "error" in response.get_json()


def test_update_book_malformed_body_returns_json_400(client):
    created = client.post(
        "/api/books",
        json={"title": "Dune", "author": "Frank Herbert", "published_year": 1965},
    ).get_json()

    responses = [
        client.put(
            f"/api/books/{created['id']}",
            data="not json",
            content_type="text/plain",
        ),
        client.put(f"/api/books/{created['id']}", json=[1, 2, 3]),
        client.put(
            f"/api/books/{created['id']}",
            data="{bad json",
            content_type="application/json",
        ),
    ]

    for response in responses:
        assert response.status_code == 400
        assert response.is_json
        assert "error" in response.get_json()


def create_book(client, **overrides):
    payload = {
        "title": "Borrowable Book",
        "author": "A. Writer",
        "category": "Fiction",
        "published_year": 2001,
    }
    payload.update(overrides)
    return client.post("/api/books", json=payload).get_json()


def test_borrow_book_success(client):
    created = create_book(client)

    response = client.post(
        f"/api/books/{created['id']}/borrow",
        json={"borrower_name": "Jane Doe"},
    )

    assert response.status_code == 200
    assert response.is_json
    book = response.get_json()
    assert book["id"] == created["id"]
    assert book["is_borrowed"] == 1
    assert book["borrower_name"] == "Jane Doe"
    assert book["created_at"] == created["created_at"]

    fetched = client.get(f"/api/books/{created['id']}")
    assert fetched.get_json() == book


def test_borrow_book_invalid_borrower_name(client):
    created = create_book(client)
    invalid_payloads = [
        {},
        {"borrower_name": ""},
        {"borrower_name": "   "},
        {"borrower_name": 123},
        {"borrower_name": None},
        {"borrower_name": ["Jane"]},
    ]

    for payload in invalid_payloads:
        response = client.post(
            f"/api/books/{created['id']}/borrow", json=payload
        )

        assert response.status_code == 400, payload
        assert response.is_json
        assert "error" in response.get_json()

    fetched = client.get(f"/api/books/{created['id']}").get_json()
    assert fetched == created


def test_borrow_already_borrowed_conflict(client):
    created = create_book(client)
    client.post(
        f"/api/books/{created['id']}/borrow",
        json={"borrower_name": "Jane Doe"},
    )

    response = client.post(
        f"/api/books/{created['id']}/borrow",
        json={"borrower_name": "John Smith"},
    )

    assert response.status_code == 409
    assert response.is_json
    assert "error" in response.get_json()

    fetched = client.get(f"/api/books/{created['id']}").get_json()
    assert fetched["is_borrowed"] == 1
    assert fetched["borrower_name"] == "Jane Doe"


def test_borrow_unknown_book_returns_json_404(client):
    response = client.post(
        "/api/books/9999/borrow", json={"borrower_name": "Jane Doe"}
    )

    assert response.status_code == 404
    assert response.is_json
    assert "error" in response.get_json()


def test_borrow_malformed_body_returns_json_400(client):
    created = create_book(client)

    responses = [
        client.post(
            f"/api/books/{created['id']}/borrow",
            data="not json",
            content_type="text/plain",
        ),
        client.post(f"/api/books/{created['id']}/borrow", json=[1, 2, 3]),
        client.post(
            f"/api/books/{created['id']}/borrow",
            data="{bad json",
            content_type="application/json",
        ),
    ]

    for response in responses:
        assert response.status_code == 400
        assert response.is_json
        assert "error" in response.get_json()


def test_return_book_success(client):
    created = create_book(client)
    client.post(
        f"/api/books/{created['id']}/borrow",
        json={"borrower_name": "Jane Doe"},
    )

    response = client.post(f"/api/books/{created['id']}/return")

    assert response.status_code == 200
    assert response.is_json
    book = response.get_json()
    assert book["id"] == created["id"]
    assert book["is_borrowed"] == 0
    assert book["borrower_name"] is None
    assert book["created_at"] == created["created_at"]

    fetched = client.get(f"/api/books/{created['id']}")
    assert fetched.get_json() == book


def test_return_book_not_borrowed_conflict(client):
    created = create_book(client)

    response = client.post(f"/api/books/{created['id']}/return")

    assert response.status_code == 409
    assert response.is_json
    assert "error" in response.get_json()

    fetched = client.get(f"/api/books/{created['id']}").get_json()
    assert fetched == created


def test_return_unknown_book_returns_json_404(client):
    response = client.post("/api/books/9999/return")

    assert response.status_code == 404
    assert response.is_json
    assert "error" in response.get_json()


