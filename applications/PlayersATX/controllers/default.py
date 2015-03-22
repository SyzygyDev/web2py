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


def user():
	form=auth()

	return dict(form=form, thisPage=thisPage)

@cache.action()
def download():
	return response.download(request, db)