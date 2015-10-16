playersATX.controller('PATXupdate',
	[        "$scope", "$timeout", "$rootScope", "LocalStorage", "playersATXService",
	function ($scope,   $timeout,   $rootScope,   LocalStorage,   playersATXService) {

	    var templatePrefix = "/playersatx/static/tpls/",
	        rootData = $rootScope.rawData;

	    $scope.images = rootData.images ? processImageDates(rootData.images) : false;
	    $scope.events = rootData.events || false;
	    $scope.thisPageID = rootData.thisPageID;
	    if ($scope.events.prices) {
	    	$scope.events.prices = convertStrToDecimal($scope.events.prices);
	    	$scope.oldPrices = angular.copy($scope.events.prices);
	    }

	    function convertStrToDecimal(prices) {
	    	angular.forEach(prices, function(thisPrice) {
	    		thisPrice.price = Number(thisPrice.price);
	    	});
	    	return prices;
	    }

	    $scope.imageUrl = function(thisImage) {
	    	var URL = "/playersatx/default/download/" + thisImage.image_file;
	    	if (!thisImage.image_file) {
	    		URL = "/playersatx/static/images/default_image.gif"
	    	}
	    	return URL;
	    };

	    $scope.getEventAction = function(thisImage) {
	    	var URL = "/playersatx/editor/update?page_id=" + $scope.thisPageID
	    	if (thisImage) {
	    		URL += "&element_id=" + thisImage.id;
	    	}
	    	window.location.href = URL;
	    };

	    function processImageDates(images) {
	    	angular.forEach(images, function(thisImage) {
	    		thisImage.created = thisImage.created ? new Date(thisImage.created) : null;
	    		thisImage.modified = thisImage.modified ? new Date(thisImage.modified) : null;
	    	});
	    	return images;
	    }

	    // ******************FOR EVENT WEBPAY***************

	    $scope.newPrice = {};

	    $scope.createNewPrice = function() {
	    	var params = {
	    		"action": "create",
	    		"eventID": $scope.events.eventID,
	    		"priceData": $scope.newPrice
	    	};
	    	priceAPICall(params);
	    };

	    $scope.checkForChanges = function(thisPrice) {
	    	var elementHasChanged = false;
	    	angular.forEach($scope.oldPrices, function(oldPrice) {
	    		if (oldPrice.id == thisPrice.id) {
	    			for (var key in oldPrice) {
	    				if (!elementHasChanged) {
	    					elementHasChanged = thisPrice[key] != oldPrice[key];
	    				}
					}
	    		}
	    	});
	    	return elementHasChanged;
	    };

	    $scope.editPrice = function(thisPrice, action) {
	    	var params = {
	    		"action": action || "edit",
	    		"eventID": $scope.events.eventID,
	    		"priceData": thisPrice
	    	};
	    	priceAPICall(params);
	    };

	    $scope.getOldPriceAndLabel = function(price, type) {
	    	var thisReturn;
	    	angular.forEach($scope.oldPrices, function(thisPrice) {
    			if (thisPrice.id == price.id) {
    				thisReturn = thisPrice[type];
    			}
    		});
    		return thisReturn;
		};

	    function priceAPICall(params) {
	    	playersATXService.createEditPrice(params).then(function(results){
		    	if (!$scope.events.prepay) {
		    		$scope.events.prepay = true;
		    		$scope.events.priceAddMode = true;
		    	}
	    		if (results.prices) {
		    		$scope.events.prices = convertStrToDecimal(results.prices);
		    		$scope.oldPrices = angular.copy($scope.events.prices)
	    		} else if (params.action != "edit") {
	    			$scope.events.prepay = false;
	    			$scope.events.prices = false;
	    		}
		    	$scope.newPrice = {};
		    	if (params.action == "edit") {
		    		$scope.events.priceAddMode = false;
		    		$scope.oldPrices = angular.copy($scope.events.prices)
		    		// angular.forEach($scope.events.prices, function(thisPrice) {
		    		// 	if (thisPrice.id == params.priceData.id) {
		    		// 		thisPrice.editMode = true;
		    		// 	}
		    		// });
		    	}
            });
	    }

	    $scope.eventPayEdit = function(thisData, closeList) {
	    	if (closeList) {
	    		$scope.events.priceAddMode = false;
	    		angular.forEach(closeList, function(thisItem, index) {
	    			thisItem.label = angular.copy($scope.oldPrices[index].label);
	    			thisItem.price = angular.copy($scope.oldPrices[index].price);
	    			thisItem.editMode = false;
	    		});
	    	}
	    	if (thisData != "off") {
	    		thisData.editMode = !thisData.editMode;
	    	}
	    };

	    $scope.priceAddMode = function(thisEvent) {
	    	thisEvent.priceAddMode = !thisEvent.priceAddMode;
	    };
	}]
);