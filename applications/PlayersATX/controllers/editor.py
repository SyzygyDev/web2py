# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from BasicSite import *
basics = MainPage(db)
cardDAL = ContentCards(db)

from Events import Events
eventDAL = Events(db)

THISPAGE = basics.get_my_page()
THISPAGE['pageSetting'] = request.vars.page_id or None

@auth.requires_login()
@auth.requires_membership('Staff')
def doubler():
	updateID = request.vars.dupID or None
	updateKey = request.vars.key or None
	thisRecord =  request.vars.record or None
	fixMe =  request.vars.fixMe or None

	if updateID and fixMe:
		recordToFix = db.membership_duplicates(int(updateID))
		if recordToFix:
			thisWorked = recordToFix.update_record(fixed=True)
			if thisWorked:
				redirect(URL('editor', 'doubler'))

	keyMap = {
		"member1fName": "his_f_name",
		"member1lName": "his_l_name",
		"member1email": "his_email",
		"member1dob": "his_dob",
		"member1dl": "his_dl",
		"member2fName": "her_f_name",
		"member2lName": "her_l_name",
		"member2email": "her_email",
		"member2dob": "her_dob",
		"member2dl": "her_dl",
		"addressaddress": "address",
		"addresscity": "city",
		"addressstate": "state",
		"addresszip": "zip",
		"addressphone": "phone",
		"expiration": "expiration"
	}

	if updateID and updateKey and keyMap.get(updateKey):
		dupRecord = db.membership_duplicates(int(updateID))
		if dupRecord:
			if thisRecord == "old":
				sourceMemID = dupRecord.old_id
				targetMemID = dupRecord.new_id
			else:
				sourceMemID = dupRecord.new_id
				targetMemID = dupRecord.old_id

			sourceData = db(db.members.member_number == sourceMemID).select().first()

			targetRow = db(db.members.member_number == targetMemID).select().first()

			targetRow[keyMap[updateKey]] = sourceData[keyMap[updateKey]]

			thisWorked = targetRow.update_record()

			if thisWorked:
				redirect(URL('editor', 'doubler'))


			# query = db.members.member_number == dupRecord.old_id
			# masterRecord = db(query).select().first()
			# if masterRecord:
			# 	masterRecord.update_record(expiration=expiration)
			# thisWorked = dupRecord.update_record(fixed=True)
			# if thisWorked:
			# 	redirect(URL('editor', 'doubler'))
	duplicates = []
	query = db.membership_duplicates.fixed == False
	results = db(query).select()
	if results:
		from Members import Members
		memberObj = Members(db)
		for result in results:
			thisRecord = {
				"newMember": memberObj.get_member(result.new_id),
				"oldMember": memberObj.get_member(result.old_id),
				"dupID": result.id,
				"diffList": {}
			}
			count = 0
			for key, value in thisRecord["newMember"].iteritems():
				if key == "member1" or key == "member2" or key =="address":
					subObject = value
					if subObject:
						for subkey, subvalue in subObject.iteritems():
							if not thisRecord["newMember"][key][subkey] == thisRecord["oldMember"][key][subkey]:
								thisRecord["diffList"][key + subkey] = True
								count += 1

				elif key == "updated" or key == "memberID" or key =="id" or key =="status":
					thisKey = key
				else:
					if not thisRecord["newMember"][key] == thisRecord["oldMember"][key]:
						thisRecord["diffList"][key] = True
						count += 1

			if count <= 6:
				duplicates.append(thisRecord)


	return dict(duplicates=duplicates)


@auth.requires_login()
@auth.requires_membership('Admin')
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
	angularData = False

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
				fields=['page_title','page_header','page_footer','page_subheader','page_tagline','page_desc'],
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
			angularData = {
				"events": eventDAL.get_events(elementId),
				"thisPageID": "event"
			}
			# images=media.g
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
			angularData = {
				"images": media.get_images(),
				"thisPageID": "image"
			}
			# images=media.get_images()
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

	return dict(thisPage=THISPAGE, form=form, bgForm=bgForm, images=images, cards=cards, events=events, pageIdError=pageIdError, angularData=angularData)

@auth.requires_login()
@auth.requires_membership('Admin')
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
@auth.requires_membership('Admin')
def page_content():
	THISPAGE['pageSetting']='layout'
	pageId = int(request.vars.element_id) if request.vars.element_id else 1
	dataId = int(request.vars.data_id) if request.vars.data_id else None
	settingId = int(request.vars.setting_id) if request.vars.setting_id else None
	action = request.vars.action or None
	showEvents = request.vars.eventView or False

	form = False
	cards = False
	events = False
	partners = False
	angularData = False

	if pageId:
		if not action:
				cards = cardDAL.get_cards_by_page_id(pageId)
				events = eventDAL.get_events_by_page_id(pageId)
				angularData = {
					"message": "there was data",
					"events": events,
					"showEvents": showEvents,
					"thisPageID": pageId
				}

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
				angularData = {
					"message": "there was data",
					"events": eventDAL.get_events(),
					"showEvents": showEvents,
					"thisPageID": pageId
				}
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

	return dict(thisPage=THISPAGE, form=form, cards=cards, events=events, partners=partners, pageId=pageId, angularData=angularData)

@auth.requires_login()
@auth.requires_membership('Staff')
def front_desk():
	THISPAGE['pageSetting']='front_desk'
	from Members import Members
	memberObj = Members(db)

	angularData = memberObj.genterate_new_member_template()
	angularData["user"] = get_user()
	angularData["attendance"] = memberObj.get_current_attendance()

	return dict(thisPage=THISPAGE, angularData=angularData)

@auth.requires_login()
@auth.requires_membership('Admin')
def member_map():
	THISPAGE['pageSetting']='map'
	angularData = False

	return dict(thisPage=THISPAGE, angularData=angularData)


@auth.requires_login()
@auth.requires_membership('Admin')
def admin():
	sapID = request.vars.sap_id or 1
	userID = request.vars.user_id or None
	deleteUser = request.vars.delete_user or None
	sapID = int(sapID)
	sessionRole = 3
	if auth.has_membership('Super User'):
		sessionRole = 2
	THISPAGE['pageSetting']='admin'
	users = None
	form = False
	angularData = False
	sapPages = [
		{"id": 1, "pageName": "Attendance", "heading": "Search Attendance Records", "display": True},
		{"id": 2, "pageName": "Members", "heading": "Members Console", "display": True},
		{"id": 3, "pageName": "Change Logs", "heading": "Staff Database Change Log", "display": True},
		{"id": 4, "pageName": "Club Staff", "heading": "Staff Members with Web access", "display": True},
		{"id": 5, "pageName": "New Staff", "heading": "Add New Staff Login", "display": False},
		{"id": 6, "pageName": "Club Staff", "heading": "Edit Active Staff Login", "display": False},
		{"id": 7, "pageName": "Online Purchases", "heading": "Event Purchases made through the website", "display": True}
	]

	from AccountAdmin import AccountAdmin
	accountObj = AccountAdmin(db)

	if sapID <= 4:
		for page in sapPages:
			if sapID == page["id"]:
				thisPage = page
		from Members import Members
		memberObj = Members(db)

		angularData = memberObj.genterate_new_member_template()
		angularData["attendance"] = memberObj.get_current_attendance()
		angularData["pageData"] = thisPage
		angularData["pages"] = sapPages
		angularData["users"] = accountObj.get_accounts(sessionRole)

	else:

		if sapID == 5:
			form = SQLFORM(db.auth_user, submit_button='Create', fields=['first_name','last_name','email','password'])
			if form.process().accepted:
				accountObj.update_group_memberships([4], form.vars.id)
				redirect(URL('editor', 'admin', vars=dict(sap_id="4")))

		elif sapID == 6:
			if not userID:
				redirect(URL('editor', 'admin'))
			query = db.auth_user(db.auth_user.id == int(userID))
			form = SQLFORM(db.auth_user, query,
				submit_button='Update',
				showid=False,
				fields=['first_name','last_name','email','password'],
				formstyle="bootstrap")
			if form.process().accepted:
				redirect(URL('editor', 'admin', vars=dict(sap_id="4")))
			if deleteUser:
				from datetime import datetime
				now = datetime.now()
				db.auth_user(int(userID)).update_record(deleted=now)
				redirect(URL('editor', 'admin', vars=dict(sap_id="4")))

	return dict(thisPage=THISPAGE, sapPages=sapPages, form=form, angularData=angularData)


# @auth.requires_login()
# @auth.requires_membership('Super User')
# def create_user():
#     # Create a new administrative user account
#     if request.get_vars.org_id:
#         orgID = request.get_vars.org_id
#     elif request.post_vars.org_id:
#         orgID = request.post_vars.org_id
#     else:
#         orgID = ''

#     # Create user form
#     form = SQLFORM(db.auth_user, submit_button='Create', fields=['first_name','last_name','email','password'])

#     if form.process().accepted:
#         from AccountAdmin import AccountAdmin
#         accountObj = AccountAdmin(db)

#         # Add the user to the 'Administrator' group
#         accountObj.set_organization_administrator(form.vars.id)

#         if orgID:
#             # Make the user a member of the given organization
#             accountObj.create_organization_membership(orgID, form.vars.id)

#         # Redirect the user to the users screen
#         redirect(URL('tadmin', 'users', vars=dict(org_id=orgID)))
#     elif form.errors:
#         response.flash = 'The form contains errors.'
#     else:
#         response.flash = 'Please complete the form.'

#     return dict(form=form, orgID=orgID)


# @auth.requires_login()
# @auth.requires_membership('Super User')
# def edit_user():
#     userID = request.vars.uid or None
#     view = request.vars.view or 'user'
#     action = request.vars.action or None
#     roleIDs = request.vars.role_ids or None

#     # Retrieve the users existing organization membership for navigation
#     from AccountAdmin import AccountAdmin
#     accountObj = AccountAdmin(db, userID)
#     accountObj.load_account()
#     orgID = accountObj.get_organization_membership()

#     if view == 'user':
#         # Build user edit form
#         user = db.auth_user(db.auth_user.id==userID)
#         form = SQLFORM(db.auth_user, user, submit_button='Update', deletable=True, showid=False,
#                        fields=['first_name','last_name','email','password'])
#         if form.process().accepted:
#             # Determine if the user account was deleted
#             if db(db.auth_user.id==userID).count() == 0:
#                 # The user account was deleted - remove the organization membership
#                 accountObj.delete_organization_membership(userID)

#                 # Redirect to the Users screen
#                 if orgID:
#                     redirect(URL('tadmin', 'users', vars=dict(org_id=orgID)))
#                 else:
#                     redirect(URL('tadmin', 'users'))
#             else:
#                 response.flash = 'The user account has been updated.'
#         elif form.errors:
#             response.flash = 'The form contains errors.'

#         return dict(view=view, form=form, orgID=orgID, user=accountObj)
#     elif view == 'role':
#         # Get the list of available roles
#         roles = accountObj.get_available_groups()

#         if roleIDs:
#             if action == 'update':
#                 # Add the user to the given role(s)
#                 accountObj.update_group_memberships(roleIDs, userID)
#                 response.flash = 'User roles updated'

#         userRoleIDs = accountObj.get_group_memberships(userID)

#         return dict(view=view, orgID=orgID, user=accountObj, roles=roles, userRoleIDs=userRoleIDs)

def get_user():
	tempUser = auth.user
	if not tempUser:
		return False
	else:
		return {"fName": tempUser.first_name, "lName": tempUser.last_name, "email": tempUser.email}

