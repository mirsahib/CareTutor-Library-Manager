import pytest


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
