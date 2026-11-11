# Add a Book

Create a new book entry via the API:
- `POST /books` with `{title, author, category?, published_year}`
- Validation: title/author required, year 1900–current_year
- Response: 201 Created with full book object

Client-side: Form validation, error handling, success feedback.