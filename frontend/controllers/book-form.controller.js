(function () {
    'use strict';

    angular.module('libraryApp')
        .controller('BookFormController', ['BookService', '$routeParams', '$location', function (BookService, $routeParams, $location) {
            var vm = this;

            vm.currentYear = new Date().getFullYear();
            vm.isEdit = !!$routeParams.id;
            vm.bookId = $routeParams.id || null;
            vm.loading = false;
            vm.errorMessage = '';

            vm.categories = ['Fiction', 'Science', 'History', 'Technology', 'Philosophy', 'Biography'];

            vm.book = {
                title: '',
                author: '',
                category: 'Fiction',
                published_year: vm.currentYear
            };

            // Load existing book data if editing
            if (vm.isEdit) {
                vm.loading = true;
                BookService.getBookById(vm.bookId)
                    .then(function (response) {
                        vm.book = response.data;
                        vm.book.published_year = parseInt(vm.book.published_year, 10);
                    })
                    .catch(function (error) {
                        vm.errorMessage = (error.data && error.data.error) ? error.data.error : 'Failed to fetch book details.';
                    })
                    .finally(function () {
                        vm.loading = false;
                    });
            }

            // Save Handler
            vm.saveBook = function (form) {
                if (form.$invalid) {
                    vm.errorMessage = 'Please fix the errors in the form before submitting.';
                    return;
                }

                vm.loading = true;
                vm.errorMessage = '';

                var savePromise = vm.isEdit
                    ? BookService.updateBook(vm.bookId, vm.book)
                    : BookService.createBook(vm.book);

                savePromise
                    .then(function () {
                        $location.path('/books');
                    })
                    .catch(function (error) {
                        vm.errorMessage = (error.data && error.data.error) ? error.data.error : 'An error occurred while saving.';
                    })
                    .finally(function () {
                        vm.loading = false;
                    });
            };

            vm.cancel = function () {
                $location.path('/books');
            };
        }]);
})();