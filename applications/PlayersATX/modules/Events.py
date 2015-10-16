#!/usr/bin/env python
# coding: utf8
from gluon import *

class Events:
	def __init__(self, db):
		self.db = db

	def get_events(self, eventID="", altImage=False, cleanData=True):
		events=False
		if eventID:
			result = self.db.events(int(eventID))
			if result:
				if cleanData:
					events = self._extract_event(result, altImage)
				else:
					events = result
		else:
			query = self.db.events.id>0
			results = self.db(query).select()
			if results:
				events = []
				for result in results:
					thisEvent = self._extract_event(result, altImage)
					events.append(thisEvent)

		return events

	def is_both_recurring_and_upcoming(self, pageID=""):
		isUpcoming = False
		isRecurring = False
		if pageID:
			query = (self.db.page_settings.page_type==pageID) & (self.db.page_settings.data_type == 'event')
			results = self.db(query).select(orderby=self.db.page_settings.data_order)
			if results:
				for result in results:
					thisEvent = self.get_events(result.data_card, cleanData=False)
					if thisEvent.expiration:
						isUpcoming = True
					else:
						isRecurring = True

		if isUpcoming and isRecurring:
			return True
		else:
			return False



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
					purgeMe = False
					thisEvent = self.get_events(result.data_card, altImage=result.alt_image)
					if not thisEvent:
						process = False
						purgeMe = True

					if thisEvent["dateType"] == "expired":
						process = False

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
					elif purgeMe:
						result.delete_record()

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
					if thisEvent:
						thisEvent["layout"] = result.layout_style or 1
						thisEvent["position"] = result.data_order
						thisEvent["dataID"] = result.id
						events.append(thisEvent)
					else:
						result.delete_record()
		return events

	def get_new_event_position(self, pageID):
		thisPostion = 0
		if pageID:
			query = (self.db.page_settings.page_type == pageID) & (self.db.page_settings.data_type == 'event')
			thisPostion = self.db(query).count()
			thisPostion = thisPostion + 1

		return thisPostion

	def create_price_for_event(self, eventID, priceData):
		if not eventID:
			return False
		event = self.db.events(eventID)
		event.update_record(prepay = True)
		label = priceData.get("label")
		if label:
			labelID = self.db.event_price_label.insert(price_label=label)
			if labelID:
				self.db.event_price.insert(
					event_id = eventID,
					price_label_id = labelID,
					price = priceData.get("price")
				)

		return self._get_prices_for_event(eventID)

	def remove_price_from_event(self, eventID, priceData):
		if not eventID:
			return False

		prices = False

		thisPrice = self.db.event_price(priceData["id"])
		if thisPrice:
			thisPrice.update_record(in_use=False)
			prices = self._get_prices_for_event(eventID)
			if prices:
				hasValidPrice = False
				for price in prices:
					if price["inUse"]:
						hasValidPrice = True

				if not hasValidPrice:
					event = self.db.events(eventID)
					if event:
						event.update_record(prepay = False)
					return False

		return prices


	def _extract_event(self, event, altImage):
		from datetime import datetime, timedelta
		TODAY = datetime.now() - timedelta(hours=9)
		TODAY = TODAY.date()
		thisEvent = {}
		thisEvent["eventID"] = event.id
		thisEvent["event_name"] = event.event_name
		thisEvent["event_heading"] = event.event_heading
		thisEvent["body_text"] = event.body_text
		thisEvent["eventDate"] = event.expiration
		thisEvent["last_edit"] = event.modified or event.created
		thisEvent["prepay"] = event.prepay
		thisEvent["prices"] = None
		thisEvent["image"] = None
		thisEvent["dateType"] = "always"
		if thisEvent["eventDate"]:
			if thisEvent["eventDate"] < TODAY:
				thisEvent["dateType"] = "expired"
			else:
				thisEvent["dateType"] = "current"

		if event.event_image:
			imageData = self.db.image_library(event.event_image)
			if imageData:
				if altImage:
					thisEvent["image"] = imageData.banner
				else:					
					thisEvent["image"] = imageData.image_file

		if event.prepay:
			thisEvent["prices"] = self._get_prices_for_event(event.id)

		return thisEvent

	def _get_prices_for_event(self, eventID):
		if not eventID:
			return False

		prices = False

		query = self.db.event_price.event_id == eventID
		priceData = self.db(query).select()
		if priceData:
			prices = []
			for price in priceData:
				thisPrice = {
					"id": price.id,
					"price": price.price,
					"label": self.db.event_price_label(price.price_label_id).price_label,
					"inUse": price.in_use
				}
				prices.append(thisPrice)

		return prices
