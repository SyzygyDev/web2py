# -*- coding: utf-8 -*-

from BasicSite import *
basics = MainPage(db)
cardDAL = ContentCards(db)
eventDAL = Events(db)
thisPage = basics.get_my_page()
for pageData in thisPage["pages"]:
	if pageData["pageFile"] == request.function:
		PAGETYPE = pageData


def index():
	cards = cardDAL.get_data_cards(pageID=PAGETYPE["id"])
	events = eventDAL.get_data_events(pageID=PAGETYPE["id"])
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


def events():
	typeOfEvent = request.vars.event_type or "always"
	events = eventDAL.get_data_events(pageID=PAGETYPE["id"], typeOfEvent=typeOfEvent)
	return dict(thisPage=thisPage, events=events)

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
		thisMessage = "on " + messageSent + ":\nfrom:" + form.vars.name + "\n" + "email address: " + form.vars.email + "\n"
		if form.vars.Phone_Number:
			thisMessage = thisMessage + "phone:" + form.vars.Phone_Number + "\n"
		thisMessage = thisMessage + "message:\n" + form.vars.message

		x = mail.send(to=['syzygywebbed@gmail.com'],
			subject="Players response",
			message= thisMessage)
		if x == True:
			emailSuccess = True
			otherMessage = "The club is open Fridays 9:00pm to 2:00am and Saturdays 9:00pm to 3:00am.\n"
			otherMessage = otherMessage + "Our staff typically responds during this time, but we will get to your email as soon as we can.\n\n\n" 
			otherMessage = otherMessage + "We recieved the following:\n" + thisMessage
			mail.send(to=[form.vars.email],
				subject="We appriciate your email",
				message= otherMessage)
	return dict(thisPage=thisPage, cards=cards, events=events, form=form, emailSuccess=emailSuccess)


def seating():
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
		thisMessage = thisMessage + form.vars.name + "\n for the evening of " + form.vars.party_date.strftime( "%A, %b %d %Y" ) + "\nEmail:" + form.vars.email + "\nPhone:" + clientPhone

		x = mail.send(to=['syzygywebbed@gmail.com'],
			subject="RESERVATION REQUEST",
			message= thisMessage)
		if x == True:
			reservationMade = datetime.now().strftime( "%A, %b %d %Y at %I:%M:%S %p" )
			emailSuccess = True
			otherMessage = "On " + reservationMade + " you sent a reservation request for " + tableID["label"] + ".\nPlease remember that reservations are 'First Come - First Served.'"
			if tableID["group"]:
				otherMessage = otherMessage + "\nIf that location is already taken, we will try to place you in the '" + tableID["group"] + "' area." 

			otherMessage = otherMessage + "\nIf we are unable to accomodate you, we will try to let you know as soon as we can."
			mail.send(to=[form.vars.email],
				subject="Reservation Request",
				message= otherMessage)
	return dict(thisPage=thisPage, cards=cards, events=events, form=form, emailSuccess=emailSuccess, isAfterEight=isAfterEight, reservables=reservables)



def user():
	form=auth()

	return dict(form=form, thisPage=thisPage)

@cache.action()
def download():
	return response.download(request, db)

def _get_reservable_spaces():
	return [
		{"label":"Table 1", "group":"Left Side Dance Floor"},
		{"label":"Table 2", "group":"Left Side Dance Floor"},
		{"label":"Table 3", "group":"Left Side Dance Floor"},
		{"label":"Table 4", "group":"Left Side Dance Floor"},
		{"label":"Table 5", "group":"Left Side Dance Floor"},
		{"label":"Table 6", "group":"Left Side Dance Floor"},
		{"label":"Table 7", "group":"Left Side Dance Floor"},
		{"label":"Table 8", "group":"Left Side Dance Floor"},
		{"label":"Table 9", "group":"Left Side Dance Floor"},
		{"label":"Table 10", "group":"Round Dance Floor"},
		{"label":"Table 11", "group":"Round Dance Floor"},
		{"label":"Table 12", "group":"Front Bar Area"},
		{"label":"Table 13", "group":"Front Bar Area"},
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