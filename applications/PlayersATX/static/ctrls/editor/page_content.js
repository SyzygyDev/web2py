playersATX.controller('PATXpage_content',
	[        "$scope", "$timeout", "$rootScope", "LocalStorage", "playersATXService",
	function ($scope,   $timeout,   $rootScope,   LocalStorage,   playersATXService) {

	    var templatePrefix = "/playersatx/static/tpls/",
	    	patxStorage = new LocalStorage("page_content"),
	        rootData = $rootScope.rawData,
	        viewSettings = {"filterView":true,"listView":true};

        viewSettings = patxStorage.getObject("eventViewSettings") || viewSettings;

	    $scope.message = rootData.message || false;
	    $scope.events = rootData.events || false;
	    console.log($scope.events);
	    $scope.thisPageID = rootData.thisPageID;
	    setGridEvents();

	    $scope.showFiltered = function(thisEvent) {
	    	if (!thisEvent) {
	    		return viewSettings.filterView;
	    	} else if (thisEvent == 'toggle') {
	    		viewSettings.filterView = !viewSettings.filterView;
	    		patxStorage.set("eventViewSettings", viewSettings);
	    		setGridEvents();
	    	} else {
	    		return !viewSettings.filterView || thisEvent.dateType != "expired"
	    	}
	    };

	    $scope.eventView = function(toggle) {
	    	if (toggle) {
	    		viewSettings.listView=!viewSettings.listView;
	    		patxStorage.set("eventViewSettings", viewSettings);
	    		setGridEvents();
	    	} else {return viewSettings.listView ? "list" : "grid";}
	    };

	    $scope.eventImage = function(thisEvent) {
	    	var URL = "/playersatx/default/download/" + thisEvent.image;
	    	if (!thisEvent.image) {
	    		URL = "/playersatx/static/images/default_image.gif"
	    	}
	    	return URL;
	    };

	    $scope.getEventAction = function(thisEvent, addEvent) {
	    	var URL = "/playersatx/editor/page_content?element_id=" + $scope.thisPageID
	    	if (thisEvent) {
	    		URL += "&setting_id=" + thisEvent.dataID + "&action=edit";
	    	} else {
	    		URL += "&action=add_event";
	    		if (addEvent) {
	    			URL += "&data_id=" + thisEvent.eventID;
	    		}
	    	}
	    	window.location.href = URL;
	    };

	    function setGridEvents() {
	    	$scope.gridEvents = [];
	    	angular.forEach($scope.events, function(thisEvent) {
	    		if (thisEvent.dateType != "expired") {
	    			$scope.gridEvents.push(thisEvent);
	    		} else if (thisEvent.dateType == "expired" && !viewSettings.filterView) {
	    			$scope.gridEvents.push(thisEvent);
	    		}
	    	});
	    }
	}]
);