from marshmallow import Schema, fields, validate, post_load

class BookSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1))
    author = fields.String(required=True, validate=validate.Length(min=1))
    category = fields.String()
    published_year = fields.Integer(
        required=True, strict=True, validate=validate.Range(min=1900, max=2026)
    )
    is_borrowed = fields.Boolean(dump_only=True)
    borrower_name = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make_book(self, data, **kwargs):
        data.setdefault("category", "Uncategorized")
        return data