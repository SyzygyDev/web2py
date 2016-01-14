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
		var STATES = [
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

		var API_ADDRESS = '/playersatx/';

		function isLoggedIn(json) {
			if (json.data.form) {
				var URL = "/playersatx/default/user/login?_next=" + window.location.href;
				 window.location.href = URL;
			} else {return json;}
		}

		function badCall(json) {
			json.data = {
				"error": json.status,
				"errorText": json.statusText
			};
			return json;
		}

		function apiGet(thisAPI, params) {
			var getURL = API_ADDRESS + thisAPI + '.json';
			//get assumes params are an object, NOT an array
			if (params) {
				getURL += '?';
				angular.forEach(params, function(value, key) {
					getURL += key + '=' + value + '&';
				});
				//remove last anpersand
				getURL = getURL.slice(0, -1);
			}
			return $http.get(getURL).then(isLoggedIn)["catch"](badCall);
		}

		function apiPost(thisAPI, params) {
			var postURL = API_ADDRESS + thisAPI + '.json';
			params = params || {};
			return $http.post(postURL, params).then(isLoggedIn)["catch"](badCall);
		}

		return {
			logMeIn: function(loginData) {
				return apiPost('api_admin/remote_login', loginData).then(function(response) {
					return response.data;
				});
			},
			getStates: function() {
				return STATES;
			},
			createEditPrice: function(params) {
				return apiPost('api_admin/create_edit_price', params).then(function(response) {
					return response.data;
				});
			},
			verifyMemberID: function(memberID, memberName) {
				var params = {"memberID": memberID.toUpperCase(), "name": memberName};
				return apiGet('api_user/verify_member_id', params).then(function(response) {
					return response.data;
				});
			},
			purchaseEvent: function(params) {
				return apiPost('api_user/purchase_event', params).then(function(response) {
					return response.data;
				});
			},
			pullMemberInfo:  function(memberRequest, requestType) {
				memberRequest.requestType = requestType;
				return apiGet('api_admin/get_member_info', memberRequest).then(function(response) {
					return response.data;
				});
			},
			getPurchaseInfo:  function(getData, dataType) {
				params = getData ? {dataType:getData} : false;
				return apiGet('api_admin/get_purchase_info', params).then(function(response) {
					return response.data;
				});
			},

			getCurrentAttendance: function(dateStamp) {
				params = dateStamp ? {"date_stamp": dateStamp} : false
				return apiGet('api_admin/get_attendance_info', params).then(function(response) {
					return response.data;
				});
			},

			checkMemberIn: function(params) {
				return apiGet('api_admin/check_member_in', params).then(function(response) {
					return response.data;
				});
			},

			createNewMember: function(newMemberData, action) {
				newMemberData = action ? angular.extend(newMemberData, {"action": action}) : newMemberData;
				return apiPost('api_admin/new_member', newMemberData).then(function(response) {
					return response.data;
				});
			},

			editMember: function(memberData, logData) {
				memberData = angular.extend(memberData, {"logData": logData});
				return apiPost('api_admin/edit_member', memberData).then(function(response) {
					return response.data;
				});
			},

			staffLogs: function(params) {
				return apiGet('api_admin/get_staff_logs', params).then(function(response) {
					return response.data;
				});
			},

			memberCredit: function(params) {
				params.action = params.action || "create";
				return apiGet('api_admin/member_credit', params).then(function(response) {
					return response.data;
				});
			},

			getPurchaseSummary: function() {
				return apiGet('api_admin/purchase_info').then(function(response) {
					return response.data;
				});
			},

			getExecVpList: function(params) {
				return apiGet('api_admin/get_vp_list', params).then(function(response) {
					return response.data;
				});
			},

			saveComment: function(commentObj) {
				return apiPost('api_admin/add_member_comment', commentObj).then(function(response) {
					return response.data;
				});
			}
		};

	}]
)
.directive('makeItSquare',
	[       "$timeout",
	function($timeout){
	return {
		restrict: 'A',
		scope: {
			childSet: '@makeItSquare',
		},
		link: function (scope, $elem) {
			var image, nImg, nWidth, nHeight, elementHeight, divWidth, adjustment, marginSettings;
			if (scope.childSet == "image") {
				image = angular.element($elem[0].getElementsByTagName('img'));
			}

			function setHeight(){
				divWidth = $elem[0].getBoundingClientRect().width;
				elementHeight = divWidth + 'px';
				$elem.css('height', elementHeight);
				if (image) {
					letterBoxMe(image, divWidth);
				}
			}

			// FUNCTION FOR IE8 SUPPORT
			function getOldBrowserNatural (thisImage) {
				var img = new Image();
				img.src = thisImage.src;
				return {
					width: img.width,
					height: img.height
				};
			}

			function letterBoxMe(thisImage, squareSize) {
				if (thisImage.prop("complete")) {
					processImage(thisImage, squareSize, thisImage[0]);
				} else {
					thisImage.bind("load" , function(){
						processImage(thisImage, squareSize, this);
					});
				}
				
			}

			function processImage(thisImage, squareSize, thisStuff) {
				if ('naturalWidth' in thisStuff) {
					nWidth = thisStuff.naturalWidth;
					nHeight = thisStuff.naturalHeight;
				} else {
					// THIS IS FOR IE8 FALL BACK
					nImg = getOldBrowserNatural(thisImage);
					nWidth = nImg.width;
					nHeight = nImg.height;
				}

				// TODO - NEED TO INCLUDE PADDING ADJUSTMENTS FOR THIS

				if (nWidth > nHeight) {
					adjustment = squareSize/nWidth;
					marginSettings = (squareSize-(adjustment*nHeight))/2;
					thisImage.css('width', squareSize + 'px');
					thisImage.css('height', 'auto');
					thisImage.css('margin-top', marginSettings + 'px');
					thisImage.css('margin-bottom', marginSettings + 'px');

				} else if (nWidth < nHeight) {
					adjustment = squareSize/nHeight;
					marginSettings = (squareSize-(adjustment*nWidth))/2;
					thisImage.css('width', 'auto');
					thisImage.css('height', squareSize + 'px');
					thisImage.css('margin-left', marginSettings + 'px');
					thisImage.css('margin-right', marginSettings + 'px');
				} else {
					thisImage.css('width', '100%');
					thisImage.css('height', '100%');
				}
			}

			$timeout(function(){

				angular.element(window).on('resize', setHeight);

				setHeight();
			});
		}
	};
}])
.factory("LocalStorage",
  [       "$window", "$log", "Class",
  function($window,   $log,   Class) {

  // Since we may use localStorage on a client domain, all keys we store in localStorage get
  // scoped with the "_shar." prefix to reduce the chance of collisions.
  var PATX_PREFIX = "_PATX.";

  // Since localStorage stores everything as a String, boolean values would be stored as
  // "true" and "false" by default.  There's really no reason to use up unnecessary space
  // to store the words "true" and "false", so instead this class stores boolean values as
  // "T" and "F".  Since localStorage is limited (and there is no mechanism to increase the
  // available storage), every character counts.
  var TRUE = "T";
  var FALSE = "F";

  var localStorage = $window && $window['localStorage'];
  if (!localStorage) {
	$log.error("Local Storage is not supported on this browser.");
  }

  // angular.fromJson bound to angular so that it can be passed around as a function.
  var parseJson = angular.bind(angular, angular.fromJson);

  // Generates the fully scoped key name.
  //
  // scopeKey is a private function that is invoked using scopeKey.call(localStorageInstance, key);
  function scopeKey(key) {
	return !key ? null : this.prefix + key;
  }

  function getParsedValue(key, parseFunc, type, defaultValue) {
	var value = this.get(key);
	if (value) {
	  try {
		return parseFunc.call(this, value);
	  } catch(e) {
		$log.warn("Unable to parse ", value, " as a ", type, "  Returning defalut value: ", defaultValue);
	  }
	}

	return defaultValue;
  }

  var LocalStorage = Class.extend({
	init: function(prefix) {
	  if (!prefix || !angular.isString(prefix)) {
		throw new Error("Local storage key prefix must be a non-empty string: received prefix=" + prefix);
	  }

	  this.prefix = PATX_PREFIX + prefix;
	  // Ensure that this.prefix always ends in a "."
	  if (prefix.charAt(prefix.length - 1) !== ".") {
		this.prefix += ".";
	  }
	},

	get: function(key) {
	  var scopedKey = scopeKey.call(this, key);
	  if (!scopedKey || !localStorage) {
		return null;
	  }

	  return localStorage[scopedKey];
	},

	getBoolean: function(key, defaultValue) {
	  var value = this.get(key);
	  return (value && value !== FALSE) || (defaultValue || false);
	},

	getInteger: function(key, defaultValue) {
	  return getParsedValue.call(this, key, parseInt, "integer", defaultValue);
	},

	getFloat: function(key, defaultValue) {
	  return getParsedValue.call(this, key, parseFloat, "float", defaultValue);
	},

	getObject: function(key, defaultValue) {
	  return getParsedValue.call(this, key, parseJson, "json", defaultValue);
	},

	getDate: function(key, defaultValue) {
	  var value = getParsedValue.call(this, key, parseInt, "integer", -1);
	  return value === -1 ? defaultValue : new Date(value);
	},

	set: function(key, value) {
	  if (angular.isUndefined(value) || value === null) {
		this.remove(key);
	  }

	  var fullKey = scopeKey.call(this, key);
	  if (!fullKey) {
		return;
	  }

	  var storeValue = value;
	  if (typeof value === "boolean") {
		storeValue = value ? TRUE : FALSE;
	  } else if (angular.isArray(value) || angular.isObject(value)) {
		storeValue = angular.toJson(value, false);
	  } else if (angular.isDate(value)) {
		// Store dates as number of milliseconds since epoch since that is shorter
		// than storing the date formatted as a string.
		storeValue = +value;
	  }

	  localStorage[fullKey] = storeValue;
	},

	remove: function(key) {
	  var fullKey = scopeKey.call(this, key);
	  if (!fullKey) {
		return;
	  }

	  localStorage.removeItem(fullKey);
	}
  });

  return LocalStorage;

}]).factory("Class", function() {
  var initializing = false,
	fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;

  var Class = function(){};

  Class.extend = function(prop) {
	var _super = this.prototype;

	initializing = true;
	var prototype = new this();
	initializing = false;

	for (var name in prop) {
	  prototype[name] = typeof prop[name] == "function" &&
		typeof _super[name] == "function" && fnTest.test(prop[name]) ?
		(function(name, fn){
		  return function() {
			var tmp = this._super;
			this._super = _super[name];
			var ret = fn.apply(this, arguments);        
			this._super = tmp;
			return ret;
		  };
		})(name, prop[name]) :
		prop[name];
	}

	function Class() {
	  if ( !initializing && this.init )
	  this.init.apply(this, arguments);
	}

	Class.prototype = prototype;
	Class.prototype.constructor = Class;
	Class.extend = arguments.callee;
	return Class;
  };
  return Class;
});
