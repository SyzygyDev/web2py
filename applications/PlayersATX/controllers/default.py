# -*- coding: utf-8 -*-

from BasicSite import *
basics = MainPage(db)
cardDAL = ContentCards(db)

from Events import Events
eventDAL = Events(db)

thisPage = basics.get_my_page()
for pageData in thisPage["pages"]:
	if pageData["pageFile"] == request.function:
		PAGETYPE = pageData

def index():
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	# THIS PULLS FROM THE EVENTS PAGE
	events = eventDAL.get_data_events(pageID=4)
	return dict(thisPage=thisPage, cards=cards, events=events)


def rules():
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	return dict(thisPage=thisPage, cards=cards)


def membership():
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	return dict(thisPage=thisPage, cards=cards)


def about():
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	return dict(thisPage=thisPage, cards=cards)


def news():
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	return dict(thisPage=thisPage, cards=cards)


def events():
	typeOfEvent = request.vars.event_type or "once"
	showbuttons = eventDAL.is_both_recurring_and_upcoming(pageID=PAGETYPE["id"])
	events = eventDAL.get_data_events(pageID=PAGETYPE["id"], typeOfEvent=typeOfEvent)
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	return dict(thisPage=thisPage, events=events, showbuttons=showbuttons, cards=cards)


def eventpay():
	eventID = request.vars.eventID or None
	angularData = {"message":"no data available"}
	if not eventID:
		redirect(URL('default', 'events'))
	if eventID:
		event = eventDAL.get_events(int(eventID))
		if event:
			if not event["prepay"]:
				redirect(URL('default', 'events'))
			elif event["dateType"] == "expired":
				redirect(URL('default', 'events'))
			else:
				angularData = {"message":"data available"}
				angularData["event"] = event
	return dict(thisPage=thisPage, angularData=angularData)


def contact():
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	events = eventDAL.get_data_events(pageID=PAGETYPE["id"])
	emailSuccess = False

	form = SQLFORM.factory(
		Field('name', requires=IS_NOT_EMPTY()),
		Field('email', requires =[ IS_EMAIL(error_message='You must provide a valid email!'), IS_NOT_EMPTY() ]),
		Field('Phone_Number', label="Phone Number"),
		Field('message', requires=IS_NOT_EMPTY(), type='text')
	)
	if form.process().accepted:
		from datetime import datetime
		messageSent = datetime.now().strftime( "%A, %b %d %Y at %I:%M:%S %p" )
		thisMessage = "On " + messageSent + ":\nFrom: " + form.vars.name + "\n" + "Email address: " + form.vars.email + "\n"
		if form.vars.Phone_Number:
			thisMessage = thisMessage + "Phone: " + form.vars.Phone_Number + "\n"
		thisMessage = thisMessage + "\n___________________________________________\nMessage: \n" + form.vars.message

		x = mail.send(to=['web_contact@playersatx.club'],
			subject="Players website response",
			message= thisMessage)
		if x == True:
			emailSuccess = True
			otherMessage = "The club is open Fridays 9:00pm to 2:00am and Saturdays 9:00pm to 3:00am.\n"
			otherMessage = otherMessage + "Our staff typically responds during this time, but we will get to your email as soon as we can.\n\n\n" 
			otherMessage = otherMessage + "We recieved the following:\n" + thisMessage
			mail.send(to=[form.vars.email],
				subject="We appreciate your email",
				message= otherMessage)
	return dict(thisPage=thisPage, cards=cards, events=events, form=form, emailSuccess=emailSuccess)


def seating():
	thisPage["datePicker"] = True
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	events = eventDAL.get_data_events(pageID=PAGETYPE["id"])
	emailSuccess = False
	isAfterEight = False

	from datetime import datetime
	timeNow = datetime.utcnow()
	isAfterEight = timeNow.strftime( "%H" )
	isAfterEight = int(isAfterEight) - 5
	if isAfterEight >= 20:
		isAfterEight = "+1d"
	else:
		isAfterEight = 0

	reservables = _get_reservable_spaces()

	form = SQLFORM.factory(
		Field('name', type='text'),
		Field('member_id'),
		Field('email', requires =[ IS_EMAIL(error_message='You must provide a valid email!'), IS_NOT_EMPTY() ]),
		Field('Phone_Number', label="Phone Number"),
		Field('table_id'),
		Field('party_date', type='date')
	)
	if form.process().accepted:
		tableID = reservables[int(form.vars.table_id)]
		clientPhone = form.vars.Phone_Number or "left blank"
		thisMessage = "Member " + form.vars.member_id + " has requested to reserve " + tableID["label"] + " for\n"
		thisMessage = thisMessage + form.vars.name + "\n for the evening of " + form.vars.party_date.strftime( "%A, %b %d %Y" ) + "\nEmail: " + form.vars.email + "\nPhone: " + clientPhone

		x = mail.send(to=['reservations@playersatx.club'],
			subject="RESERVATION REQUEST",
			message= thisMessage)
		if x == True:
			reservationMade = datetime.now().strftime( "%A, %b %d %Y at %I:%M:%S %p" )
			emailSuccess = True
			otherMessage = "On " + reservationMade + " you sent a reservation request for " + tableID["label"] + ".\nPlease remember that reservations are 'First Come - First Served.'"
			if tableID["group"]:
				otherMessage = otherMessage + "\nIf that location is already taken, we will try to place you in the '" + tableID["group"] + "' area." 

			otherMessage = otherMessage + "\nIf we are unable to accomodate you, we will try to let you know as soon as we can.\n\nReservation Request: " + thisMessage
			mail.send(to=[form.vars.email],
				subject="Reservation Request",
				message= otherMessage)
	return dict(thisPage=thisPage, cards=cards, events=events, form=form, emailSuccess=emailSuccess, isAfterEight=isAfterEight, reservables=reservables)


def party():
	thisPage["datePicker"] = True
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	events = eventDAL.get_data_events(pageID=PAGETYPE["id"])
	emailSuccess = False
	isAfterEight = False

	from datetime import datetime
	timeNow = datetime.utcnow()
	isAfterEight = timeNow.strftime( "%H" )
	isAfterEight = int(isAfterEight) - 5
	if isAfterEight >= 20:
		isAfterEight = "+1d"
	else:
		isAfterEight = 0

	reservables = _get_reservable_spaces()

	form = SQLFORM.factory(
		Field('name', type='text'),
		Field('member_id'),
		Field('email', requires =[ IS_EMAIL(error_message='You must provide a valid email!'), IS_NOT_EMPTY() ]),
		Field('Phone_Number', label="Phone Number"),
		Field('table_id'),
		Field('party_date', type='date')
	)
	if form.process().accepted:
		tableID = reservables[int(form.vars.table_id)]
		clientPhone = form.vars.Phone_Number or "left blank"
		thisMessage = "Member " + form.vars.member_id + " has requested to reserve " + tableID["label"] + " for\n"
		thisMessage = thisMessage + form.vars.name + "\n for the evening of " + form.vars.party_date.strftime( "%A, %b %d %Y" ) + "\nEmail: " + form.vars.email + "\nPhone: " + clientPhone

		x = mail.send(to=['parties@playersatx.club'],
			subject="RESERVATION REQUEST -- LARGE PARTY",
			message= thisMessage)
		if x == True:
			reservationMade = datetime.now().strftime( "%A, %b %d %Y at %I:%M:%S %p" )
			emailSuccess = True
			otherMessage = "On " + reservationMade + " you sent a reservation request for " + tableID["label"] + ".\nPlease remember that reservations are 'First Come - First Served.'"
			if tableID["group"]:
				otherMessage = otherMessage + "\nIf that location is already taken, we will try to place you in the '" + tableID["group"] + "' area." 

			otherMessage = otherMessage + "\nIf we are unable to accomodate you, we will try to let you know as soon as we can.\n\nReservation Request - Large Party: " + thisMessage
			mail.send(to=[form.vars.email],
				subject="Reservation Request - Large Party",
				message= otherMessage)
	return dict(thisPage=thisPage, cards=cards, events=events, form=form, emailSuccess=emailSuccess, isAfterEight=isAfterEight, reservables=reservables)



def user():
	response.generic_patterns = ['json', 'jsonp']

	form=auth()

	return dict(form=form, thisPage=thisPage)

def userModal2():
	form=auth()

	return dict(form=form, thisPage=thisPage)


def userModal():
	angularData = {"message":"no data available"}

	return dict(angularData=angularData, thisPage=thisPage)

def csv_data():
	recordStart = request.vars.start or "0"
	recordCount = request.vars.count or "10"
	# from Csvimport import Csvimport
	# csvObj = Csvimport(db)
	# testData = csvObj.get_me_clean_data(int(recordStart), int(recordCount))
	testData = "Done"

	dupList = make_dup_list()
	if dupList:
		testData = []
		for dup in dupList:
			query = db.members.member_number == dup
			results = db(query).select()
			if results:
				testData.append(results)
				# count = 0
				# for result in results:
				# 	if count != 0:
				# 		newMemberKey = genterate_new_key()
				# 		newID = db.membership_duplicates.insert(
				# 			old_id=result.member_number,
				# 			new_id=newMemberKey,
				# 			member_id=result.id
				# 		)
				# 		if newID:
				# 			result.update_record(member_number=newMemberKey)

				# 	count = count + 1

	return dict(thisPage=thisPage, testData=testData)

def genterate_new_key():
	import random, string
	exists = False

	newKey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
	newKey = newKey.replace("O", "0");
	if db(db.members.member_number == newKey).count() > 0:
		exists = True

	if exists:
		return genterate_new_key()
	else:
		return newKey

@cache.action()
def download():
	return response.download(request, db)

def _get_reservable_spaces():
	return [
		{"label":"Table 1", "group":"Dance Floor Member Seating"},
		{"label":"Table 2", "group":"Dance Floor Member Seating"},
		{"label":"Table 3", "group":"Dance Floor Member Seating"},
		{"label":"Table 4", "group":"Dance Floor Member Seating"},
		{"label":"Table 5", "group":"Dance Floor Member Seating"},
		{"label":"Table 6", "group":"Dance Floor Member Seating"},
		{"label":"Table 7", "group":"Dance Floor Member Seating"},
		{"label":"Table 8", "group":"Dance Floor Member Seating"},
		{"label":"Table 9", "group":"Dance Floor Member Seating"},
		{"label":"Table 10", "group":"Dance Floor Round Tables"},
		{"label":"Table 11", "group":"Dance Floor Round Tables"},
		{"label":"Table 12", "group":"Front Bar Area"},
		{"label":"Table 14", "group":"Front Bar Area"},
		{"label":"Table 15", "group":"Front Bar Area"},
		{"label":"Table 16", "group":"Front Bar Area"},
		{"label":"Table 17", "group":"Front Bar Area"},
		{"label":"Table 18", "group":"Front Bar Area"},
		{"label":"Table 19", "group":"Front Bar Area"},
		{"label":"Table 20", "group":"Front Bar Area"},
		{"label":"Table 21", "group":"Front Bar Area"},
		{"label":"Table 22", "group":"Front Bar Area"},
		{"label":"Table 25", "group":"Rear Bar Area"},
		{"label":"Table 26", "group":"Rear Bar Area"},
		{"label":"Table 30", "group":"Elevated Area"},
		{"label":"Table 31", "group":"Elevated Area"},
		{"label":"Executive VIP by the Dance Floor", "group":None},
		{"label":"Executive VIP Lounge Area in the rear", "group":None},
	]

def make_dup_list():
	return [
		"A00519",
		"A00917",
		"a01591",
		"A01919",
		"A09779",
		"A13099",
		"a13899",
		"A13905",
		"A14606",
		"A14792",
		"A14921",
		"A15608",
		"A16321",
		"A18788",
		"A19234",
		"A20468",
		"A20680",
		"A21796",
		"A24363",
		"A26834",
		"A29910",
		"A30804",
		"A30867",
		"A30999",
		"A37685",
		"A38003",
		"A40413",
		"A40564",
		"A45304",
		"A45494",
		"A45505",
		"A46632",
		"A50367",
		"A50533",
		"A5246",
		"A55000",
		"A56025",
		"A56027",
		"A57140",
		"A57308",
		"A61445",
		"A62825",
		"A64236",
		"A68585",
		"A69980",
		"A70149",
		"A71822",
		"A71908",
		"A75799",
		"A76392",
		"A77594",
		"A78174",
		"A78361",
		"A79294",
		"a83948",
		"A87351",
		"A88178",
		"A89990",
		"A90045",
		"A91774",
		"A92428",
		"A93077",
		"A93507",
		"A94800",
		"A94921",
		"A95563",
		"A96764",
		"A97106",
		"A99381"
	]