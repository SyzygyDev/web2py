playersATX.controller('PATXuserModal',
	[        "$scope", "$timeout", "$rootScope", "LocalStorage", "playersATXService",
	function ($scope,   $timeout,   $rootScope,   LocalStorage,   playersATXService) {

	    var templatePrefix = "/playersatx/static/tpls/",
	    	patxStorage = new LocalStorage("page_content"),
	        rootData = $rootScope.rawData;

        $scope.loginInfo = {
        	"email": "",
        	"password": ""
        }

        $scope.logMeIn = function() {
        	// $scope.showModal = !$scope.showModal;
        	playersATXService.logMeIn($scope.loginInfo).then(function(results) {
        		console.log(results);
        	});
        }
        window.iFrameSourceChanged = function(iframe) {
        	var originalUrl = "http://playersatx.club/playersatx/default/userModal2/login";
			if(iframe.contentWindow.location != originalUrl) {
				console.log(iframe.contentWindow.location + " from " + originalUrl);
			} else {
				console.log("unchanged");
			}
		}
	}]
);