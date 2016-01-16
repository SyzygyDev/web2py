playersATX.controller('PATXfront_desk',
	[        "$scope", "$timeout", "$rootScope", "LocalStorage", "playersATXService",
	function ($scope,   $timeout,   $rootScope,   LocalStorage,   playersATXService) {

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
			patxStorage = new LocalStorage("front_desk"),
			rootData = $rootScope.rawData,
	        NOW = new Date(),
			typeTimer,
	        showModal = false,
	        changeDetected = false;
	        
        $scope.iAmOfAge = 1900 + NOW.getYear() - 17;

        var modalMap = {
            "checkIn": templatePrefix + "checkMemberIn.tpl.html",
            "verifyMember":  templatePrefix + "verifyNewMember.tpl.html",
            "newMember": templatePrefix + "newMember.tpl.html"
        }

        $scope.stateInfo = playersATXService.getStates();

		$scope.currentMember = "";
		$scope.memberRequest = {};
		$scope.viewPane = "members";
		$scope.attendance = rootData.attendance;
		$scope.user = rootData.user;

		$scope.panelSettings = function(panelValue) {
			var thisValue = false,
				settingsMap = {
				"members": {"heading": "Members", "template": templatePrefix + "FDmembers.tpl.html"},
				"execVp": {"heading": "Executive VIP Check-in", "template": templatePrefix + "FDExecCheckIn.tpl.html"},
				"purchase": {"heading": "Completed Purchases for this weekend", "template": templatePrefix + "FDpurchases.tpl.html"},
				"attendance": {"heading": "Current Attendance", "template": templatePrefix + "FDattendance.tpl.html"},
			};
			return settingsMap[$scope.viewPane] && settingsMap[$scope.viewPane][panelValue];
		};

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

// **************************MEMBER STUFF******************************

        $scope.toggleEditMode = function(objectToEdit, action) {
        	
        	if (action == "cancel") {
        		$scope.currentMember = angular.copy($scope.originalCurrentMember);
        		objectToEdit.editMode = !objectToEdit.editMode;
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

		function setNewComment() {
			$scope.newComment = {
				"comment": "",
				"revoke": false,
				"memberID": 0
			};
		}

		setNewComment();
		var commentFormChanged = false;

		$scope.showCommentForm = function(member) {
			member.showCommentForm = !member.showCommentForm;
			if (member.showCommentForm) {
				$scope.newComment.memberID = member.id;
				$scope.oldComment = angular.copy($scope.newComment);
			}
		};

		$scope.commentFormChanged = function(check) {
			if (check) {
				return commentFormChanged;
			} else {
				commentFormChanged = ($scope.newComment.comment != $scope.oldComment.comment);
			}
		};

		$scope.saveComment = function(member) {
			var saveThisComment = false,
				message = "Are you sure you want to revoke this member?\nThis can only be undone by a manager";
			if ($scope.newComment.revoke) {
				if (confirm(message)) {
					saveThisComment = true;
				}
			} else {
				saveThisComment = true;
			}
			if (saveThisComment) {
				playersATXService.saveComment($scope.newComment).then(function (response) {
					if (response.error) {
						alert(response.error);
					} else {
						member.comments = response.comments;
					}
					if ($scope.newComment.revoke) {
						member.status = 'Revoked';
						member.memberType = 'Revoked';
					}
					setNewComment();
					member.showCommentForm = false;
				})
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

		function getMemberInfo(requestType) {
			$scope.imSaving = true;
			var thisRequest = false;
			requestType = requestType || "memberID";
			if (requestType != "lastName" && requestType != "memberID") {
				thisRequest = {"checkID": requestType};
				requestType = "memberID";
			} else {
				thisRequest = $scope.memberRequest
			}
			playersATXService.pullMemberInfo(thisRequest, requestType).then(function(result) {
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
				$scope.memberRequest.checkID = $scope.currentMember.memberID || $scope.memberRequest.checkID;
			}
			if (result.duplicateMembers) {
				$scope.duplicateMembers = result.duplicateMembers;
			} else {
				$scope.duplicateMembers = false;
			}
			$scope.dupOpen = false
			$scope.imSaving = false;
		}

		function getCurrentAttendance(attendyToRemove) {
			playersATXService.getCurrentAttendance(false, attendyToRemove).then(function(results) {
				$scope.attendance = results.attendance;
				if (attendyToRemove) {
					getExecVpList();
				}
			});
		}

		getExecVpList();
		getRecentPurchases();
		getCurrentAttendance();

		$scope.removeAttendy = function(attendy) {
			var message = "This is not for when someone leaves,\nThis is only when someone was checked in by mistake.\nAre you sure?"
			if (confirm(message)) {
				getCurrentAttendance(attendy.attendID);
			}
		};

		$scope.thisViewPane = function(paneLabel) {
			$scope.viewPane = paneLabel;
		};

		$scope.showDuplicates = function() {
			$scope.dupOpen = !$scope.dupOpen;
		};

		$scope.checkIDEntered = function(checkID) {
			if (!checkID) {
				if (typeTimer) {
					$timeout.cancel(typeTimer);
				}
				typeTimer = $timeout(function() {
					getMemberInfo();
				}, 600);
			} else {
				getMemberInfo(checkID);
			}
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

		$scope.memberCheckedIn = function(member) {
			var areCheckedIn = false;
			if ($scope.attendance.members.length >= 1) {
				angular.forEach($scope.attendance.members, function(thisMember) {
					if (thisMember.memberID == member.memberID) {
						areCheckedIn = true;
					}
				});
			}
			return areCheckedIn;
		};

		$scope.checkMemberIn = function(member) {
			$scope.checkIn = {
				"member1": member.member1 ? false : true,
				"member2": member.member2 ? false : true,
				"status": false,
			};
			$scope.modalOn("checkIn");
		};

		$scope.staffVerified = function(thisSetting) {
			$scope.checkIn[thisSetting] = !$scope.checkIn[thisSetting];
		};

		$scope.finalizeCheckin = function(action) {
			if (action == "submit") {
				var params = {
					"member_id": $scope.currentMember.id,
					"gender": $scope.currentMember.gender
				}
				if ($scope.checkIn.credit) {
					params.credit = $scope.checkIn.credit;
				}
				if ($scope.checkIn.renewalDefault) {
					params.renew = $scope.checkIn.renewalMonths || $scope.checkIn.renewalDefault;
				}
				$scope.imSaving = true;
				playersATXService.checkMemberIn(params).then(function(results) {
					$scope.attendance = results.attendance;
					$scope.modalOn("off");
					$scope.imSaving = false;
					if (params.renew) {
						$scope.currentMember = results.member;
					}
				});
			} else {
				var memberisCurrent = $scope.currentMember.status == "valid" || $scope.checkIn.status;
				return !memberisCurrent || !$scope.checkIn.member1 || !$scope.checkIn.member2
			}
		};

        $scope.newMemFormCmplt = function(formTable) {
        	var formCmplt = false;
        	if (formTable == "him") {
        		formCmplt = $scope.newMember.hisFname && $scope.newMember.hisLname && $scope.newMember.hisDl;
        		formCmplt = $scope.newMember.gender == 2 ? true : formCmplt;
        	} else if (formTable == "her") {
        		formCmplt = $scope.newMember.herFname && $scope.newMember.herLname && $scope.newMember.herDl;
        		formCmplt = $scope.newMember.gender == 3 ? true : formCmplt;
        	} else if (formTable == "gen") {
        		formCmplt = $scope.newMember.duration;
        	}
        	return formCmplt;
        };

        $scope.checkInVp = function(member) {
        	getExecVpList(member);
        };

        function getExecVpList(member) {
			$scope.imSaving = true;
			var params = false;
			if (member) {
				params = {"member_id": member.id, "gender": member.gender};
			}
			playersATXService.getExecVpList(params).then(function(result) {
				$scope.execVps = result.execVps;
				$scope.imSaving = false;
				if (member) {
					getCurrentAttendance();
				}
			});
        }

		function getRecentPurchases(dataRequest, dataType) {
			$scope.imSaving = true;
			playersATXService.getPurchaseInfo(dataRequest, dataType).then(function(result) {
				$scope.purchases = makeDateObjects(result.purchases);
				$scope.imSaving = false;
			});
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

		Date.prototype.addHours= function(h){
			this.setHours(this.getHours()+h);
			return this;
		}

	}]
);