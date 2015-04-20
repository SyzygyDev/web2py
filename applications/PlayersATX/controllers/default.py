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

	form = SQLFORM.factory(
		Field('name', requires=IS_NOT_EMPTY()),
		Field('email', requires =[ IS_EMAIL(error_message='You must provide a valid email!'), IS_NOT_EMPTY() ]),
		Field('Phone_Number', label="Phone Number"),
		Field('message', requires=IS_NOT_EMPTY(), type='text')
	)
	if form.process().accepted:
		thisMessage = "from:" + form.vars.name + "\n" + "email address: " + form.vars.email + "\n"
		if form.vars.Phone_Number:
			thisMessage = thisMessage + "phone:" + form.vars.Phone_Number + "\n"
		thisMessage = thisMessage + "message:\n" + form.vars.message

		x = mail.send(to=['syzygywebbed@gmail.com'],
			subject="Players response",
			message= thisMessage)
		if x == True:
			mail.send(to=[form.vars.email],
				subject="We appriciate your email",
				message= "The club is open Fridays 9:00pm to 2:00am and Saturdays 9:00pm to 3:00am.\nOur staff typically responds during this time, but we will get to your email as soon as we can")
	return dict(thisPage=thisPage, cards=cards, events=events, form=form)



def user():
	form=auth()

	return dict(form=form, thisPage=thisPage)

@cache.action()
def download():
	return response.download(request, db)