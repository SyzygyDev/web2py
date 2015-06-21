#!/usr/bin/env python
# coding: utf8
from gluon import *

class Tournament:
	def __init__(self, db):
		self.db = db

	def get_tournaments(self):
		tournamentObject = {
	        "active":[],
	        "expired":[]
		}
		results = self.db(self.db.tournament.id > 0).select()
		if results:
			for result in results:
				thisTournament = self._extract_tournament(result)
				if thisTournament:
					if not thisTournament.get("expired"):
						tournamentObject["active"].append(thisTournament)
					else:
						tournamentObject["expired"].append(thisTournament)

		return tournamentObject

	def get_tournament_by_id(self, tournamentID):
		return self._extract_tournament(self.db.tournament(tournamentID))

	def _extract_tournament(self, tournament):
		thisTournament = False
		if tournament:
			thisTournament = {
				"id":tournament.id,
				"name":tournament.name,
				"description":tournament.description,
				"type":False,
				"image":False,
				"location":False,
				"date":False,
				"time":False
			}

			tournType = tournament.tourn_type or 1
			thisType = self.db.tournament_types(tournType)
			thisTournament["type"] = thisType.tourn_type

			if tournament.tourn_img:
				image = self.db.image_library(tournament.tourn_img)
				if image:
					thisTournament["image"] = {
						"name":image.image_name,
						"img":image.image_file,
						"thumb":image,
						"banner":image
					}

			if tournament.location_id:
			    from Location import Location
			    LocationObj = Location(self.db)
			    thisTournament["location"] = LocationObj.get_location_by_id(tournament.location_id)

			if tournament.tourn_date:
				from datetime import datetime
				TODAY = datetime.now().date()
				thisTournament["date"] = tournament.tourn_date.date()
				rawDate = tournament.tourn_date.timetuple()
				# timetuple = "time.struct_time(tm_year=2015, tm_mon=6, tm_mday=27, tm_hour=7, tm_min=30, tm_sec=0, tm_wday=5, tm_yday=178, tm_isdst=-1)"
				meridian = "AM"
				if rawDate.tm_hour >= 12:
					meridian = "PM"
				thisTournament["time"] = str(rawDate.tm_hour) + ":" + str(rawDate.tm_min) + " " + meridian
				if thisTournament["date"] < TODAY:
					thisTournament["expired"] = True

		return thisTournament


	def create_new_tournament(self, tournamentJson):
		newTournament = False
		if tournamentJson:
			renderedDateObject = self._render_datetime_object(tournamentJson.get("date"), tournamentJson.get("time"))

			newTournament = self.db.tournament.insert(
				name= tournamentJson.get("name"),
				description= tournamentJson.get("description"),
				tourn_type= int(tournamentJson.get("type")) if tournamentJson.get("type") else 1,
				location_id= int(tournamentJson.get("location")) if tournamentJson.get("location") else None,
				tourn_date= renderedDateObject
			)
		if newTournament:
			return self.get_tournament_by_id(newTournament)
		else:
			return False

	def get_tournament_types(self):
		theseTypes = False
		results = self.db(self.db.tournament_types.id > 0).select()
		if results:
			theseTypes = []
			for result in results:
				theseTypes.append({"id":result.id,"name":result.tourn_type})
		return theseTypes

	def _render_datetime_object(self, date, time):
		dateTimeObj = False
		if date and time:
			dateString = str(date) + " " + str(time.get("hour")) + ":" + str(time.get("minute")) + ":00 " + time.get("meridian")
			from datetime import datetime
			dateTimeObj = datetime.strptime(dateString, '%m/%d/%Y %I:%M:%S %p')
		return dateTimeObj

	# def get_my_page(self):
	# 	pageSettings = {}
	# 	results = self.db(self.db.basic_site.id > 0).select().first()

	# 	pageSettings["pages"] = []
	# 	pageSettings["groups"] = []
	# 	if results:
	# 		pageSettings["siteID"] = results.id or None
	# 		pageSettings["title"] = results.page_title or "PlayersATX"
	# 		pageSettings["heading"] = results.page_header or "PlayersATX"
	# 		pageSettings["footer"] = results.page_footer or "PlayersATX"
	# 		pageSettings["subHeading"] = results.page_subheader or "PlayersATX"
	# 		pageSettings["tagLine"] = results.page_tagline or "PlayersATX"
	# 		pageSettings["description"] = results.page_desc or "The PlayersATX web site"
	# 		pageSettings["last_edit"] = results.modified or None
	# 		pageSettings["backgroundColor"] = results.background_color or None
	# 		pageSettings["backgroundStyle"] = results.background_img_style or None
	# 		pageSettings["backgroundImg"] = None
	# 		pageSettings["datePicker"] = False
	# 		if results.background_img:
	# 			imageData = self.db.image_library(results.background_img)
	# 			pageSettings["backgroundImg"] = imageData.image_file

	# 	else:
	# 		pageSettings["siteID"] = None
	# 		pageSettings["title"] = "PlayersATX"
	# 		pageSettings["heading"] = "PlayersATX"
	# 		pageSettings["footer"] = "PlayersATX"
	# 		pageSettings["subHeading"] = "PlayersATX"
	# 		pageSettings["tagLine"] = "PlayersATX"
	# 		pageSettings["description"] = "The PlayersATX web site"
	# 		pageSettings["last_edit"] = None
	# 		pageSettings["backgroundColor"] = None
	# 		pageSettings["backgroundStyle"] = None
	# 		pageSettings["backgroundImg"] = None
	# 		pageSettings["datePicker"] = False
	# 	query = self.db.page_types.id > 0
	# 	rawPages = self.db(query).select()
	# 	if rawPages:
	# 		for rawPage in rawPages:
	# 			if not rawPage.is_group:
	# 				thisPage = {
	# 					"id":rawPage.id,
	# 					"pageName":rawPage.page_name,
	# 					"pageFile":rawPage.page_file,
	# 					"group":rawPage.group
	# 				}
	# 				pageSettings["pages"].append(thisPage)
	# 			else:
	# 				thisGroup = {
	# 					"id":rawPage.id,
	# 					"pageName":rawPage.page_name,
	# 				}
	# 				pageSettings["groups"].append(thisGroup)

	# 	return pageSettings

	# def reorder_page_setting(self, dataID, action):
	# 	thisWorked = False
	# 	result = self.db.page_settings(dataID)
	# 	if result:
	# 		startPosition = int(result.data_order)
	# 		if action=="down":
	# 			query = (self.db.page_settings.page_type == result.page_type) & (self.db.page_settings.data_type == result.data_type) & (self.db.page_settings.data_order == startPosition + 1)
	# 			self.db(query).update(data_order=result.data_order)
	# 			self.db(self.db.page_settings.id == dataID).update(data_order=startPosition + 1)
	# 			thisWorked = True
	# 		elif action=="up":
	# 			query = (self.db.page_settings.page_type == result.page_type) & (self.db.page_settings.data_type == result.data_type) & (self.db.page_settings.data_order == startPosition - 1)
	# 			self.db(query).update(data_order=result.data_order)
	# 			self.db(self.db.page_settings.id == dataID).update(data_order=startPosition - 1)
	# 			thisWorked = True

	# 	return thisWorked

	# def remove_page_setting(self, dataID):
	# 	thisWorked = False
	# 	result = self.db.page_settings(dataID)
	# 	if result:
	# 		query = (self.db.page_settings.page_type == result.page_type) & (self.db.page_settings.data_type == result.data_type) & (self.db.page_settings.data_order > result.data_order)
	# 		reOrders = self.db(query).select()
	# 		if reOrders:
	# 			for thisSetting in reOrders:
	# 				self.db(self.db.page_settings.id == thisSetting.id).update(data_order=thisSetting.data_order - 1)
	# 		self.db(self.db.page_settings.id == dataID).delete()
	# 		thisWorked = True
	# 	return thisWorked