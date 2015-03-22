#!/usr/bin/env python
# coding: utf8
from gluon import *
from datetime import datetime
TODAY = datetime.now().date()

class MainPage:
	def __init__(self, db):
		self.db = db

	def get_my_page(self):
		pageSettings = {}
		results = self.db(self.db.basic_site.id > 0).select().first()
		if results:
			pageSettings["siteID"] = results.id or None
			pageSettings["title"] = results.page_title or "PlayersATX"
			pageSettings["heading"] = results.page_header or "PlayersATX"
			pageSettings["footer"] = results.page_footer or "PlayersATX"
			pageSettings["subHeading"] = results.page_subheader or "PlayersATX"
			pageSettings["tagLine"] = results.page_tagline or "PlayersATX"
			pageSettings["description"] = results.page_desc or "The PlayersATX web site"
			pageSettings["last_edit"] = results.modified or None
			pageSettings["backgroundColor"] = results.background_color or None
			pageSettings["backgroundStyle"] = results.background_img_style or None
			pageSettings["backgroundImg"] = None
			if results.background_img:
				imageData = self.db.image_library(results.background_img)
				pageSettings["backgroundImg"] = imageData.image_file

			else:
				thisPage = {
					"id":1,
					"pageName":"Home",
					"pageFile":"index"
				}
				pageSettings["pages"].append(thisPage)

		else:
			pageSettings["siteID"] = None
			pageSettings["title"] = "PlayersATX"
			pageSettings["heading"] = "PlayersATX"
			pageSettings["footer"] = "PlayersATX"
			pageSettings["subHeading"] = "PlayersATX"
			pageSettings["tagLine"] = "PlayersATX"
			pageSettings["description"] = "The PlayersATX web site"
			pageSettings["last_edit"] = None
			pageSettings["backgroundColor"] = None
			pageSettings["backgroundStyle"] = None
			pageSettings["backgroundImg"] = None

		pageSettings["pages"] = []
		query = self.db.page_types.id > 0
		rawPages = self.db(query).select()
		if rawPages:
			for rawPage in rawPages:
				thisPage = {
					"id":rawPage.id,
					"pageName":rawPage.page_name,
					"pageFile":rawPage.page_file
				}
				pageSettings["pages"].append(thisPage)

		return pageSettings

	def reorder_page_setting(self, dataID, action):
		thisWorked = False
		if action=="down":
			result = self.db.page_settings(dataID)
			if result:
				query = (self.db.page_settings.page_type == result.page_type) & (self.db.page_settings.data_type == result.data_type) & (self.db.page_settings.data_order == result.data_order + 1)
				self.db(query).update(data_order=result.data_order)
				self.db(self.db.page_settings.id == dataID).update(data_order=result.data_order + 1)
				thisWorked = True
		elif action=="up":
			result = self.db.page_settings(dataID)
			if result:
				query = (self.db.page_settings.page_type == result.page_type) & (self.db.page_settings.data_type == result.data_type) & (self.db.page_settings.data_order == result.data_order - 1)
				self.db(query).update(data_order=result.data_order)
				self.db(self.db.page_settings.id == dataID).update(data_order=result.data_order - 1)
				thisWorked = True

		return thisWorked

	def remove_page_setting(self, dataID):
		thisWorked = False
		result = self.db.page_settings(dataID)
		if result:
			query = (self.db.page_settings.page_type == result.page_type) & (self.db.page_settings.data_type == result.data_type) & (self.db.page_settings.data_order > result.data_order)
			reOrders = self.db(query).select()
			if reOrders:
				for thisSetting in reOrders:
					self.db(self.db.page_settings.id == thisSetting.id).update(data_order=thisSetting.data_order - 1)
			self.db(self.db.page_settings.id == dataID).delete()
			thisWorked = True
		return thisWorked




class ContentCards:
	def __init__(self, db):
		self.db = db

	def get_content_cards(self, cardID="", altImage=False):
		cards=False
		if cardID:
			result = self.db.content_card(cardID)
			if result:
				cards = self._extract_card(result, altImage)
		else:
			query = self.db.content_card.id>0
			results = self.db(query).select()
			if results:
				cards = []
				for result in results:
					thisCard = self._extract_card(result, altImage)
					cards.append(thisCard)

		return cards

	def get_data_cards(self, dataID="", pageID=""):
		cards=False
		if dataID:
			result = self.db.page_settings(dataID)
			if result and result.data_type=='content':
				cards = self.get_content_cards(result.data_card, altImage=result.alt_image)
				cards["imageSize"] = str(result.image_size or 25) + "%"
				cards["position"] = result.data_order
		elif pageID:
			query = (self.db.page_settings.page_type==pageID) & (self.db.page_settings.data_type == 'content')
			results = self.db(query).select(orderby=self.db.page_settings.data_order)
			if results:
				cards = []
				for result in results:
					thisCard = self.get_content_cards(result.data_card, altImage=result.alt_image)
					thisCard["imageSize"] = str(result.image_size or 25) + "%"
					thisCard["position"] = result.data_order
					cards.append(thisCard)

		return cards

	def get_cards_by_page_id(self, pageID):
		cards=False
		if pageID:
			query = (self.db.page_settings.page_type == pageID) & (self.db.page_settings.data_type == 'content')
			results = self.db(query).select(orderby=self.db.page_settings.data_order)
			if results:
				cards = []
				for result in results:
					thisCard = self.get_content_cards(result.data_card)
					thisCard["position"] = result.data_order
					thisCard["dataID"] = result.id
					cards.append(thisCard)
		return cards

	def get_new_card_position(self, pageID):
		thisPostion = 0
		if pageID:
			query = (self.db.page_settings.page_type == pageID) & (self.db.page_settings.data_type == 'content')
			thisPostion = self.db(query).count()
			thisPostion = thisPostion + 1

		return thisPostion

	def _extract_card(self, card, altImage):
		thisCard = {}
		thisCard["cardID"] = card.id
		thisCard["card_name"] = card.card_name
		thisCard["card_heading"] = card.card_heading
		thisCard["body_text"] = card.body_text
		thisCard["last_edit"] = card.modified or card.created
		thisCard["left_image"] = None
		thisCard["right_image"] = None
		if card.left_image:
			imageData = self.db.image_library(card.left_image)
			if altImage:
				thisCard["left_image"] = imageData.banner
			else:
				thisCard["left_image"] = imageData.image_file
		if card.right_image:
			imageData = self.db.image_library(card.right_image)
			if altImage:
				thisCard["right_image"] = imageData.banner
			else:
				thisCard["right_image"] = imageData.image_file
		return thisCard




class Events:
	def __init__(self, db):
		self.db = db

	def get_events(self, eventID="", altImage=False):
		events=False
		if eventID:
			result = self.db.events(eventID)
			if result:
				events = self._extract_event(result, altImage)
		else:
			query = self.db.events.id>0
			results = self.db(query).select()
			if results:
				events = []
				for result in results:
					thisEvent = self._extract_event(result, altImage)
					events.append(thisEvent)

		return events

	def get_data_events(self, dataID="", pageID="", typeOfEvent=""):
		events=False
		if dataID:
			result = self.db.page_settings(dataID)
			if result and result.data_type=='event':
				events = self.get_events(result.data_card, altImage=result.alt_image)
				events["layout"] = result.layout_style or 1
				events["position"] = result.data_order

		elif pageID:
			query = (self.db.page_settings.page_type==pageID) & (self.db.page_settings.data_type == 'event')
			results = self.db(query).select(orderby=self.db.page_settings.data_order)
			if results:
				events = []
				for result in results:
					process = True
					thisEvent = self.get_events(result.data_card, altImage=result.alt_image)
					if typeOfEvent:
						if typeOfEvent == "always":
							if not thisEvent["dateType"] == "always":
								process = False
						elif typeOfEvent == "once":
							if not thisEvent["dateType"] == "current":
								process = False

					if process:
						thisEvent["layout"] = result.layout_style or 1
						thisEvent["position"] = result.data_order
						events.append(thisEvent)

		return events

	def get_events_by_page_id(self, pageID):
		events=False
		if pageID:
			query = (self.db.page_settings.page_type == pageID) & (self.db.page_settings.data_type == 'event')
			results = self.db(query).select(orderby=self.db.page_settings.data_order)
			if results:
				events = []
				for result in results:
					thisEvent = self.get_events(result.data_card)
					thisEvent["layout"] = result.layout_style or 1
					thisEvent["position"] = result.data_order
					thisEvent["dataID"] = result.id
					events.append(thisEvent)
		return events

	def get_new_event_position(self, pageID):
		thisPostion = 0
		if pageID:
			query = (self.db.page_settings.page_type == pageID) & (self.db.page_settings.data_type == 'event')
			thisPostion = self.db(query).count()
			thisPostion = thisPostion + 1

		return thisPostion

	def _extract_event(self, event, altImage):
		thisEvent = {}
		thisEvent["eventID"] = event.id
		thisEvent["event_name"] = event.event_name
		thisEvent["event_heading"] = event.event_heading
		thisEvent["body_text"] = event.body_text
		thisEvent["eventDate"] = event.expiration
		thisEvent["last_edit"] = event.modified or event.created
		thisEvent["image"] = None
		thisEvent["dateType"] = "always"
		if thisEvent["eventDate"]:
			if thisEvent["eventDate"] < TODAY:
				thisEvent["dateType"] = "expired"
			else:
				thisEvent["dateType"] = "current"

		if event.event_image:
			imageData = self.db.image_library(event.event_image)
			if altImage:
				thisEvent["image"] = imageData.image_file
			else:
				thisEvent["image"] = imageData.banner
		return thisEvent
