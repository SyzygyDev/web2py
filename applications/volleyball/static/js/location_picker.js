var input_lat=document.getElementById("locations_latitude"),
    input_lon=document.getElementById("locations_longitude"),
    input_add=document.getElementById("locations_address"),
    viewport=document.getElementById("viewport"),
    viewfoot=document.getElementById("viewportfoot"),
    trans=document.getElementById("addressresult"),
    mapdisplay=document.getElementById("map_canvas");
var geocoder = new google.maps.Geocoder();
var startLat = input_lat.value || 37.09024;
var startLon = input_lon.value || -95.71289100000001;
var startZoom = 3;
var startMarker = false;
if (input_lat.value && input_lon.value) {
    var startZoom = 14;
    var startMarker = true;
}

var myLatlng = new google.maps.LatLng(startLat,startLon);
var myOptions = {
    zoom: startZoom,
    mapTypeControl: true,
    mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU},
    navigationControl: true,
    navigationControlOptions: {style: google.maps.NavigationControlStyle.SMALL},
    mapTypeId: google.maps.MapTypeId.ROADMAP
}
map = new google.maps.Map(mapdisplay, myOptions);

map.setCenter(myLatlng);

var marker = new google.maps.Marker({
    draggable: true,
    map: map,
    title: "Selected location"
});

var infowindow = new google.maps.InfoWindow({
});

if (startMarker) {
    marker.setPosition(myLatlng);
}

google.maps.event.addListener(marker, 'dragend', function (event) {
    infowindow.close(map,marker);
    input_lat.value = event.latLng.lat();
    input_lon.value = event.latLng.lng();
    map.setCenter(event.latLng);
});

google.maps.event.addListener(marker, 'click', function(event) {
    markerInfo(event.latLng, map.zoom);
    infowindow.open(map,marker);
});

google.maps.event.addListener(map, 'click', function (event) {
    infowindow.close(map,marker);
    marker.setPosition(event.latLng);
    if (map.zoom <= 8) {
        map.setZoom(8);
    }
    input_lat.value = event.latLng.lat();
    input_lon.value = event.latLng.lng();
    map.setCenter(event.latLng);
});

function markerInfo(latLng, mapZoom) {
    geocoder.geocode({'latLng': latLng}, function(results, status) {
        if (mapZoom >= 10) {
            input_add.value = results[0].formatted_address;
            mapAddress = results[0].formatted_address;
            trans.innerHTML = "<span>Address Notes:</span><br /><span>Nearest address from map pin:<br />"
            + results[0].formatted_address + "</span>";
            document.getElementById("input_address").value = mapAddress;
        } else {
            mapAddress = "Zoom in closer for address";

        }
        var infoContent = "<div style='width:125px'>" + mapAddress + "</div>"
        infowindow.setContent(infoContent);
    });
}

function addressTranslation() {
    var input_address = document.getElementById("input_address").value
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
                input_lat.value = latLon.lat();
                startLat = latLon.lat();
                input_lon.value = latLon.lng();
                startLon = latLon.lng();
                input_add.value = results[0].formatted_address;
                startMarker = true;
                trans.innerHTML = "<span>Address Notes:</span><br><span>Latitude and Longitude provided for the "
                + results[0].geometry.location_type + " center of "
                + type_address + ": "
                + results[0].formatted_address + "</span>";
                mapThisAddress(latLon);
            } else {
                trans.innerHTML = "<span>Address Notes:</span><br>More than one address found. Your address translated into more than one location. Try being more specific. Ensure you have the right zip code or city/state, and check to make sure you included street, road, or lane etc.</span>";
            }
        }
    });
    return false;
}

function mapThisAddress(latLon) {
    // var myLatlng = new google.maps.LatLng(input_lat.value,input_lon.value);
    marker.setPosition(latLon);
    map.setCenter(latLon);
    map.setZoom(10);
}
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(mapPosition, noLocation,{enableHighAccuracy:true});
    } else {
        trans.innerHTML="Geolocation is not supported by this browser.";
    }
}

function mapPosition(pos) {
    geocoder = new google.maps.Geocoder();
    input_lat.value= pos.coords.latitude;
    input_lon.value= pos.coords.longitude;
    var latlng = new google.maps.LatLng(pos.coords.latitude,pos.coords.longitude);
    geocoder.geocode({'latLng': latlng}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            trans.innerHTML= "Current Address: " + results[0].formatted_address;
        }
    });
    mapThisAddress(latlng);
}

function noLocation() {
    trans.innerHTML="<input type=\"text\" style=\"height:50px; width:350px; font-size:125%\" name=\"location\"><br>No GPS location data aquired"
}