# Borrow and Return

**Borrow:**
- `POST /books/<id>/borrow` with `{borrower_name}`
- Requires non-empty borrower_name (400 if missing)
- Book must not already be borrowed (409 Conflict)
- Sets `is_borrowed=1` and `borrower_name`

**Return:**
- `POST /books/<id>/return`
- Book must be currently borrowed (409 if not)
- Clears `is_borrowed=0` and `borrower_name=NULL`

Client-side: Bootstrap modals for borrower name input, success/failure alerts.