playersATX.controller('PATXadmin',
	[        "$scope", "$timeout", "$rootScope", "LocalStorage", "playersATXService",
	function ($scope,   $timeout,   $rootScope,   LocalStorage,   playersATXService) {
		$scope.isAdmin = true;

		function varType(thisVar) {
			var objType = Object.prototype.toString.call( thisVar )
			if ( objType === "[object Array]") {
				return "array";
			} else if ( objType === "[object Object]") {
				return "object";
			} else {
				return "var";
			}
		}

	    var templatePrefix = "/playersatx/static/tpls/",
	    	patxStorage = new LocalStorage("page_content"),
	        NOW = new Date(),
			typeTimer,
	        rootData = $rootScope.rawData,
	        changeDetected = false,
	        showModal = false;

        var pages = rootData.pages;

        var modalMap = {
            "newMember": templatePrefix + "adminNewMember.tpl.html",
            "addComp": templatePrefix + "adminComp.tpl.html"
        }
        
		$scope.genderOptions =  rootData.genderOptions;
		$scope.memberTypeOptions = rootData.memberTypeOptions;

        $scope.modalOn = function(toggle) {
            if (toggle) {
                if (toggle=="off") {
                    showModal = false;
                } else {
                    showModal = modalMap[toggle];
                }
            } else {
                return showModal;
            }
        };
        
        $scope.stateInfo = playersATXService.getStates();

        $scope.pageSettings = rootData.pageData;
        $scope.users = rootData.users;
		$scope.currentMember = "";
		$scope.memberRequest = {};

		function setNewMemberTemplate(newMemberID, genOpt, memTypeOpt) {
			$scope.genderOptions = genOpt;
			$scope.memberTypeOptions = memTypeOpt;
			$scope.newMember = {
				"gender": 1,
				"memberType": 1,
				"memberID": newMemberID,
				"state": "TX"
			};
		}

        $scope.activePage = function(pageID, toggle) {
        	if (!toggle) {
        		return pageID == $scope.pageSettings.id
        	} else {
        		angular.forEach(pages, function(page) {
        			if (page.id == pageID) {
        				$scope.pageSettings = page;
        				if (pageID == 7) {
        					getPurchases();
        				}
        			}
        		});
        	}
        };

        $scope.createNewMember = function(action) {
        	if (action == "initial") {
				setNewMemberTemplate(rootData.newMemberID, rootData.genderOptions, rootData.memberTypeOptions);
				$scope.modalOn("newMember");
        	} else if (action == "save") {
				playersATXService.createNewMember($scope.newMember, "admin_new").then(function(result) {
					if (result.newMember) {
						rootData.newMemberID = result.newMember.newMemberID;
						rootData.genderOptions = result.newMember.genderOptions;
						rootData.memberTypeOptions = result.newMember.memberTypeOptions;
						$scope.modalOn("off");
					}
					processMemberInfo(result);
				});
        	} else if (action == "cancel") {
				setNewMemberTemplate(rootData.newMemberID, rootData.genderOptions, rootData.memberTypeOptions);
				$scope.modalOn("off");
        	}
        };

        $scope.toggleEditMode = function(objectToEdit, action) {
        	if (action == "cancel") {
        		$scope.currentMember = angular.copy($scope.originalCurrentMember);
        	} else if (action == "save") {
        		var logData = $scope.formHasChanged("getLog");
				playersATXService.editMember($scope.currentMember, logData).then(function(result) {
					objectToEdit.editMode = !objectToEdit.editMode;
					$scope.originalCurrentMember = angular.copy($scope.currentMember);
				});
        	} else {
        		objectToEdit.editMode = !objectToEdit.editMode;
        	}
        };

		$scope.showDuplicates = function() {
			$scope.dupOpen = !$scope.dupOpen;
		};

		$scope.checkIDEntered = function() {
			if (typeTimer) {
				$timeout.cancel(typeTimer);
			}
			typeTimer = $timeout(function() {
				getMemberInfo();
			}, 600);
		};

		$scope.checkLastNameEntered = function() {
			if($scope.memberRequest.checkLastName) {
				getMemberInfo("lastName");
			}
		};

		$scope.getMemberKey = function(memberID) {
			$scope.memberRequest.checkID = memberID;
			getMemberInfo();
		};

		$scope.formHasChanged = function(flag) {
			if (flag == "check") {
				return changeDetected;
			} else {
				var logData = "", formHasChanged = false;
				for (var key in $scope.currentMember) {
					if (key != "editMode") {
						if (varType($scope.currentMember[key]) !== "array") {
							if (varType($scope.currentMember[key]) === "object" ) {
								for (var subKey in $scope.currentMember[key]) {
									formHasChanged = formHasChanged ? formHasChanged : $scope.currentMember[key][subKey] == $scope.originalCurrentMember[key][subKey];
									if ($scope.currentMember[key][subKey] != $scope.originalCurrentMember[key][subKey]) {logData += " " + key + "." + subKey + ",";}
								}
							} else {
								formHasChanged = formHasChanged ? formHasChanged : $scope.currentMember[key] == $scope.originalCurrentMember[key];
								if ($scope.currentMember[key] != $scope.originalCurrentMember[key]) {logData += " " + key + ",";}
							}
						}
					}
				}
				changeDetected = formHasChanged;
			}
			if (flag == "getLog") {
				return logData.substring(0, logData.length - 1);
			}
		};

		function getPurchases() {
			$scope.imSaving = true;
			playersATXService.getPurchaseSummary().then(function(result) {
				$scope.purchases = result.purchaseData.purchases;
				$scope.summaries = result.purchaseData.summary;
			});
		}

		function getMemberInfo(requestType) {
			$scope.imSaving = true;
			requestType = requestType || "memberID";
			playersATXService.pullMemberInfo($scope.memberRequest, requestType).then(function(result) {
				processMemberInfo(result);
			});
		}

		function processMemberInfo(result) {
			if ( Object.prototype.toString.call( result.memberData ) === '[object Array]' ) {
				$scope.memberList = result.memberData;
				$scope.currentMember = "";
				$scope.memberRequest.checkID = "";
			} else {
				$scope.originalCurrentMember = result.memberData;
				if ($scope.originalCurrentMember.purchases) {
					$scope.originalCurrentMember.purchases = makeDateObjects($scope.originalCurrentMember.purchases);
				}
				$scope.currentMember = angular.copy($scope.originalCurrentMember);
				$scope.memberList = "";
				$scope.memberRequest.checkLastName = "";
			}
			if (result.duplicateMembers) {
				$scope.duplicateMembers = result.duplicateMembers;
			} else {
				$scope.duplicateMembers = false;
			}
			$scope.dupOpen = false
			$scope.imSaving = false;
		}

		function makeDateObjects(purchases) {
			var nowDate = NOW.getDate(), adjustedDate;
			angular.forEach(purchases, function(purchase) {
				for (var k in purchase){
					if (k == "eventDate") {
						purchase[k] = new Date(purchase[k]);
						purchase[k] = purchase[k].addHours((purchase[k].getTimezoneOffset() / 60));
						adjustedDate = angular.copy(purchase[k]);
						adjustedDate = adjustedDate.addHours(3).getUTCDate()
						if (nowDate == adjustedDate) {
							purchase.status = "current";
						} else if (nowDate > adjustedDate) {
							purchase.status = "expired";
							if (Math.abs(nowDate - adjustedDate) > 4) {
								purchase.status = false;
							}
						} else if (nowDate < adjustedDate) {
							purchase.status = "pending";
							if (Math.abs(nowDate - adjustedDate) > 4) {
								purchase.status = "purchased";
							}
							// if (NOW.getDate() < purchase[k].addHours(104).getUTCDate()) {
							// 	purchase.status = "purchased";
							// }
						}
					}
				}
			});
			return purchases;
		}

// **********************ATTENDANCE******************
		$scope.getAttendance = function(searchDate) {
			playersATXService.getCurrentAttendance(searchDate).then(function(results) {
				$scope.attendance = results.attendance;
			});
		};

// **********************FREE COMPS******************
		$scope.addComp = function(action) {
			if (!action) {
				$scope.newComp = {
					"memberID": $scope.currentMember.id,
					"creditType": ""
				};
				$scope.modalOn("addComp");
			} else {
				playersATXService.memberCredit($scope.newComp).then(function(results) {
					$scope.currentMember.credits = results.memberCredits;
					$scope.modalOn("off");
				});
			}
		};

// **********************STAFF LOGS******************
		$scope.getStaffAction = function(range, staffID) {
			var params = {"range": range || "day"};
			if (staffID) {
				params.staffer = staffID;
			}
			playersATXService.staffLogs(params).then(function(results) {
				if (results.changeLog) {
					$scope.staffChanges = staffDates(results.changeLog);
					$scope.noLogs = false;
				} else {$scope.noLogs = true;}
			});
		};

		function staffDates(staffArray) {
			angular.forEach(staffArray, function(thisStaff) {
				thisStaff.actionDate = new Date(thisStaff.actionDate);
				thisStaff.actionDate = thisStaff.actionDate.subtractHours(thisStaff.actionDate.getTimezoneOffset() / 60)
			});
			return staffArray;
		}

		Date.prototype.addHours= function(h){
			this.setHours(this.getHours()+h);
			return this;
		}

		Date.prototype.subtractHours= function(h){
			this.setHours(this.getHours()-h);
			return this;
		}
	}]
);