(function () {
    'use strict';

    angular.module('libraryApp')
        .controller('BookListController', ['BookService', '$timeout', function (BookService, $timeout) {
            var vm = this;

            // State variables
            vm.books = [];
            vm.loading = false;
            vm.errorMessage = '';
            vm.successMessage = '';

            // Search & Filters
            vm.searchQuery = '';
            vm.selectedCategory = '';
            vm.categories = ['Fiction', 'Science', 'History', 'Technology', 'Philosophy', 'Biography'];

            // Sorting & Pagination (Optional Bonus Features)
            vm.sortColumn = 'title';
            vm.reverseSort = false;
            vm.currentPage = 1;
            vm.itemsPerPage = 5;

            // Borrow Modal State
            vm.borrowingBook = null;
            vm.borrowerName = '';
            vm.borrowError = '';

            // Fetch books from backend
            vm.loadBooks = function () {
                vm.loading = true;
                vm.errorMessage = '';

                BookService.getBooks(vm.searchQuery, vm.selectedCategory)
                    .then(function (response) {
                        vm.books = response.data;
                    })
                    .catch(function (error) {
                        vm.errorMessage = (error.data && error.data.error) 
                            ? error.data.error 
                            : 'Failed to connect to backend server. Make sure Flask API is running.';
                    })
                    .finally(function () {
                        vm.loading = false;
                    });
            };

            // Client-side category/search trigger
            vm.onFilterChange = function () {
                vm.currentPage = 1;
                vm.loadBooks();
            };

            // Sort Handler
            vm.sortBy = function (column) {
                if (vm.sortColumn === column) {
                    vm.reverseSort = !vm.reverseSort;
                } else {
                    vm.sortColumn = column;
                    vm.reverseSort = false;
                }
            };

            // Open Borrow Modal
            vm.openBorrowModal = function (book) {
                vm.borrowingBook = book;
                vm.borrowerName = '';
                vm.borrowError = '';
                var modalElement = new bootstrap.Modal(document.getElementById('borrowModal'));
                modalElement.show();
            };

            // Submit Borrow Action
            vm.confirmBorrow = function () {
                if (!vm.borrowerName || !vm.borrowerName.trim()) {
                    vm.borrowError = 'Please enter the borrower\'s name.';
                    return;
                }

                vm.loading = true;
                BookService.borrowBook(vm.borrowingBook.id, vm.borrowerName.trim())
                    .then(function () {
                        vm.showSuccess('Book successfully borrowed by ' + vm.borrowerName + '!');
                        var modalInstance = bootstrap.Modal.getInstance(document.getElementById('borrowModal'));
                        if (modalInstance) modalInstance.hide();
                        vm.loadBooks();
                    })
                    .catch(function (error) {
                        vm.borrowError = (error.data && error.data.error) ? error.data.error : 'Failed to borrow book.';
                    })
                    .finally(function () {
                        vm.loading = false;
                    });
            };

            // Return Book Action
            vm.returnBook = function (book) {
                if (!confirm('Mark "' + book.title + '" as returned?')) return;

                vm.loading = true;
                BookService.returnBook(book.id)
                    .then(function () {
                        vm.showSuccess('Book successfully returned!');
                        vm.loadBooks();
                    })
                    .catch(function (error) {
                        vm.errorMessage = (error.data && error.data.error) ? error.data.error : 'Failed to return book.';
                    })
                    .finally(function () {
                        vm.loading = false;
                    });
            };

            // Delete Book Action
            vm.deleteBook = function (book) {
                if (book.is_borrowed) {
                    alert('Cannot delete a borrowed book until it is returned.');
                    return;
                }

                if (!confirm('Are you sure you want to delete "' + book.title + '"?')) return;

                vm.loading = true;
                BookService.deleteBook(book.id)
                    .then(function () {
                        vm.showSuccess('Book deleted successfully.');
                        vm.loadBooks();
                    })
                    .catch(function (error) {
                        vm.errorMessage = (error.data && error.data.error) ? error.data.error : 'Failed to delete book.';
                    })
                    .finally(function () {
                        vm.loading = false;
                    });
            };

            vm.showSuccess = function (msg) {
                vm.successMessage = msg;
                $timeout(function () { vm.successMessage = ''; }, 4000);
            };

            // Initialize page load
            vm.loadBooks();
        }]);
})();