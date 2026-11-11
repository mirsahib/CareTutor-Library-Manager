from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from database import get_connection, init_db


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

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify({"error": "An internal server error occurred"}), 500

    return app


app = create_app()
