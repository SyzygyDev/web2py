
var hellerVolleyBall = angular.module('hellerVolleyBall', []);

hellerVolleyBall.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{!');
    $interpolateProvider.endSymbol('!}');
});

hellerVolleyBall.factory("hellerVolleyBallService",
    [       "$q", "$http",
    function($q,   $http) {
        var API_ADDRESS = '/volleyball/api_volley/';

        function apiGet(thisAPI, params) {
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

        function apiPost(thisAPI, params) {
            var postURL = API_ADDRESS + thisAPI + '.json';
            params = params || {};
            return $http.post(postURL, params);
        }

        return {
            getTournaments: function() {
                return apiGet('get_tournaments').then(function(response) {
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
                thisImage.bind("load" , function(e){
                    if ('naturalWidth' in this) {
                        nWidth = this.naturalWidth;
                        nHeight = this.naturalHeight;
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
                });
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
  var SHAR_PREFIX = "_shar.";

  // Since localStorage stores everything as a String, boolean values would be stored as
  // "true" and "false" by default.  There's really no reason to use up unnecessary space
  // to store the words "true" and "false", so instead this class stores boolean values as
  // "T" and "F".  Since localStorage is limited (and there is no mechanism to increase the
  // available storage), every character counts.
  var TRUE = "T";
  var FALSE = "F";

  // Get reference to browser's localStorage interface.  If not available, then an error is logged
  // and all methods on LocalStorage instances will be no-ops.  All of the browser's that we support
  // have support for localStorage, so this will only be an issue for non-supported browsers.
  // It's important that we do not throw errors on unsupported browsers.  The experience will
  // obviously be degraded in some way, but we do not want to entirely prevent the user from using
  // the app.
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

  /**
   * Parses the value of the given key using the provided parse function.
   * If successfully parsed, the parsed value is returned.  If the value is
   * not set or if the value cannot be parsed, then the defaultValue is returned.
   */
  // Private function - this is an instance of LocalStorage class.
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

      this.prefix = SHAR_PREFIX + prefix;
      // Ensure that this.prefix always ends in a "."
      if (prefix.charAt(prefix.length - 1) !== ".") {
        this.prefix += ".";
      }
    },

    /**
     * Gets an unparsed value from localStorage.  If localStorage is not supported,
     * then null is returned.
     */
    get: function(key) {
      var scopedKey = scopeKey.call(this, key);
      if (!scopedKey || !localStorage) {
        return null;
      }

      return localStorage[scopedKey];
    },

    /**
     * Gets the
     */
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

}]);

hellerVolleyBall.factory("Class", function() {
  // Source: http://ejohn.org/blog/simple-javascript-inheritance/
  /*
   * Simple JavaScript Inheritance
   * By John Resig http://ejohn.org/
   * MIT Licensed.
   */
  // Inspired by base2 and Prototype
  var initializing = false,
    fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;

  // The base Class implementation (does nothing)
  var Class = function(){};

  // Create a new Class that inherits from this class
  Class.extend = function(prop) {
    var _super = this.prototype;

    // Instantiate a base class (but only create the instance,
    // don't run the init constructor)
    initializing = true;
    var prototype = new this();
    initializing = false;

    // Copy the properties over onto the new prototype
    for (var name in prop) {
      // Check if we're overwriting an existing function
      prototype[name] = typeof prop[name] == "function" &&
        typeof _super[name] == "function" && fnTest.test(prop[name]) ?
        (function(name, fn){
          return function() {
            var tmp = this._super;

            // Add a new ._super() method that is the same method
            // but on the super-class
            this._super = _super[name];
             
            // The method only need to be bound temporarily, so we
            // remove it when we're done executing
            var ret = fn.apply(this, arguments);        
            this._super = tmp;
             
            return ret;
          };
        })(name, prop[name]) :
        prop[name];
    }

    // The dummy class constructor
    function Class() {
      // All construction is actually done in the init method
      if ( !initializing && this.init )
      this.init.apply(this, arguments);
    }

    // Populate our constructed prototype object
    Class.prototype = prototype;

    // Enforce the constructor to be what we expect
    Class.prototype.constructor = Class;

    // And make this class extendable
    Class.extend = arguments.callee;

    return Class;
  };

  return Class;
});