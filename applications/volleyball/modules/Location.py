#!/usr/bin/env python
# coding: utf8
from gluon import *

class Location:
	def __init__(self, db):
		self.db = db

	def get_locations(self):
		locationArray = False
		query = self.db.locations.id >= 1
		results = self.db(query).select()
		if results:
			locationArray = []
			for result in results:
				thisLocation = self._extract_location(result)
				locationArray.append(thisLocation)

		return locationArray

	def get_location_by_id(self, locationID):
		return self._extract_location(self.db.locations(locationID))

	def create_new_location(self, locationJson):
		coords = False
		lat = locationJson.get("lat")
		lon = locationJson.get("lon")
		if lat and lon:
			coords = "lat:" + lat + "|lon:" + lon

		newLocation = self.db.locations.insert(
			name=locationJson.get("name"),
			google_place_id=locationJson.get("googlePlaceId"),
			location_coords=coords,
			location_address=locationJson.get("address"),
			location_url=locationJson.get("webSite"),
			location_img_url=locationJson.get("imgUrl"),
			location_img=locationJson.get("image"),
		)

		return newLocation

	def _extract_location(self, location):
		thisLocation = False
		if not location:
			return False

		thisLocation = {
			"id":location.id,
			"name":location.name,
			"googlePlaceID":location.google_place_id,
			"address":location.location_address,
			"imgLink":location.location_img_url,
			"image":False
		}
		if location.location_coords:
			coordArray = self._extractPipeEncodedValues(location.location_coords)
			if coordArray:
				thisLocation.update(coordArray)

		if location.location_img:
			image = self.db.image_library(location.location_img)
			if image:
				thisLocation["image"] = {
					"name":image.image_name,
					"img":image.image_file,
					"thumb":image,
					"banner":image
				}

		return thisLocation

	def _extractPipeEncodedValues(self, pipeEncodedString):
	    elems = pipeEncodedString.split('|')
	    attrs = {}

	    # String was not properly pipe encoded, so there are no attributes to extract
	    if len(elems) == 1 and ":" not in elems[0]:
	        return attrs

	    for elem in elems:
	        if elem:
	            field, value = elem.split(':', 1)
	            attrs[field] = value

	    return attrs