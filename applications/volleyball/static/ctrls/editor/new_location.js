hellerVolleyBall.controller('HVBAnew_location',
  [        "$scope", "$window", "$rootScope", "$sce", "hellerVolleyBallService",
  function ($scope,   $window,   $rootScope,   $sce,   hellerVolleyBallService) {
    var rootData = $rootScope.rawData;

    $scope.newLocation = {}
    $scope.searchLocation = "";
    $scope.addressMessage = "";
    $scope.photos = [];
    $scope.selectedPhoto = 0;

    $scope.createNewLocation = function() {
        if ($scope.newLocation.lat) {
            $scope.newLocation.lat = $scope.newLocation.lat.toString();
            $scope.newLocation.lon = $scope.newLocation.lon.toString();
        }
        hellerVolleyBallService.createNewLocation($scope.newLocation).then(function(results){
            if (results.success) {
                var thisReturn = results.data;
                if (rootData.referer) {
                    $window.location.href = '/volleyball/editor/index?location=' + thisReturn.locationID;
                } else {
                    $window.location.href = '/volleyball/editor/library';
                }
            }
        });
    };

    $scope.findAddress = function() {
        if ($scope.newLocation.searchAddress) {
            $scope.searchLocation = $scope.newLocation.searchAddress;
        }
    };

    $scope.getPhotoUrl = function(photo) {
        var thisUrl = photo.getUrl({'maxWidth': 350, 'maxHeight': 75});
        photo.photoUrl = thisUrl;
        return $sce.trustAsResourceUrl(thisUrl);
    };

    $scope.setPhotoUrl = function(photo, index) {
        $scope.newLocation.imgUrl = photo.photoUrl;
        $scope.selectedPhoto = index + 1;
    };

    $scope.selectedPhotoUrl = function(photo, index) {
        var imSelected = false;
        if (index + 1 === $scope.selectedPhoto && $scope.newLocation.imgUrl == photo.photoUrl) {
            imSelected = true;
        }
        return imSelected;
    };

    $scope.formComplete = function () {
        var formIsComplete = false;
        if ($scope.newLocation.name && $scope.newLocation.address) {
            formIsComplete = true;
        }
        return formIsComplete;
    };

}])
.directive('locationMap',
    [       "$timeout",
    function($timeout) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var input_search=document.getElementById("pac-input");
                parentData = scope.newLocation;
                scope.$watch('searchLocation', function(){
                    if (scope.searchLocation) {
                        addressTranslation(scope.searchLocation);
                    }
                });
                // MAP DISPLAY FOR NEW LOCATION
                var mapdisplay = document.getElementById("map-canvas"),
                    defaultLocation = new google.maps.LatLng(30.266962, -97.772859);
                var geocoder = new google.maps.Geocoder();

                var mapOptions = {
                    center: defaultLocation,
                    mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU},
                    zoom: 14
                };
                var map = new google.maps.Map(mapdisplay,mapOptions);

                var marker = new google.maps.Marker({
                    draggable: true,
                    map: map,
                    title: "Selected location"
                });
                marker.setPosition(defaultLocation);

                var infowindow = new google.maps.InfoWindow({
                });

                var autocomplete = new google.maps.places.Autocomplete(input_search);
                autocomplete.bindTo('bounds', map);

               google.maps.event.addListener(autocomplete, 'place_changed', function() {
                    infowindow.close(map,marker);
                    // marker.setVisible(false);
                    var place = autocomplete.getPlace();
                    if (!place.geometry) {
                        return;
                    }
                    var latLon = place.geometry.location;
                    var params = {
                        address: place.formatted_address,
                        googlePlaceId: place.place_id
                    };
                    map.setCenter(latLon);
                    marker.setPosition(latLon);
                    if (place.photos && place.photos.length >= 1) {
                        scope.photos = place.photos;
                    }
                    if (place.website) {
                        params.webSite = place.website;
                    } else if (place.url) {
                        params.webSite = place.url;
                    }
                    formUpdate(params, latLon);
                });

                google.maps.event.addListener(marker, 'dragend', function (event) {
                    infowindow.close(map,marker);
                    formUpdate(false, event.latLng)
                    map.setCenter(event.latLng);
                });

                google.maps.event.addListener(marker, 'click', function(event) {
                    markerInfo(event.latLng, map.zoom);
                    infowindow.open(map,marker);
                });

                google.maps.event.addListener(map, 'click', function (event) {
                    infowindow.close(map,marker);
                    marker.setPosition(event.latLng);
                    if (map.zoom <= 10) {
                        map.setZoom(10);
                    }
                    formUpdate(false, event.latLng)
                    map.setCenter(event.latLng);
                });

                function formUpdate(params, latLng, addressMessage, error) {
                    params = params || {};
                    if (latLng) {
                        params.lat = latLng.lat();
                        params.lon = latLng.lng();
                    }
                    $timeout(function() {
                        if (params) {
                            parentData = angular.extend(parentData, params);
                        }
                        scope.addressMessage = addressMessage;
                        scope.error = error;
                    });
                }

                function markerInfo(latLng, mapZoom) {
                    geocoder.geocode({'latLng': latLng}, function(results, status) {
                        mapAddress = results[0].formatted_address;
                        if (mapZoom >= 10) {
                            formUpdate({address:mapAddress}, false, "Nearest address from map pin")
                            // mapAddress = results[0].formatted_address;
                            // scope.addressMessage = "Nearest address from map pin:";
                            // document.getElementById("input_address").value = mapAddress;
                        } else {
                            // scope.addressMessage = "Zoom in closer to verify address";
                            formUpdate(false, false, "Zoom in closer to verify address");
                        }
                        var infoContent = "<div style='width:125px'>" + mapAddress + "</div>"
                        infowindow.setContent(infoContent);
                    });
                }

                function addressTranslation(input_address) {
                    geocoder.geocode({'address': input_address}, function(results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            if (results.length == 1) {
                                if (results[0].types[0] == 'street_address') {
                                    type_address = 'street address';
                                    startZoom = 14;
                                } else if (results[0].types[0] == 'administrative_area_level_3') {
                                    type_address = 'the neighborhood';
                                    startZoom = 12;
                                } else if (results[0].types[0] == 'postal_code') {
                                    type_address = 'the zip code for';
                                    startZoom = 12;
                                } else if (results[0].types[0] == 'locality') {
                                    type_address = 'the city';
                                    startZoom = 10;
                                } else if (results[0].types[0] == 'administrative_area_level_2') {
                                    type_address = 'the county';
                                    startZoom = 8;
                                } else if (results[0].types[0] == 'administrative_area_level_1') {
                                    type_address = 'the state';
                                    startZoom = 6;
                                } else if (results[0].types[0] == 'country') {
                                    type_address = 'the country';
                                } else {
                                    type_address = results[0].types[0];
                                }
                                var latLon = results[0].geometry.location
                                var addressMessage = "Latitude and Longitude provided for the "
                                + results[0].geometry.location_type + " center of "
                                + type_address + ": "
                                + results[0].formatted_address;
                                formUpdate({address:results[0].formatted_address}, latLon, addressMessage);
                                map.setCenter(latLon);
                                marker.setPosition(latLon);
                            } else {
                                var error = "More than one address found. Your address translated into more than one location. Try being more specific. Ensure you have the right zip code or city/state, and check to make sure you included street, road, or lane etc.";
                                formUpdate(false, false, false, error);
                            }
                        }
                    });
                    return false;
                }

                // var marker = new google.maps.Marker({
                //     map: map,
                //     anchorPoint: new google.maps.Point(0, -29)
                // });
                // marker.setPosition(defaultLocation);
                // marker.setVisible(true);
            }
        };
    }
]);