# Walking Skeleton

A minimal end-to-end implementation that exercises the full stack:
- Backend: Flask app with SQLite, seed data, and API endpoints
  - **Dependencies**: `flask`, `flask-cors`, `flask-sqlalchemy`, `marshmallow`
  - **Validation schemas**: `BookSchema` using marshmallow for request validation and response serialization
- Frontend: AngularJS app with basic book list view
- Docker Compose setup for local development

This establishes the baseline for adding subsequent features.

## Backend Setup

### Installation

```bash
pip install flask flask-cors flask-sqlalchemy marshmallow
```

### Book Schema

```python
from marshmallow import Schema, fields, validate

class BookSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1))
    author = fields.String(required=True, validate=validate.Length(min=1))
    category = fields.String(missing="Uncategorized")
    published_year = fields.Integer(required=True, validate=validate.Range(min=1900, max=2026))
    is_borrowed = fields.Boolean(dump_only=True)
    borrower_name = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
```