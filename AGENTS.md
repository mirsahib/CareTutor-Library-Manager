# Coding Guidelines & Best Practices for AI Agents

When modifying or generating code for this repository, agents MUST strictly adhere to the following principles optimized for low-latency, deterministic execution.

---

## 1. General Agent Rules

- **Minimal File Modifications:** Do not rewrite whole files unnecessarily. Keep updates focused on target functions.
- **No Unused Packages:** Stick strictly to standard libraries (`sqlite3`, `os`, `sys`, `datetime`) and specified dependencies (`Flask`, `Flask-CORS`, `pytest`, `angular`, `angular-route`, `bootstrap`).
- **Explicit Error Catching:** Never allow generic exception bubbles that yield unformatted standard 500 HTML responses.

---

## 2. Backend Rules: Python 3.10 & Flask

### Database Access (SQLite)
- Always open and close SQLite connections cleanly, or use context managers.
- Always set `conn.row_factory = sqlite3.Row` to allow direct conversion of database rows into JSON dictionaries (`dict(row)`).
- Use parameter substitution (`?`) for ALL queries to prevent SQL injection. Never format or concatenate strings into SQL queries.

```python
# CORRECT
cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))

# INCORRECT
cursor.execute(f"SELECT * FROM books WHERE id = {book_id}")
```

### Route & Validation Rules
- Return explicit HTTP status codes alongside JSON dictionaries: `return jsonify({"data": ...}), 200`.
- Catch `TypeError`, `ValueError`, and database operational errors explicitly:
```python
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    return jsonify({"error": "An internal server error occurred"}), 500
```
- Explicitly convert data types from incoming JSON payloads before SQLite ingestion.

---

## 3. Frontend Rules: AngularJS 1.8

### Scope & Architecture Guidelines
- Use standard AngularJS 1.8 syntax (`angular.module('libraryApp')`).
- Avoid modern ES6 imports/build tools (Webpack, Vite, Babel). Use clean global script tags in `index.html`.
- **Single Responsibility Service:** Keep all API calls in `BookService`.

```javascript
// Example Service Pattern
angular.module('libraryApp').factory('BookService', ['$http', function($http) {
    var baseUrl = 'http://localhost:5000/api/books';
    return {
        getAll: function(search, category) {
            return $http.get(baseUrl, { params: { search: search, category: category } });
        },
        create: function(bookData) {
            return $http.post(baseUrl, bookData);
        },
        borrow: function(id, borrowerName) {
            return $http.post(baseUrl + '/' + id + '/borrow', { borrower_name: borrowerName });
        }
    };
}]);
```

### Controller Best Practices
- Controller functions must only assign data to `$scope` and invoke `BookService` promises.
- Handle promise rejections explicitly to show user alerts:
```javascript
BookService.borrow(id, name).then(function(response) {
    // Success flow
}, function(errorResponse) {
    $scope.errorMessage = errorResponse.data.error || 'Failed to borrow book';
});
```

---

## 4. Testing Rules (`pytest`)

- Unit tests must run using an in-memory database (`sqlite3.connect(':memory:')`) or a temporary isolated database file to prevent corrupting development data.
- Use Flask's built-in test client (`app.test_client()`).
```python
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Initialize isolated schema here
        yield client
```