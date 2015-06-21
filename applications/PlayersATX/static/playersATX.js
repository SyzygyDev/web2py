var playersATX = angular.module('playersATX', [
    "720kb.datepicker"
]);

playersATX.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{!');
    $interpolateProvider.endSymbol('!}');
});

playersATX.factory("playersATXService",
    [       "$q", "$http",
    function($q,   $http) {
        var API_ADDRESS = '/volleyball/api_volley/';

        function adminGet(thisAPI, params) {
            var getURL = API_ADDRESS + thisAPI + '.json';
            //get assumes params are an object, NOT an array
            if (params) {
                getURL += '?';
                angular.forEach(params, function(value, key) {
                    getURL += key + '=' + value + '&';
                });
                //remove last anpersand
                getURL.slice(0, -1);
            }
            return $http.get(getURL);
        }

        function adminPost(thisAPI, params) {
            var postURL = API_ADDRESS + thisAPI + '.json';
            params = params || {};
            return $http.post(postURL, params);
        }

        return {
            getTournaments: function() {
                return adminGet('get_tournaments').then(function(response) {
                    return response.data;
                });
            },
            createNewTournament: function(params) {
                return adminPost('new_tournament', params).then(function(response) {
                    return response.data;
                });
            },
            createNewLocation: function(params) {
                return adminPost('new_location', params).then(function(response) {
                    return response.data;
                });
            }
        };

    }]
)
