
var hellerVolleyBall = angular.module('hellerVolleyBall', ['ngBracket']);

hellerVolleyBall.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{!');
    $interpolateProvider.endSymbol('!}');
});