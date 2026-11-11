# Search and Category Filter

**Search (`GET /books?search=`):**
- Case-insensitive substring match against title OR author
- Combines with category filter using AND

**Category (`GET /books?category=`):**
- Case-insensitive exact match
- Omitted/empty returns all books

**Combined filtering:**
- Search + category both apply (AND logic)
- Absent/empty params return all books

Client-side: Debounced search input, category dropdown with "All" option.