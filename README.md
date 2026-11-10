## Folder Structure
```
library-app/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py           # Flask app instance, routes, and JSON error handlers
│   ├── database.py      # SQLite connection & database table initialization
│   ├── seed.py          # Script to insert 10 initial sample books
│   └── test_app.py      # Pytest test suite (3+ tests)
└── frontend/
    ├── Dockerfile
    ├── index.html       # Single Page Application root with CDN dependencies
    ├── app.js           # AngularJS module & ngRoute definitions
    ├── services/
    │   └── book.service.js  # All API $http calls in one place
    ├── controllers/
    │   ├── book-list.controller.js
    │   └── book-form.controller.js
    └── views/
        ├── book-list.html
        └── book-form.html
```