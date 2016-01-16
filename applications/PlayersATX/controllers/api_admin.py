# -*- coding: utf-8 -*-

apiVersion = '0.9'

import gluon.contrib.simplejson as simplejson
from Logging import Logging
logger = Logging(db)

from Events import Events
eventDAL = Events(db)

# The following line is required for .json output.
# Note: There are security implications related to generic views.
# See:
#   https://groups.google.com/forum/?fromgroups=#!topic/web2py/Jk-TIoQhRh4
#   http://comments.gmane.org/gmane.comp.python.web2py/67902
response.generic_patterns = ['json', 'jsonp']

response.headers['Cache-Control'] = "max-age=0"


@auth.requires_login()
def remote_login():
	user = False
	thisResponse = "Missing Form Field"
	jsonData = simplejson.loads(request.body.read()) if request.body else {}
	if jsonData:
		if jsonData.get("email") and jsonData.get("password"):
			password = jsonData.get("password").encode('ascii','replace')
			user = auth.login_bare(jsonData.get("email"), password)
			if user:
				thisResponse = "Logged in"
			else:
				thisResponse = "Invalid login"

	return api_response(message=thisResponse, user=user)

@auth.requires_login()
@auth.requires_membership('Admin')
def create_edit_price():
	jsonData = simplejson.loads(request.body.read()) if request.body else {}
	eventID = jsonData.get("eventID")
	priceData = jsonData.get("priceData")
	prices = False
	if jsonData.get("action") == "create":
		prices = eventDAL.create_price_for_event(eventID, priceData)

	if jsonData.get("action") == "remove":
		prices = eventDAL.remove_price_from_event(eventID, priceData)

	if jsonData.get("action") == "edit":
		thisPrice = db.event_price(priceData["id"])
		if thisPrice:
			thisPrice.update_record(price = priceData["price"])
			thisLabel = db.event_price_label(thisPrice.price_label_id)
			if thisLabel:
				thisLabel.update_record(price_label = priceData["label"])

	return api_response(prices=prices)


@auth.requires_login()
@auth.requires_membership('Staff')
def get_member_info():
	memberKey = request.vars.checkID or None
	member_L_Name = request.vars.checkLastName or None
	requestType = request.vars.requestType or "memberID"
	member = False
	memberDuplicates = False

	from Members import Members, MembersComments
	memberObj = Members(db)

	if requestType == "memberID":
		member = memberObj.get_member(memberKey)
		memberDuplicates = memberObj.get_member_duplicates(memberKey)
		if member:
			member["comments"] = MembersComments(db, member["id"]).get_comments()
	elif requestType == "lastName":
		member = memberObj.get_members_by_last_name(member_L_Name)

	return api_response(memberData=member, duplicateMembers=memberDuplicates)


@auth.requires_login()
@auth.requires_membership('Staff')
def get_purchase_info():
	eventID = request.vars.eventID or None
	lastName = request.vars.lastName or None
	
	from Purchase import Purchase
	purchaseObj = Purchase(db)

	if eventID:
		purchases = False
	elif lastName:
		purchases = False
	else:
		purchases = purchaseObj.get_current_purchases()

	return api_response(purchases=purchases)


@auth.requires_login()
@auth.requires_membership('Admin')
def get_staff_logs():
	range = request.vars.range or "day"
	staffID = request.vars.staffer or None
	from Members import Members
	memberObj = Members(db)
	changeLog = memberObj.get_staff_actions(range, staffID)

	return api_response(changeLog=changeLog)


@auth.requires_login()
@auth.requires_membership('Staff')
def get_attendance_info():
	date = request.vars.date_stamp or None
	idToRemove = request.vars.attendance_id or None
	if idToRemove:
		attendanceRow = db.attendance(int(idToRemove))
		if attendanceRow:
			logger.log_activity("attendance of memberID " + str(attendanceRow.member_id) + " removed", auth.user.id)
			attendanceRow.delete_record()
			# del db.attendance[int(idToRemove)]
	# if date:
	# 	from datetime import datetime, timedelta
	# 	date = datetime.fromtimestamp(int(date)) - timedelta(hours=9)
	from Members import Members
	memberObj = Members(db)
	attendance = memberObj.get_current_attendance(showMembers="true", searchDate=date)

	return api_response(attendance=attendance)


@auth.requires_login()
@auth.requires_membership('Staff')
def member_credit():
	memberID = request.vars.memberID or None
	creditID = request.vars.creditID or None
	creditType = request.vars.creditType or None
	action = request.vars.action or None
	memberCredits = False
	if memberID:
		from Members import Members
		memberObj = Members(db)
		memberCredits = memberObj.create_credit(memberID, creditType)
		if memberCredits:
			member = db.members(int(memberID)).member_number
			logger.log_activity(creditType + " credit added to member " + member, auth.user.id)

	return api_response(memberCredits=memberCredits)


@auth.requires_login()
@auth.requires_membership('Staff')
def check_member_in():
	memberID = int(request.vars.member_id) if request.vars.member_id else None
	gender = request.vars.gender or None
	useCredit = request.vars.credit or None
	renewMembership = request.vars.renew or None
	attendance = False
	member = False
	if memberID and gender:
		from Members import Members
		memberObj = Members(db)
		attendance = memberObj.check_member_in(memberID, gender, auth.user, useCredit)
		if renewMembership:
			try:
				thisRenewal = int(renewMembership)
				if thisRenewal > 0:
					thisRenewal = str(thisRenewal) + " months"
			except:
				thisRenewal = "a " + renewMembership
			thisMode = False
			# thisMode = "testMode"
			member = memberObj.renew_this_member(memberID, renewMembership, thisMode)
			if member:
				logger.log_activity("Renew member " + member["memberID"] + " for " + thisRenewal  , auth.user.id)

	return api_response(attendance=attendance, member=member)


@auth.requires_login()
@auth.requires_membership('Staff')
def add_member_comment():
	jsonData = simplejson.loads(request.body.read()) if request.body else {}
	memberID = int(jsonData["memberID"]) if jsonData.get("memberID") else None
	commentRequest = jsonData.get("comment")
	userID = auth.user
	comments = False
	error = False
	if memberID and userID and commentRequest:
		from Members import MembersComments
		comments = MembersComments(db, memberID).set_comment(userID, commentRequest)
	else:
		error = "We did not recieve enough data to log this comment"

	return api_response(comments=comments, error=error)


@auth.requires_login()
@auth.requires_membership('Staff')
def new_member():
	jsonData = simplejson.loads(request.body.read()) if request.body else {}
	newMember = False
	member = False
	memberDuplicates = False
	if jsonData:
		from Members import Members
		memberObj = Members(db)

		action = jsonData.get("action")
		if action == "initial":
			newMember = memberObj.create_new_member(jsonData)
		elif action == "complete":
			newMember = memberObj.verify_new_member(jsonData)
		# elif action == "edit":
		# 	newMember = memberObj.verify_new_member(jsonData, auth.user)
		elif action == "admin_new":
			memberKey = memberObj.create_new_member(jsonData, "admin")
			if memberKey:
				logger.log_activity("created New Member " + memberKey, auth.user.id)
				member = memberObj.get_member(memberKey)
				memberDuplicates = memberObj.get_member_duplicates(memberKey)
				newMember = memberObj.genterate_new_member_template()

	return api_response(newMember=newMember, memberData=member, duplicateMembers=memberDuplicates)


@auth.requires_login()
@auth.requires_membership('Staff')
def edit_member():
	jsonData = simplejson.loads(request.body.read()) if request.body else {}
	message = False
	if jsonData:
		from Members import Members
		memberObj = Members(db)
		memberKey = memberObj.edit_member(jsonData)
		if memberKey:
			message = "successfully updated"
			logger.log_activity("made changes to" + jsonData.get("logData") + " of member " + memberKey, auth.user.id)

	return api_response(message=message)


@auth.requires_login()
@auth.requires_membership('Admin')
def purchase_info():
	eventID = int(request.vars.event_id) if request.vars.event_id else None
	from Purchase import Purchase
	return api_response(purchaseData = Purchase(db).purchase_info(eventID))


@auth.requires_login()
@auth.requires_membership('Staff')
def get_vp_list():
	memberID = int(request.vars.member_id) if request.vars.member_id else None
	gender = request.vars.gender or None
	from Members import Members
	return api_response(execVps = Members(db).get_executive_members(auth.user, memberID, gender))


def api_response(**kwargs):
	resp = dict(**kwargs)

	resp.update({
		'version': apiVersion,
		'success': True
	})

	return resp