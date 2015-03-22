#!/usr/bin/env python
# coding: utf8
from gluon import *

import os
try:
	from PIL import Image, ImageOps
except:
	import Image, ImageOps

def image_generator(file_name, box, fit=True, name=""):
	'''Downsample the image.
	@param img: Image - an Image-object
	@param box: tuple(x, y) - the bounding box of the result image
	@param fit: boolean - crop the image to fill the box
	'''
	if file_name:
		request = current.request
		image_dir = _find_image_dir__(file_name, os.path.join(request.folder, 'uploads'))
		img = Image.open(os.path.join(image_dir, file_name))# Convert to RGB if necessary
		if img.mode not in ('L', 'RGB'):
			img = img.convert('RGB')
		if fit:
			img = ImageOps.fit(img, box, Image.ANTIALIAS)
		else:
			img.thumbnail(box, Image.ANTIALIAS)
		root, ext = os.path.splitext(file_name)
		# I use PNG since there is no lost of quality with it way of compression
		thisImage = '%s_%s%s' % (root, name, '.png')
		img.save(os.path.join(image_dir, thisImage), 'PNG')
	return thisImage

def _find_image_dir__(name, path):
	for root, dirs, files in os.walk(path):
		if name in files:
			return root

class Media:
	def __init__(self, db):
		self.db = db

	def get_images(self, mediaID=''):
		if mediaID:
			return self.db.image_library(mediaID)
		else:
			query = self.db.image_library.id>0
			return self.db(query).select()

	def assign_image(self, mediaID, assignSource, elementId):
		if not mediaID:
			return False

		returnPage = False

		SOURCEMAP = {
			"basic":{"table":"basic_site","column":"background_img", "page":"basic"},
			"content-left":{"table":"content_card","column":"left_image", "page":"content"},
			"content-right":{"table":"content_card","column":"right_image", "page":"content"},
			"event":{"table":"events","column":"event_image", "page":"event"}
		}

		if SOURCEMAP.get(assignSource):
			thisTable = SOURCEMAP[assignSource]["table"]
			thisColumn = SOURCEMAP[assignSource]["column"]
			query = self.db[thisTable].id == elementId
			result = self.db(query).select().first()
			if result:
				if mediaID == "blank":
					mediaID = None
				result[thisColumn] = mediaID
				self.db(query).update(**self.db[thisTable]._filter_fields(result))
				returnPage = SOURCEMAP[assignSource]["page"]

		return returnPage



	def process_key_words(self, mediaID=''):
		if mediaID:
			# query = self.db.account_albums.id == albumID
			# if self.db(query).update(name=name, view_level=viewLevel, description=notes):

			result = self.db.image_library(mediaID)
			if result:
				query = self.db.image_key_words.image_id == mediaID
				self.db(query).delete()
				if result.keywords:
					keyWords = result.keywords.split()
					for keyWord in keyWords:
						self.db.image_key_words.insert(image_id=mediaID, key_word=keyWord)

