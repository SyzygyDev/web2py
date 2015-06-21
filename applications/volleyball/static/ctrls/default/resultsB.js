hellerVolleyBall.controller('HVBresults',
	[       '$scope', '$rootScope', '$timeout', '$document', 'tournamentGenerator',
	function($scope,   $rootScope,   $timeout,   $document,   tournamentGenerator) {

		$scope.tType='DE';

		var rawData = $rootScope.rawData;
		if (rawData.teams) {
			$timeout(function() {
				$scope.generateWithRandomPlayers();
			}, 1000);
		}

		var adminMode = false;
		$scope.showMeAdmin = function(toggle) {
			if (toggle) {adminMode = !adminMode;} else {return adminMode;}
		};

		$scope.addPlayer = function() {
			if ($scope.newPlayerName) {
				$scope.bracketData.teams.push({
					name: $scope.newPlayerName,
					id: ($scope.bracketData.teams.length + 1).toString(),
					flag: $scope.newPlayerFlag.length > 0 ? $scope.newPlayerFlag + '.png' : '',
					members: []
				});
			}
		};

		$scope.setEnableDetails = function() {
			$scope.bracketData.options.detailsEnabled = $scope.enableDetails;
		};

		$scope.shuffleTeams = function() {
			tournamentGenerator.shuffle($scope.bracketData);
		};

		$scope.loadTeams = function() {
			$scope.bracketData.teams = JSON.parse($scope.teamsJson);
		};

		$scope.generateWithRandomPlayers = function() {
			function generateTeams(size, startFrom) {
				var t = [];
                startFrom = startFrom ? startFrom : 0;
				for (var i = 1; i <= size; i++) {
					t.push({
						name: 'Team ' + (i + startFrom),
						id: (i + startFrom).toString(),
						flag: '',
						members: []
					});
				}

                return t;
			}

			if (rawData.teams) {
				$scope.bracketData.teams = [];
				var n = parseInt(rawData.teams);
                var n2 = parseInt($scope.playersToGenerate2);
				if (n > 3 && (!n2 || n2 > 3)) {
					for (var i = 1; i <= n; i++) {
						$scope.bracketData.teams.push();
					}

                    $scope.bracketData.teams = [];
                    $scope.bracketData.teams.push(generateTeams(n));

                    var t;

                    if(n2 > 3){
                        $scope.bracketData.teams.push(generateTeams(n2, n));
                        t = tournamentGenerator.newTournament($scope.tType, $scope.bracketData.teams, $scope.playBronzeMatch, true);
                        t.conferences[0].conferenceName = 'West';
                        t.conferences[2].conferenceName = 'East';
                    }
                    else
                    {
						t = tournamentGenerator.newTournament($scope.tType, $scope.bracketData.teams[0], $scope.playBronzeMatch, false);
                    }
					
					startTournament(t, $scope.bracketData.teams);
				}
			}
		};

		function startTournament(tournamentData, teams) {
			$scope.bracketData.teams = teams;
			$scope.bracketData.tournament = tournamentData;
			$scope.bracketData.reload();
		}

		$scope.newTournament = function() {
			startTournament(tournamentGenerator.newTournament($scope.tType, $scope.bracketData.teams, $scope.playBronzeMatch), $scope.bracketData.teams);
		};

		$scope.loadTournament = function(sample) {
			if (sample === 'SE') {
				startTournament(SEsampleTournamentData, SEsampleTeamsData);
			} else if (sample === 'DE') {
				startTournament(DEsampleTournamentData, DEsampleTeamsData);
			}
		};

		$scope.onTeamClick = function(event, team) {
			console.log("Team clicked.");
		};

		$scope.onMatchRightClick = function(event, match) {
			console.log("Match right clicked.");
		};

		function showDialog(dialog, targetEl, offsetX, offsetY) {
			if (dialog !== null) {
				if (targetEl !== null && targetEl.getBoundingClientRect()) {
					var div = targetEl.getBoundingClientRect();
					var offsetLeft = div.right + ((window.pageXOffset !== undefined) ? window.pageXOffset : (document.documentElement || document.body.parentNode || document.body).scrollLeft);
					var offsetTop = div.top + ((window.pageYOffset !== undefined) ? window.pageYOffset : (document.documentElement || document.body.parentNode || document.body).scrollTop);
					var targetHeight = div.height;
					var dialogHeight = dialog[0].getBoundingClientRect().height;

					offsetTop += (dialogHeight > targetHeight) ? (dialogHeight / -2) + (targetHeight / 2) : (targetHeight / 2) - (dialogHeight / 2);

					dialog.css('left', (offsetLeft + offsetX) + 'px');
					dialog.css('top', (offsetTop + offsetY) + 'px');
				}

				dialog.css('visibility', 'visible');
			}
		}

		function hideDialog(dialog) {
			if (dialog !== null) {
				dialog.css('visibility', 'hidden');
			}
		}

		function showDetails(event, match) {
			function hide() {
				$scope.detailContainer.unbind('keyup', $scope.detailsHandleKeyUpEvent);
				hideDialog($scope.detailContainer);
				$scope.detailsHandleKeyUpEvent = null;
			}
			$scope.detailsHandleKeyUpEvent = createCloseOnEscEventHandler(this, hide);
			var matchElement = event.currentTarget;

			// Toggle closed
			if ($scope.detailContainer && $scope.detailContainer.css('visibility') == 'visible' && match.matchId == $scope.matchToShow.matchId) {
				hide();
				return;
			}

			if (!$scope.enableDetails || !match.team1 || !match.team2) {
				return;
			}

			$scope.matchToShow = match;
			$scope.$apply();

			if (!$scope.detailContainer) {
				$scope.detailContainer = angular.element(document.getElementById('detailOverlay'));
			}
			if ($scope.detailContainer.length > 0 && matchElement !== null) {
				$document.unbind('keyup', $scope.detailsHandleKeyUpEvent).bind('keyup', $scope.detailsHandleKeyUpEvent);
				showDialog($scope.detailContainer, matchElement, 0, 0);
			}
		}

		$scope.selectTeam = function(team) {
			if ($scope.targetTeamslot) {
				$scope.targetTeamslot.id = team.id;
			}
			hideDialog($scope.teamSelectDialog);
		};

		function hideSelectTeam() {
			$scope.targetTeamslot = null;
			if ($scope.teamSelectDialog !== null) {
				$document.unbind('keyup', $scope.teamselectHandleKeyUpEvent);
				$document.unbind('click', $scope.teamselectHandleClickEvent);
				$scope.teamselectHandleKeyUpEvent = null;
				$scope.teamselectHandleClickEvent = null;
				hideDialog($scope.teamSelectDialog);
			}
		}

		function createCloseOnEscEventHandler(callbackObj, callback) {
			return function(event) {
				if (event.keyCode === 27) {
					callback.call(callbackObj);
				}
			};
		}

		function showSelectTeam(event, team) {

			event.preventDefault();
			event.stopPropagation();
			$scope.teamselectHandleKeyUpEvent = createCloseOnEscEventHandler(this, hideSelectTeam);

			$scope.teamselectHandleClickEvent = function(event) {
				if (event.button !== 2 && !angular.module('ngBracket').findParentByAttribute(event.target, 'id', 'selectTeamOverlay')) {
					hideSelectTeam();
				}
			};

			if ($scope.bracketData.tournament.properties.status !== 'Not started' || !team || !team.id) {
				return;
			}
			if (!$scope.teamSelectDialog) {
				$scope.teamSelectDialog = angular.element(document.getElementById('selectTeamOverlay'));
			}
			if ($scope.teamSelectDialog && $scope.teamSelectDialog.length > 0) {
				$document.unbind('keyup', $scope.teamselectHandleKeyUpEvent).bind('keyup', $scope.teamselectHandleKeyUpEvent);
				$document.unbind('click', $scope.teamselectHandleClickEvent).bind('click', $scope.teamselectHandleClickEvent);

				$scope.targetTeamslot = team;
				showDialog($scope.teamSelectDialog, findParentTeam(event.target), 0, 0);
			}
		}

		function findParentTeam(el) {
			var current = el;
			while (current.parentNode !== null) {
				current = current.parentNode;
				if (current.classList.contains('team')) {
					return current;
				}
			}
		}

		// data object for bracket controller
		$scope.bracketData = {
			teams: [],
			tournament: {
				type: "SE",
				matches: []
			},
			options: {
				onTeamRightClick: showSelectTeam,
				onTeamClick: $scope.onTeamClick,
				onMatchClick: showDetails,
				onMatchRightClick: $scope.onMatchRightClick,
			}
		};
	}
]);