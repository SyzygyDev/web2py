# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from BasicSite import *
basics = MainPage(db)
cardDAL = ContentCards(db)
eventDAL = Events(db)

THISPAGE = basics.get_my_page()
THISPAGE['pageSetting'] = request.vars.page_id or None

@auth.requires_login()
def update():
	pageSetting = request.vars.page_id or "advanced"
	elementId = int(request.vars.element_id) if request.vars.element_id else None
	pageIdError = False
	form=False
	bgForm = False
	images=False
	cards=False
	events=False
	THISPAGE['pageSetting'] = pageSetting

	from Media import Media
	media = Media(db)


# ******************BASIC PAGE********************
	if pageSetting=="advanced":
		query = db.basic_site.id>0
		result = db(query).select().first()
		if result:
			if result.background_img:
				images=media.get_images(result.background_img)
			query = db.basic_site(db.basic_site.id==result.id)
			form = SQLFORM(db.basic_site, query,
				submit_button='Update',
				showid=False,
				fields=['page_title','page_header','page_footer','page_subheader','page_tagline','page_desc'],
				formstyle="bootstrap")
			for input in form.elements('input'):
				input['_style']='width:100%'
			form.element('textarea[name=page_desc]')['_style']='width:100%'
			bgForm = SQLFORM(db.basic_site, query,
				showid=False,
				submit_button='save background settings',
				fields=['background_color','background_img_style'],
				formstyle="bootstrap")
			for input in bgForm.elements('input'):
				input['_style']='width:100%'

			if bgForm.process(formname='bgForm').accepted:
				# redirect(URL('profile', 'broken', vars=dict(account_key=accountKey)))
				redirect(URL('editor', 'update'))

		else:
			form = SQLFORM(db.basic_site,
				submit_button='Create',
				fields=['page_title','page_header','page_subheader','page_tagline','page_desc'],
				formstyle="bootstrap")
			for input in form.elements('input'):
				input['_style']='width:100%'
			form.element('textarea[name=page_desc]')['_style']='width:100%'

		if form.process(formname='form').accepted:
			redirect(URL('editor', 'update'))

	elif pageSetting=="layout":
		form=False


# ******************CONTENT PAGE********************
	elif pageSetting=="content":
		if not elementId:
			cards=cardDAL.get_content_cards()
			form = SQLFORM(db.content_card,
				submit_button='Create',
				fields=['card_name','card_heading','body_text'],
				formstyle="bootstrap")
			for input in form.elements('input'):
				input['_style']='width:100%'
			form.element('textarea[name=body_text]')['_style']='width:100%'

			if form.process(formname='form').accepted:
				redirect(URL('editor', 'update', vars=dict(page_id="content")))

		else:
			cards=cardDAL.get_content_cards(elementId)
			if not cards:
				redirect(URL('editor', 'update', vars=dict(page_id="content")))
			query = db.content_card(db.content_card.id == elementId)
			form = SQLFORM(db.content_card, query,
				submit_button='Update',
				deletable=True,
				showid=False,
				fields=['card_name','card_heading','body_text'],
				formstyle="bootstrap")
			for input in form.elements('input'):
				input['_style']='width:100%'
			form.element('textarea[name=body_text]')['_style']='width:100%'

			if form.process(formname='form').accepted:
				redirect(URL('editor', 'update', vars=dict(page_id="content", element_id=elementId)))


# ******************EVENT PAGE********************
	elif pageSetting=="event":
		if not elementId:
			events=eventDAL.get_events()
			form = SQLFORM(db.events,
				submit_button='Create',
				fields=['event_name','event_heading','body_text', 'expiration'],
				formstyle="bootstrap")
			for input in form.elements('input'):
				input['_style']='width:100%'
			form.element('textarea[name=body_text]')['_style']='width:100%'

			if form.process(formname='form').accepted:
				redirect(URL('editor', 'update', vars=dict(page_id="event")))

		else:
			events=eventDAL.get_events(elementId)
			if not events:
				redirect(URL('editor', 'update', vars=dict(page_id="event")))
			query = db.events(db.events.id == elementId)
			form = SQLFORM(db.events, query,
				submit_button='Update',
				deletable=True,
				showid=False,
				fields=['event_name','event_heading','body_text', 'expiration'],
				formstyle="bootstrap")
			for input in form.elements('input'):
				input['_style']='width:100%'
			form.element('textarea[name=body_text]')['_style']='width:100%'

			if form.process(formname='form').accepted:
				redirect(URL('editor', 'update', vars=dict(page_id="event", element_id=elementId)))


# ******************IMAGE PAGE********************
	elif pageSetting=="image":
		if not elementId:
			images=media.get_images()
			form = SQLFORM(db.image_library,
				submit_button='Upload',
				fields=['image_name','image_desc','keywords','image_file'],
				formstyle="bootstrap")
			for input in form.elements('input'):
				input['_style']='width:100%'
			form.element('textarea[name=image_desc]')['_style']='width:100%'

			if form.process(formname='form').accepted:
				media.process_key_words(form.vars.id)
				redirect(URL('editor', 'update', vars=dict(page_id="image")))

		else:
			images=media.get_images(elementId)
			if not images:
				redirect(URL('editor', 'update', vars=dict(page_id="image")))
			query = db.image_library(db.image_library.id == elementId)
			form = SQLFORM(db.image_library, query,
				submit_button='Update',
				deletable=True,
				showid=False,
				fields=['image_name','image_desc','keywords'],
				formstyle="bootstrap")
			for input in form.elements('input'):
				input['_style']='width:100%'
			form.element('textarea[name=image_desc]')['_style']='width:100%'

			if form.process(formname='form').accepted:
				media.process_key_words(form.vars.id)
				redirect(URL('editor', 'update', vars=dict(page_id="image", element_id=elementId)))

	else:
		pageIdError="You are poking around where you dont belong, try something else, or close your browser and login in again"

	return dict(thisPage=THISPAGE, form=form, bgForm=bgForm, images=images, cards=cards, events=events, pageIdError=pageIdError)

@auth.requires_login()
def assign_image():
	assignSource = request.vars.page_id
	elementId = int(request.vars.element_id) if request.vars.element_id else None
	if not request.vars.image_id == "blank":
		imageId = int(request.vars.image_id) if request.vars.image_id else None
	else:
		imageId = "blank"

	if not assignSource and elementId:
		redirect(URL('editor', 'update', vars=dict(page_id="image")))

	from Media import Media
	media = Media(db)

	if imageId:
		pageRedirect = media.assign_image(imageId, assignSource, elementId)
		if pageRedirect:
			redirect(URL('editor', 'update', vars=dict(page_id=pageRedirect, element_id=elementId)))
		else:
			redirect(URL('editor', 'assign_image', vars=dict(page_id=assignSource, element_id=elementId)))

	images=media.get_images()
	form = SQLFORM(db.image_library,
		submit_button='Upload',
		fields=['image_name','image_desc','keywords','image_file'],
		formstyle="bootstrap")
	for input in form.elements('input'):
		input['_style']='width:100%'
	form.element('textarea[name=image_desc]')['_style']='width:100%'

	if form.process(formname='form').accepted:
		media.process_key_words(form.vars.id)
		pageRedirect = media.assign_image(form.vars.id, assignSource, elementId)
		if pageRedirect:
			redirect(URL('editor', 'update', vars=dict(page_id=pageRedirect, element_id=elementId)))
		else:
			redirect(URL('editor', 'assign_image', vars=dict(page_id=assignSource, element_id=elementId)))

	return dict(thisPage=THISPAGE, form=form, images=images)

@auth.requires_login()
def page_content():
	THISPAGE['pageSetting']='layout'
	pageId = int(request.vars.element_id) if request.vars.element_id else 1
	dataId = int(request.vars.data_id) if request.vars.data_id else None
	settingId = int(request.vars.setting_id) if request.vars.setting_id else None
	action = request.vars.action or None

	form = False
	cards = False
	events = False
	partners= False

	if pageId:
		if not action:
				import operator
				cards = cardDAL.get_cards_by_page_id(pageId)
				events = eventDAL.get_events_by_page_id(pageId)

		if action == "add_card":
			if dataId:
				newItemOrder = cardDAL.get_new_card_position(pageId)
				settingId = db.page_settings.insert(
					page_type=pageId,
					data_type="content",
					data_card=dataId,
					data_order=newItemOrder)
				if settingId:
					redirect(URL('editor', 'page_content', vars=dict(element_id=pageId)))

			else:
				cards = cardDAL.get_content_cards()

		if action == "add_event":
			if dataId:
				newItemOrder = eventDAL.get_new_event_position(pageId)
				settingId = db.page_settings.insert(
					page_type=pageId,
					data_type="event",
					data_card=dataId,
					data_order=newItemOrder)
				if settingId:
					redirect(URL('editor', 'page_content', vars=dict(element_id=pageId)))

			else:
				events = eventDAL.get_events()

		elif action == "edit":
			cards=cardDAL.get_data_cards(dataID=settingId)
			events=eventDAL.get_data_events(dataID=settingId)
			if cards:
				query = db.page_settings(db.page_settings.id==settingId)
				form = SQLFORM(db.page_settings, query,
					submit_button='Save Size',
					showid=False,
					fields=['alt_image', 'image_size'],
					formstyle="bootstrap")
			elif events:
				query = db.page_settings(db.page_settings.id==settingId)
				form = SQLFORM(db.page_settings, query,
					submit_button='Save Layout',
					showid=False,
					fields=['alt_image', 'layout_style'],
					formstyle="bootstrap")

			if cards or events:
				if form.process(formname='form').accepted:
					redirect(URL('editor', 'page_content', vars=dict(element_id=pageId, setting_id=settingId, action='edit')))

		elif action == "down" or action == "up":
			if basics.reorder_page_setting(settingId, action):
				redirect(URL('editor', 'page_content', vars=dict(element_id=pageId)))
		elif action == "remove":
			if basics.remove_page_setting(settingId):
				redirect(URL('editor', 'page_content', vars=dict(element_id=pageId)))

	# 	redirect(URL('editor', 'update', vars=dict(page_id="image")))

	# from Media import Media
	# media = Media(db)

	# if imageId:
	# 	pageRedirect = media.assign_image(imageId, assignSource, elementId)
	# 	if pageRedirect:
	# 		redirect(URL('editor', 'update', vars=dict(page_id=pageRedirect, element_id=elementId)))
	# 	else:
	# 		redirect(URL('editor', 'assign', vars=dict(page_id=assignSource, element_id=elementId)))

	# images=media.get_images()
	# form = SQLFORM(db.image_library,
	# 	submit_button='Upload',
	# 	fields=['image_name','image_desc','keywords','image_file'],
	# 	formstyle="bootstrap")
	# for input in form.elements('input'):
	# 	input['_style']='width:100%'
	# form.element('textarea[name=image_desc]')['_style']='width:100%'

	# if form.process(formname='form').accepted:
	# 	media.process_key_words(form.vars.id)
	# 	pageRedirect = media.assign_image(form.vars.id, assignSource, elementId)
	# 	if pageRedirect:
	# 		redirect(URL('editor', 'update', vars=dict(page_id=pageRedirect, element_id=elementId)))
	# 	else:
	# 		redirect(URL('editor', 'assign', vars=dict(page_id=assignSource, element_id=elementId)))

	return dict(thisPage=THISPAGE, form=form, cards=cards, events=events, partners=partners)