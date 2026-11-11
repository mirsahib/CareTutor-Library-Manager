(function () {
    'use strict';

    angular.module('libraryApp', ['ngRoute'])
        .config(['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {
            // Enable hashbang mode for standard AngularJS SPA routing
            $locationProvider.hashPrefix('!');

            $routeProvider
                .when('/books', {
                    templateUrl: 'views/book-list.html',
                    controller: 'BookListController',
                    controllerAs: 'vm'
                })
                .when('/books/new', {
                    templateUrl: 'views/book-form.html',
                    controller: 'BookFormController',
                    controllerAs: 'vm'
                })
                .when('/books/:id/edit', {
                    templateUrl: 'views/book-form.html',
                    controller: 'BookFormController',
                    controllerAs: 'vm'
                })
                .otherwise({
                    redirectTo: '/books'
                });
        }]);
})();