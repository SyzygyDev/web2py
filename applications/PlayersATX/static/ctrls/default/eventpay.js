
playersATX.controller('eventpay',
	[        "$scope", "$rootScope", "playersATXService",
	function ($scope,   $rootScope,   playersATXService) {

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

	    var templatePrefix = "/volleyball/static/tpls/",
	        rootData = $rootScope.rawData,
	        NOW = new Date();

	    $scope.message = rootData.message || false;
	    // $scope.loginFailed = rootData.login || false;
	    
	    // var iAmAMember = true;
	    // $scope.alreadyAMember = function(member) {
	    //     if (member == "toggle") {
	    //         iAmAMember = !iAmAMember;
	    //     }
	    //     if (!member) {return iAmAMember;}
	    // };

	    // hellerVolleyBallService.getTournaments().then(function(results){
	    //     if (results.success) {
	    //         var thisReturn = results.data;
	    //         $scope.tournaments = thisReturn.tournaments;
	    //         preProcess($scope.tournaments);
	    //         $scope.locations = thisReturn.locations;
	    //     }
	    // });

	    // function preProcess(tournaments) {
	    //     if (tournaments.active && tournaments.active.length >= 1) {
	    //         angular.forEach(tournaments.active, function(thistourny) {
	    //             processTournament(thistourny);
	    //         });
	    //     }
	    //     if (tournaments.expired && tournaments.expired.length >= 1) {
	    //         angular.forEach(tournaments.expired, function(thistourny) {
	    //             processTournament(thistourny);
	    //         });
	    //     }
	    // }

	    // function processTournament(tournament) {
	    //     var thisColor, dateObject = new Date(tournament.date);
	    //     thisColor = setColor((dateObject.getTime() - NOW.getTime()));
	    //     tournament.color = tournament.expired ? "red" : thisColor;
	    //     tournament.day = thisDay(dateObject);
	    // }

	    // function setColor(millisecondDif) {
	    //     var thisIncrument, steps = (432000000 / 51).toFixed(0);
	    //     if (millisecondDif < 0) {
	    //         return "red";
	    //     } else if (millisecondDif >= 432000000) {
	    //         return "green"
	    //     } else {
	    //         thisIncrument = (millisecondDif / steps).toFixed(0);
	    //         thisIncrument = parseInt("ff", 16) - thisIncrument;
	    //         return "#" + thisIncrument.toString(16) + "ff00";
	    //     }
	    // }

	    // function thisDay(dateObj) {
	    //     var weekdayMap = [
	    //         "Sunday",
	    //         "Monday",
	    //         "Tuesday",
	    //         "Wednesday",
	    //         "Thursday",
	    //         "Friday",
	    //         "Saturday"
	    //     ];
	    //     return weekdayMap[dateObj.getUTCDay()];
	    // }
	}]
);