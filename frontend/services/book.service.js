(function () {
    'use strict';

    angular.module('libraryApp')
        .service('BookService', ['$http', function ($http) {
            var API_BASE = '/api/books';

            // 1. Get all books (supports optional search and category params)
            this.getBooks = function (search, category) {
                var params = {};
                if (search) params.search = search;
                if (category) params.category = category;

                return $http.get(API_BASE, { params: params });
            };

            // 2. Get a single book by ID
            this.getBookById = function (id) {
                return $http.get(API_BASE + '/' + id);
            };

            // 3. Add a new book
            this.createBook = function (bookData) {
                return $http.post(API_BASE, bookData);
            };

            // 4. Update an existing book
            this.updateBook = function (id, bookData) {
                return $http.put(API_BASE + '/' + id, bookData);
            };

            // 5. Delete a book by ID
            this.deleteBook = function (id) {
                return $http.delete(API_BASE + '/' + id);
            };

            // 6. Borrow a book (requires borrower_name body)
            this.borrowBook = function (id, borrowerName) {
                return $http.post(API_BASE + '/' + id + '/borrow', { borrower_name: borrowerName });
            };

            // 7. Return a borrowed book
            this.returnBook = function (id) {
                return $http.post(API_BASE + '/' + id + '/return');
            };
        }]);
})();