
playersATX.controller('PATXeventpay',
	[        "$scope", "$timeout", "$sce", "$rootScope", "playersATXService",
	function ($scope,   $timeout,   $sce,   $rootScope,   playersATXService) {

		/*
		TEST DATA -
		Visa: 4111111111111111 
		MasterCard: 5431111111111111 
		Discover: 6011601160116611 
		American Express: 341111111111111 
		Credit Card Expiration: 10/25 
		account (ACH): 123123123 
		routing (ACH): 123123123 
		amount 1.00 (Amounts under 1.00 generate failure). 
	    */

	    $scope.safeText = function(textToClean) {
	    	return $sce.trustAsHtml(textToClean || '');
	    };

	    var templatePrefix = "/playersatx/static/tpls/",
	        rootData = $rootScope.rawData,
	        NOW = new Date(),
	        showModal = false;

        var modalMap = {
            "initial": templatePrefix + "checkoutIntial.tpl.html",
            "proceed":  templatePrefix + "checkoutData.tpl.html",
            "process":  templatePrefix + "checkoutFinal.tpl.html",
            "declined":  templatePrefix + "checkoutDeclined.tpl.html",
            "error":  templatePrefix + "checkoutError.tpl.html"
        }

        $scope.imSaving = false;

	    $scope.message = rootData.message || false;
	    $scope.event = rootData.event || false;

	    if ($scope.event && $scope.event.prices) {
	    	$scope.event.prices = convertStrToDecimal($scope.event.prices);
	    }

	    function convertStrToDecimal(prices) {
	    	angular.forEach(prices, function(thisPrice) {
	    		thisPrice.price = Number(thisPrice.price);
	    	});
	    	return prices;
	    }

	    $scope.imageUrl = function(thisImage) {
	    	var URL = "/playersatx/default/download/" + thisImage;
	    	if (!thisImage) {
	    		URL = "/playersatx/static/images/default_image.gif"
	    	}
	    	return URL;
	    };

	    $scope.checkSelectedPrice = function(thisPrice) {
	    	if (!thisPrice.selectedPrice) {
		    	angular.forEach($scope.event.prices, function(somePrice) {
		    		somePrice.selectedPrice = false;
		    	});
		    	thisPrice.selectedPrice = true;
	    	} else {
	    		thisPrice.selectedPrice = !thisPrice.selectedPrice;
	    	}
	    };

	    $scope.checkout = function(action, actionData) {
	    	if (action == "initial") {
	    		$scope.newPurchase = angular.extend($scope.newPurchase, actionData);
	    		showModal = modalMap[action];
	    		StartPageTimeout();
	    	} else if (action == "proceed") {
	    		$scope.newPurchase.billingData = {
	    			"state": "TX"
	    		};
	    		$scope.newPurchase.cardData = {};
	    		showModal = modalMap[action];
	    		StartPageTimeout();
	    	} else if (action == "process") {
	    		$scope.newPurchase.cardData.cleanCCnumber = $scope.newPurchase.cardData.ccnumber.replace(/\D/g,'');
	    		$scope.newPurchase.cardData.thisCard = thisCard;
	        	$scope.imSaving = true;
		    	playersATXService.purchaseEvent($scope.newPurchase).then(function(results){
		    		console.log(results);
		    		if (results.error && results.errorText) {
		    			$scope.error = results.errorText;
		    			showModal = modalMap['error'];
		    		} else {
		    			var successData = results.thisPurchase;
		    			if (successData.successCode == 1) {
		    				$scope.txnSuccess = successData;
		    				showModal = modalMap['process'];
		    			} else {
		    				showModal = modalMap['declined'];
		    			}
		    		}

	        		$scope.imSaving = false;
	            });
	    	}
	    	// showModal = modalMap[action];
	    };

	    $scope.$watch("imSaving", function() {
	    	if ($scope.imSaving) {
	    		createProcessingScope();
	    	}
	    });

	    function createProcessingScope() {
	    	if ($scope.imSaving) {
	    		if (!$scope.processing) {
	    			$scope.processing = "Processing"
	    		} else {
	    			$scope.processing += ".";
	    		}
	    		$timeout(function() {
	    			createProcessingScope();
	    		}, 1000);
	    	} else {
	    		$scope.processing = false;
	    	}
	    }

        $scope.modalOn = function(toggle) {
            if (toggle) {
                if (toggle=="off") {
                	$scope.newPurchase = {};
                	thisCard = "card";
                    showModal = false;
                } else {
                    showModal = modalMap[toggle];
                }
            } else {
                return showModal;
            }
        };

        // *****************PURCHASE STUFF**************
        $scope.newPurchase = {}

        $scope.verifyMemberID = function(memberID) {
        	$scope.imSaving = true;
	    	playersATXService.verifyMemberID(memberID).then(function(results){
		    	if (results.memberInfo) {
		    		$scope.newPurchase = angular.extend($scope.newPurchase, results.memberInfo);
		    		isCouple = $scope.newPurchase.gender == "Couple";
	    		} else {
	    			$scope.newPurchase.status = "invalid";
	    		}
	    		$scope.imSaving = false;
            });
        };

        var isCouple = true;
        $scope.isCouple = function(toggle) {
        	if (!toggle) {
        		return isCouple;
        	} else {
        		isCouple = !isCouple;
        	}
        };

        $scope.purchaseFormCmplt = function(formType) {
        	var isComplete = true;
        	if (formType == "initial") {
	        	if (!$scope.newPurchase.fName || !$scope.newPurchase.lName) {
	        		isComplete = false;
	        	}
	        	if (isCouple && (!$scope.newPurchase.fName1 || !$scope.newPurchase.lName1)) {
	        		isComplete = false;
	        	}
        	} else if (formType == "checkout") {
        		var b = $scope.newPurchase.billingData,
        			c = $scope.newPurchase.cardData
	        	if (!b.firstname || !b.lastname || !b.address1 || !b.city || !b.zip) {
	        		isComplete = false;
	        	}
	        	if (!c.ccnumber || !c.ccExpMonth || !c.ccExpYear || !c.cvv || c.ccnumber.length < 18) {
	        		isComplete = false;
	        	}
        	}
        	return isComplete;
        };

        var thisCard = "card";

        $scope.myCard = function(raw) {
        	var cardMap = {
        		"card": "fa-credit-card",
        		"amex": "fa-cc-amex",
        		"visa": "fa-cc-visa",
        		"mastercard": "fa-cc-mastercard",
        		"discover": "fa-cc-discover"
        	};
        	return raw ? thisCard : cardMap[thisCard];
        };

        $scope.checkMyCard = function() {
        	fieldValue = document.getElementById("cardnumber");
    		var ccNum = $scope.newPurchase.cardData.ccnumber;
    		if (/^(?:[0-9 ]+$)/.test(ccNum)) {
	    		if (ccNum.length == 4 || ccNum.length == 9 ||  ccNum.length == 14) {
	    			fieldValue.value = ccNum + " ";
	    		}
    		} else {
    			fieldValue.value = ccNum.substring(0, ccNum.length - 1);
    		}
    		var isAmex = ccNum.lastIndexOf("34", 0) === 0;
    		isAmex = isAmex || ccNum.lastIndexOf("37", 0) === 0;

    		var isVisa = ccNum.lastIndexOf("4", 0) === 0;

    		var isMasterCard = ccNum.lastIndexOf("51", 0) === 0;
    		isMasterCard = isMasterCard || ccNum.lastIndexOf("52", 0) === 0;
    		isMasterCard = isMasterCard || ccNum.lastIndexOf("53", 0) === 0;
    		isMasterCard = isMasterCard || ccNum.lastIndexOf("54", 0) === 0;
    		isMasterCard = isMasterCard || ccNum.lastIndexOf("55", 0) === 0;

    		var isDiscover = ccNum.lastIndexOf("6011", 0) === 0;
    		isDiscover = isDiscover || ccNum.lastIndexOf("622", 0) === 0;
    		isDiscover = isDiscover || ccNum.lastIndexOf("64", 0) === 0;
    		isDiscover = isDiscover || ccNum.lastIndexOf("65", 0) === 0;

    		if (isAmex) {thisCard = "amex";}
    		else if (isVisa) {thisCard = "visa";}
    		else if (isMasterCard) {thisCard = "mastercard";}
    		else if (isDiscover) {thisCard = "discover";}
    		else {thisCard = "card";}
    	};

    	$scope.lastFour = function() {
    		var ccNum = $scope.newPurchase.cardData.ccnumber;
    		return ccNum.slice(-4);
    	};

    	var myTimer;

    	function StartPageTimeout() {
			var mins = 5;
			var secs = mins * 60;
			$scope.leadingZero = "";
			function decrement() {
				if (!$scope.imSaving) {
					if (secs < 59) {
						$scope.minutes = 0;
						$scope.seconds = secs;
					} else {
						$scope.minutes = getminutes();
						$scope.seconds = getseconds();
					}
					if ($scope.seconds <= 9) {
						$scope.leadingZero = "0";
					} else {
						$scope.leadingZero = "";
					}
					secs--;
					if (secs === 0) {
						window.location.reload();
					}
					if (myTimer) {
						$timeout.cancel(myTimer);
					}
					myTimer = $timeout(function () {
						decrement();
					},1000);
				}
			}
			function getminutes() {
				// minutes is seconds divided by 60, rounded down
				mins = Math.floor(secs / 60);
				return mins;
			}
			function getseconds() {
				// take mins remaining (as seconds) away from total seconds remaining
				return secs-Math.round(mins *60);
			}
			if (myTimer) {
				$timeout.cancel(myTimer);
			}
			myTimer = $timeout(function () {
				decrement();
			},1000);
    	};

    	StartPageTimeout();

        $scope.stateInfo = [
			{"label": "Alabama", "abb": "AL"},
			{"label": "Alaska", "abb": "AK"},
			{"label": "Arizona", "abb": "AZ"},
			{"label": "Arkansas", "abb": "AR"},
			{"label": "California", "abb": "CA"},
			{"label": "Colorado", "abb": "CO"},
			{"label": "Connecticut", "abb": "CT"},
			{"label": "Delaware", "abb": "DE"},
			{"label": "Florida", "abb": "FL"},
			{"label": "Georgia", "abb": "GA"},
			{"label": "Hawaii", "abb": "HI"},
			{"label": "Idaho", "abb": "ID"},
			{"label": "Illinois", "abb": "IL"},
			{"label": "Indiana", "abb": "IN"},
			{"label": "Iowa", "abb": "IA"},
			{"label": "Kansas", "abb": "KS"},
			{"label": "Kentucky", "abb": "KY"},
			{"label": "Louisiana", "abb": "LA"},
			{"label": "Maine", "abb": "ME"},
			{"label": "Maryland", "abb": "MD"},
			{"label": "Massachusetts", "abb": "MA"},
			{"label": "Michigan", "abb": "MI"},
			{"label": "Minnesota", "abb": "MN"},
			{"label": "Mississippi", "abb": "MS"},
			{"label": "Missouri", "abb": "MO"},
			{"label": "Montana", "abb": "MT"},
			{"label": "Nebraska", "abb": "NE"},
			{"label": "Nevada", "abb": "NV"},
			{"label": "New Hampshire", "abb": "NH"},
			{"label": "New Jersey", "abb": "NJ"},
			{"label": "New Mexico", "abb": "NM"},
			{"label": "New York", "abb": "NY"},
			{"label": "North Carolina", "abb": "NC"},
			{"label": "North Dakota", "abb": "ND"},
			{"label": "Ohio", "abb": "OH"},
			{"label": "Oklahoma", "abb": "OK"},
			{"label": "Oregon", "abb": "OR"},
			{"label": "Pennsylvania", "abb": "PA"},
			{"label": "Rhode Island", "abb": "RI"},
			{"label": "South Carolina", "abb": "SC"},
			{"label": "South Dakota", "abb": "SD"},
			{"label": "Tennessee", "abb": "TN"},
			{"label": "Texas", "abb": "TX"},
			{"label": "Utah", "abb": "UT"},
			{"label": "Vermont", "abb": "VT"},
			{"label": "Virginia", "abb": "VA"},
			{"label": "Washington", "abb": "WA"},
			{"label": "West Virginia", "abb": "WV"},
			{"label": "Wisconsin", "abb": "WI"},
			{"label": "Wyoming", "abb": "WY"},
			{"label": "American Samoa", "abb": "AS"},
			{"label": "District of Columbia", "abb": "DC"},
			{"label": "Federated States of Micronesia", "abb": "FM"},
			{"label": "Guam", "abb": "GU"},
			{"label": "Marshall Islands", "abb": "MH"},
			{"label": "Northern Mariana Islands", "abb": "MP"},
			{"label": "Palau", "abb": "PW"},
			{"label": "Puerto Rico", "abb": "PR"},
			{"label": "Virgin Islands", "abb": "VI"},
			{"label": "Armed Forces Africa", "abb": "AE"},
			{"label": "Armed Forces Americas", "abb": "AA"},
			{"label": "Armed Forces Canada", "abb": "AE"},
			{"label": "Armed Forces Europe", "abb": "AE"},
			{"label": "Armed Forces Middle East", "abb": "AE"},
			{"label": "Armed Forces Pacific", "abb": "AP"},
		];
	}]
);