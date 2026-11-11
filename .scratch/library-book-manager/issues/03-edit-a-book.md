# Edit a Book

Update an existing book via the API:
- `PUT /books/<id>` with `{title, author, category?, published_year}`
- Title and author are required after trimming
- Category defaults to "Uncategorized" when omitted/blank
- Response: 200 OK with updated book object

Client-side: Prefilled form, inline error messages, cancel option.