hellerVolleyBall.controller('HVBAindex',
  [        "$scope", "$window", "$rootScope", "hellerVolleyBallService", "LocalStorage",
  function ($scope,   $window,   $rootScope,   hellerVolleyBallService,   LocalStorage) {
    var templatePrefix = "/volleyball/static/tpls/",
        hvbStorage = new LocalStorage("hvba"),
        rootData = $rootScope.rawData,
        NOW = new Date();

    var viewActive = true;
    $scope.newTournament = hvbStorage.getObject("newTournamentData") || {};

    $scope.today = formatedDate( NOW );
    $scope.timePicker = timePickerDefaults();

    hellerVolleyBallService.getTournaments().then(function(results){
        if (results.success) {
            var thisReturn = results.data;
            $scope.tournaments = thisReturn.tournaments;
            preProcess($scope.tournaments);
            $scope.types = thisReturn.types;
            $scope.locations = thisReturn.locations;
            viewActive = $scope.tournaments.active.length >=1;
            checkModalStatus();
        }
    });

    function preProcess(tournaments) {
        if (tournaments.active && tournaments.active.length >= 1) {
            angular.forEach(tournaments.active, function(thistourny) {
                processTournament(thistourny);
            });
        }
        if (tournaments.expired && tournaments.expired.length >= 1) {
            angular.forEach(tournaments.expired, function(thistourny) {
                processTournament(thistourny);
            });
        }
    }

    function processTournament(tournament) {
        var thisColor, dateObject = new Date(tournament.date);
        thisColor = setColor((dateObject.getTime() - NOW.getTime()));
        tournament.color = tournament.expired ? "red" : thisColor;
        tournament.day = thisDay(dateObject);
    }

    function setColor(millisecondDif) {
        var thisIncrument, steps = (432000000 / 51).toFixed(0);
        if (millisecondDif < 0) {
            return "red";
        } else if (millisecondDif >= 432000000) {
            return "green"
        } else {
            thisIncrument = (millisecondDif / steps).toFixed(0);
            thisIncrument = parseInt("ff", 16) - thisIncrument;
            return "#" + thisIncrument.toString(16) + "ff00";
        }
    }

    function thisDay(dateObj) {
        var weekdayMap = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday"
        ];
        return weekdayMap[dateObj.getUTCDay()];
    }


    function formatedDate(inputDate) {
        var today = inputDate;
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!
        var yyyy = today.getFullYear();
        if(dd<10) {
            dd='0'+dd
        }
        if(mm<10) {
            mm='0'+mm
        }
        return  yyyy + '/' + mm + '/' + dd;
    }

    function timePickerDefaults() {
        return {
            hour:11,
            minute:30,
            meridian:"AM"
        };
    }

    $scope.updateTime = function() {
        $scope.newTournament.time = $scope.timePicker;
    };

    $scope.tournamentStatus = function(toggle) {
        if (!toggle) {
            return viewActive ? "active" : "expired";
        } else if (toggle == "switch") {
            viewActive = !viewActive;
        } else if (toggle == "count") {
            return $scope.tournaments.active.length >=1 || $scope.tournaments.expired.length >=1 
        } else if (toggle == "choice") {
            return $scope.tournaments.active.length >=1 && $scope.tournaments.expired.length >=1 
        }
    };

    var myModal, showModal=false,
        modalMap = {
            "newTournament":"new_tournament.html"
        };
    $scope.modalOn = function(toggle) {
        if (!toggle) {
            return showModal;
        } else if (toggle == "myModal") {
            return templatePrefix + modalMap[myModal];
        } else if (toggle == "toggle") {
            showModal = !showModal;
        } else {
            myModal = toggle;
            showModal = !showModal;
        }
    };

    function checkModalStatus() {
        if (rootData.location) {
            $scope.newTournament.location = rootData.location;
            $scope.modalOn("newTournament");
        }
    }
    $scope.formComplete = function() {
        var formIsComplete = false;
        if ($scope.newTournament.name
            && $scope.newTournament.description
            && $scope.newTournament.location
            && $scope.newTournament.type
            && $scope.newTournament.date) {
            formIsComplete = true;
        }
        return formIsComplete;
    };

    $scope.createNewLocation = function() {
        if ($scope.newTournament.name || $scope.newTournament.description) {
            hvbStorage.set("newTournamentData", $scope.newTournament);
        }
        $window.location.href = '/volleyball/editor/new_location?referer=tourn';
    };

    $scope.createTournament = function() {
        if (!$scope.newTournament.time) {
             $scope.newTournament.time = $scope.timePicker;
        }
        hellerVolleyBallService.createNewTournament($scope.newTournament).then(function(results){
            if (results.success) {
                hvbStorage.remove("newTournamentData");
                var thisReturn = results.data;
                $scope.tournaments.active.push(thisReturn.tournament)
                $scope.newTournament = {};
                $scope.timePicker = timePickerDefaults();
                $scope.modalOn("toggle");
            }
        });
    };
}])
.directive('locationMap',
    [
    function() {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var selectedLocation, startCoords, marker;

                function setSelectedLocation() {
                    angular.forEach(scope.locations, function(thisLocal) {
                        if (thisLocal.id == scope.newTournament.location) {
                            selectedLocation = thisLocal;
                        }
                    });
                }

                function updateMap() {
                    if (selectedLocation.lat) {
                        var newCenter = new google.maps.LatLng(parseFloat(selectedLocation.lat), parseFloat(selectedLocation.lon));
                        map.setCenter(newCenter);
                        if (!marker) {
                            marker = new google.maps.Marker({
                                map: map
                            });
                        }
                        marker.setPosition(newCenter);
                        marker.setVisible(true);
                    } else {
                        if (marker) {
                            marker.setVisible(false);
                            marker = null;
                        }
                    }

                }

                setSelectedLocation();


                // MAP DISPLAY FOR LOCATION

                startCoords = selectedLocation ? [parseFloat(selectedLocation.lat), parseFloat(selectedLocation.lon)] : [30.266962, -97.772859];

                var mapdisplay = document.getElementById("map-canvas"),
                    startLocation = new google.maps.LatLng(startCoords[0], startCoords[1]);

                var mapOptions = {
                    center: startLocation,
                    zoom: 13
                };
                var map = new google.maps.Map(mapdisplay,mapOptions);
                if (selectedLocation.lat) {
                    marker = new google.maps.Marker({
                        map: map
                    });
                    marker.setPosition(startLocation);
                    marker.setVisible(true);
                }

                scope.$watch("newTournament.location", function() {
                    if (startCoords) {
                        setSelectedLocation();
                        updateMap();
                    }
                });
            }
        };
    }
]);