from typing import Any, cast

from flask import Flask, jsonify, request
from flask_cors import CORS
from marshmallow import EXCLUDE, ValidationError
from werkzeug.exceptions import HTTPException
from database import get_connection, init_db
from schema import BookSchema


def format_validation_error(error):
    messages = error.messages
    if isinstance(messages, dict):
        details = []
        for field, field_messages in messages.items():
            if isinstance(field_messages, dict):
                field_messages = [
                    message
                    for nested in field_messages.values()
                    for message in nested
                ]
            details.append(f"{field}: {', '.join(field_messages)}")
        return "; ".join(details)
    return str(messages)


def create_app():
    app = Flask(__name__)
    CORS(app)
    init_db()

    @app.route("/")
    def index():
        return jsonify({"message": "Library Book Manager API"}), 200

    @app.route("/api/books", methods=["GET"])
    def get_books():
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
        return jsonify([dict(row) for row in rows]), 200

    @app.route("/api/books", methods=["POST"])
    def create_book():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        try:
            book_data = cast(
                dict[str, Any], BookSchema(unknown=EXCLUDE).load(payload)
            )
        except ValidationError as error:
            return jsonify({"error": format_validation_error(error)}), 400

        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO books (title, author, category, published_year)
                VALUES (?, ?, ?, ?)
                """,
                (
                    book_data["title"],
                    book_data["author"],
                    book_data["category"],
                    book_data["published_year"],
                ),
            )
            row = conn.execute(
                "SELECT * FROM books WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()

        return jsonify(dict(row)), 201

    @app.route("/api/books/<int:book_id>", methods=["GET"])
    def get_book(book_id):
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM books WHERE id = ?", (book_id,)
            ).fetchone()

        if row is None:
            return jsonify({"error": "Book not found"}), 404

        return jsonify(dict(row)), 200

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify({"error": "An internal server error occurred"}), 500

    return app


app = create_app()
