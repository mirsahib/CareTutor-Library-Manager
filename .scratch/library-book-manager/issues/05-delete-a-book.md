# Delete a Book

Delete a book via the API:
- `DELETE /books/<id>`
- Book must not be currently borrowed (409 Conflict)
- Returns 204 No Content (no body)

If book is borrowed, user must return it first. Delete button is disabled or shows warning when `is_borrowed=1`.