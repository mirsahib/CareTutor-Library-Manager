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
