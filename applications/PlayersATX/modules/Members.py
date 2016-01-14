#!/usr/bin/env python
# coding: utf8
from gluon import *
from datetime import datetime, timedelta

class Members:
	def __init__(self, db):
		self.db = db

	def member_is_checked_in(self, memberRowID):
		if not memberRowID:
			return False
		TODAY = datetime.now() - timedelta(hours=9)
		TODAY = TODAY.date()
		query = (self.db.attendance.attend_date == TODAY) & (self.db.attendance.member_id == memberRowID)
		return self.db(query).count() >= 1


	def get_executive_members(self, user, memberRowID=False, gender=False):
		TODAY = datetime.now() - timedelta(hours=9)
		TODAY = TODAY.date()
		checkedIn = False
		if memberRowID and gender:
			if not self.member_is_checked_in(memberRowID):
				genderID = self.db(self.db.gender_types.gender_label == gender).select().first()
				genderID = genderID.id if genderID else 1
				self.db.attendance.insert(member_id=memberRowID, gender=genderID, staff_id=user.id, attend_date=TODAY)
				checkedIn = memberRowID
			else:
				checkedIn = memberRowID

		members=False
		query = (self.db.members.status == self.db.membership_type.id) & (self.db.membership_type.membership_label == "Executive VIP")
		member_rows = self.db(query).select()
		if member_rows:
			members = []
			for mRow in member_rows:
				tempMember = self._extract_member(mRow.members)

				query = self.db.purchases.member_id == mRow.members.id
				purchases = self.db(query).select()
				if purchases:
					tempMember["purchases"] = self._extract_member_purchases(purchases)

				if checkedIn and checkedIn == mRow.members.id:
					tempMember["checkedIn"] = True
				else:
					query = (self.db.attendance.attend_date == TODAY) & (self.db.attendance.member_id == mRow.members.id)
					tempMember["checkedIn"] = self.db(query).count() >= 1

				members.append(tempMember)

		return members

	def get_member_by_row_id(self, memberRowID):
		if not memberRowID:
			return False

		member=False
		member_row = self.db.members(memberRowID)
		if member_row:
			member = self._extract_member(member_row)
			query = self.db.purchases.member_id == member_row.id
			purchases = self.db(query).select()
			if purchases:
				member["purchases"] = self._extract_member_purchases(purchases)

		return member

	def get_member(self, memberKey):
		member=False
		if memberKey:
			query = self.db.members.member_number == memberKey
			result = self.db(query).select().first()
			if result:
				member = self._extract_member(result)
				query = self.db.purchases.member_id == result.id
				purchases = self.db(query).select()
				if purchases:
					member["purchases"] = self._extract_member_purchases(purchases)

		return member

	def get_member_duplicates(self, memberKey):
		members = False
		if memberKey:
			query = (self.db.membership_duplicates.old_id == memberKey) & (self.db.membership_duplicates.fixed == False)
			results = self.db(query).select()
			if results:
				for result in results:
					memberRow = self.db.members(result.member_id)
					if memberRow:
						thisMember = self._extract_member(memberRow)
						if thisMember:
							if not members:
								members = []
							members.append(thisMember)

		return members


	def get_members_by_last_name(self, lastName):
		members=False
		memberArray = False
		if lastName:
			query = self.db.members.his_l_name == lastName
			results = self.db(query).select()
			if results:
				members = {}
				for result in results:
					if not result.member_number in members:
						members[result.member_number] = {
							'fname1': result.his_f_name,
							'lname1': result.his_l_name,
							'dob1': result.his_dob,
							'dl1': result.his_dl,
							'fname2': result.her_f_name,
							'lname2': result.her_l_name,
							'dob2': result.her_dob,
							'dl2': result.her_dl
						}
			query = self.db.members.her_l_name == lastName
			results2 = self.db(query).select()
			if results2:
				if not members:
					members = {}
				for result in results2:
					tempArray = {
						'fname2': result.her_f_name,
						'lname2': result.her_l_name,
						'dob2': result.her_dob,
						'dl2': result.her_dl
					}
					if not result.member_number in members:
						if result.his_f_name or result.his_l_name:
							members[result.member_number] = {
								'fname1': result.his_f_name,
								'lname1': result.his_l_name,
								'dob1': result.his_dob,
								'dl1': result.his_dl
							}
							members[result.member_number].update(tempArray)
						else:
							members[result.member_number] = {
								'fname1': result.her_f_name,
								'lname1': result.her_l_name,
								'dob1': result.her_dob,
								'dl1': result.her_dl
							}
					else:
						members[result.member_number].update(tempArray)

			if members:
				memberArray = []
				for key, value in members.iteritems():
					thisRow = value
					thisRow.update({"memberKey":key})
					memberArray.append(thisRow)

		if memberArray:
			if len(memberArray) == 1:
				return self.get_member(memberArray[0]["memberKey"])

		return memberArray


	def _extract_member(self, member):
		TODAY = datetime.now() - timedelta(hours=9)
		TODAY = TODAY.date()
		thisMember = {}
		thisMember["id"] = member.id
		thisMember["memberID"] = member.member_number
		thisMember["gender"] = self.db.gender_types(member.gender).gender_label if member.gender else "missing"
		thisMember["memberType"] = self.db.membership_type(member.status).membership_label if member.status else "missing"
		thisMember["expiration"] = member.expiration
		thisMember["status"] = "valid"
		thisMember["pending"] = member.is_pending
		thisMember["updated"] = member.update_date
		thisMember["pendingReason"] = False
		thisMember["member1"] = False
		thisMember["member2"] = False
		thisMember["address"] = False
		thisMember["purchases"] = False
		thisMember["credits"] = self._get_credits_by_row_id(member.id)

		if member.expiration:
			if member.expiration < TODAY:
				thisMember["status"] = "expired"

		if thisMember["memberType"] == "Revoked":
			thisMember["status"] = "Revoked"

		if member.his_f_name or member.his_l_name:
			thisMember["member1"] = {
				'fName': member.his_f_name,
				'lName': member.his_l_name,
				'email': member.his_email,
				'dob': member.his_dob,
				'dl': member.his_dl
			}

		if member.her_f_name or member.her_l_name:
			tempStuff = {
				'fName': member.her_f_name,
				'lName': member.her_l_name,
				'email': member.her_email,
				'dob': member.her_dob,
				'dl': member.her_dl
			}
			if not thisMember["member1"]:
				thisMember["member1"] = tempStuff
			else:
				thisMember["member2"] = tempStuff

		if member.zip or member.state or member.city or member.address:
			thisMember["address"] = {
				'address': member.address,
				'city': member.city,
				'state': member.state,
				'zip': member.zip,
				'phone': member.phone
			}

		if thisMember["pending"]:
			if not member.member_number:
				thisMember["pendingReason"] = "No Membership ID"
			elif not member.his_dl and not member.her_dl:
				thisMember["pendingReason"] = "ID not verified"

		return thisMember

	def _extract_member_purchases(self, purchases):
		purchaseList = False
		for purchase in purchases:
			thisPurchase = False
			if not purchase.is_pending:
				thisPrice = self.db.event_price(purchase.price_id)
				if thisPrice:
					thisPurchase = {}
					thisPurchase["notes"] = purchase.f_name + " " + purchase.l_name
					thisPurchase["completed"] = purchase.update_date
					thisPurchase["event"] = False
					thisPurchase["priceLabel"] = False

					if purchase.notes:
						thisPurchase["notes"] = thisPurchase["notes"] + " " + purchase.notes
					event = self.db.events(thisPrice.event_id)
					if event:
						thisPurchase["event"] = event.event_name
						thisPurchase["eventDate"] = event.expiration
					price_label = self.db.event_price_label(thisPrice.price_label_id)
					if price_label:
						thisPurchase["priceLabel"] = price_label.price_label

			if thisPurchase:
				if not purchaseList:
					purchaseList = []

				purchaseList.append(thisPurchase)

		return purchaseList

	def create_new_member(self, memberJson, isAdmin=False):
		newMemberKey = False
		if memberJson.get("memberID"):
			isPending = False if isAdmin else True

			Expires = False
			if memberJson.get("expires"):
				Expires =  memberJson.get("expires")
			elif memberJson.get("duration"):
				if memberJson.get("duration") == "year":
					from datetime import date
					Expires = datetime.now().date()
					try:
						Expires = Expires.replace(year = Expires.year + 1)
					except ValueError:
						# THIS ACCOUNTS FOR LEAPYEARS, TURNING FEB 29TH INTO MARCH 1ST. A LITTLE OVERILL? MAYBE
						Expires = Expires + (date(Expires.year + 1, 1, 1) - date(Expires.year, 1, 1))
				elif memberJson.get("duration") == "weekend":
					Expires = datetime.now() + timedelta(days=5)
					Expires = Expires.date()

			newMember = self.db.members.insert(
				member_number= memberJson.get("memberID"),
				address= memberJson.get("address"),
				city= memberJson.get("city"),
				state=memberJson.get("state"),
				zip=memberJson.get("zip"),
				phone=memberJson.get("phone"),
				gender= int(memberJson.get("gender")) if memberJson.get("gender") else 1,
				status= int(memberJson.get("memberType")) if memberJson.get("memberType") else 1,
				expiration=Expires,
				his_f_name= memberJson.get("hisFname"),
				his_l_name= memberJson.get("hisLname"),
				his_email= memberJson.get("hisEmail"),
				his_dob= memberJson.get("hisDob"),
				his_dl= memberJson.get("hisDl"),
				her_f_name= memberJson.get("herFname"),
				her_l_name= memberJson.get("herLname"),
				her_email= memberJson.get("herEmail"),
				her_dob= memberJson.get("herDob"),
				her_dl= memberJson.get("herDl"),
				is_pending=isPending
			)
			if newMember:
				thisKey = self.db.members(newMember)
				if thisKey:
					newMemberKey = thisKey.member_number
		return newMemberKey

	def edit_member(self, memberJson):
		memberKey = False
		if memberJson.get("memberID"):
			address = memberJson.get("address") or {}
			him = memberJson.get("member1") or {}
			her = memberJson.get("member2") or {}
			query = self.db.gender_types.gender_label == memberJson.get("gender")
			gender = self.db(query).select().first()
			query = self.db.membership_type.membership_label == memberJson.get("memberType")
			status = self.db(query).select().first()
			query = self.db.members.member_number == memberJson.get("memberID")
			member_row = self.db(query).select().first()
			if member_row:
				if member_row.update_record(
					member_number= memberJson.get("memberID"),
					address= address.get("address"),
					city= address.get("city"),
					state=address.get("state"),
					zip=address.get("zip"),
					phone=address.get("phone"),
					gender= gender.id if gender else 1,
					status= status.id if status else 1,
					expiration= memberJson.get("expiration"),
					his_f_name= him.get("fName"),
					his_l_name= him.get("lName"),
					his_email= him.get("email"),
					his_dob= him.get("dob"),
					his_dl= him.get("dl"),
					her_f_name= her.get("fName"),
					her_l_name= her.get("lName"),
					her_email= her.get("email"),
					her_dob= her.get("dob"),
					her_dl= her.get("dl")
				):
					memberKey = memberJson.get("memberID")
		return memberKey

	def verify_new_member(self, memberJson, user):
		return memberJson


	def get_current_attendance(self, showMembers=False, searchDate=False):
		TODAY = datetime.now() - timedelta(hours=9)
		TODAY = searchDate or TODAY.date()

		attendance = {"date": TODAY, "count": 0, "members": [], "summary":{"Staff":0,"Standard":0,"VIP":0, "credits":0}}

		query = self.db.attendance.attend_date == TODAY
		results = self.db(query).select()
		if results:
			for result in results:
				personCount = 1 if result.gender > 1 else 2
				attendance["count"] += personCount
				if result.credit:
					attendance["summary"]["credits"] += personCount
				if showMembers:
					member_row = self.db.members(result.member_id)
					if member_row:
						gender = self.db.gender_types(member_row.gender)
						thisMember = {
							"id": member_row.id,
							"memberID": member_row.member_number,
							"memberType": "member_row.status",
							"gender": gender.gender_label if gender else False,
							"name": "",
							"staffID": result.staff_id,
							"staffName": ""
						}

						if member_row.status:
							if member_row.status == 2:
								attendance["summary"]["VIP"] += personCount
							elif member_row.status == 3:
								attendance["summary"]["Staff"] += personCount
							else:
								attendance["summary"]["Standard"] += personCount
							membershipType = self.db.membership_type(member_row.status)
							if membershipType:
								thisMember["memberType"] = membershipType.membership_label

						if member_row.his_f_name or member_row.his_l_name:
							thisMember["name"] += str(member_row.his_f_name) + " " + str(member_row.his_l_name)
						if member_row.her_f_name or member_row.her_l_name:
							if thisMember["name"]:
								thisMember["name"] += " and "
							thisMember["name"] += str(member_row.her_f_name) + " " + str(member_row.her_l_name)

						if result.staff_id:
							thisStaffer = self.db.auth_user(result.staff_id)
							if thisStaffer:
								thisMember["staffName"] = thisStaffer.first_name + " " + thisStaffer.last_name

						attendance["members"].append(thisMember)

		return attendance


	def check_member_in(self, memberID, gender, user, usedCredit=None):
		if not user:
			return False

		if not self.member_is_checked_in(memberID):
			TODAY = datetime.now() - timedelta(hours=9)
			TODAY = TODAY.date()
			genderID = self.db(self.db.gender_types.gender_label == gender).select().first()
			genderID = genderID.id if genderID else 1
			usedCredit = int(usedCredit) if usedCredit else None

			credits = self.use_credit(memberID, usedCredit)

			self.db.attendance.insert(member_id=memberID, gender=genderID, staff_id=user.id, attend_date=TODAY, credit=usedCredit)

		return self.get_current_attendance(True)


	def renew_this_member(self, memberID, renewalType, testMode=False):
		member = False
		if memberID:
			member_row = self.db.members(memberID)
			if member_row:
				from datetime import date
				NOW = datetime.now().date()
				if member_row.expiration:
					if member_row.expiration > NOW:
						NOW = member_row.expiration

				if renewalType == "weekend":
					newExpiration = NOW + timedelta(days=5)
				elif renewalType == "year":
					try:
						newExpiration = NOW.replace(year = NOW.year + 1)
					except ValueError:
						# THIS ACCOUNTS FOR LEAPYEARS, TURNING FEB 29TH INTO MARCH 1ST. A LITTLE OVERILL? MAYBE
						newExpiration = NOW + (date(NOW.year + 1, 1, 1) - date(NOW.year, 1, 1))
				else:
					try:
						newExpiration = NOW + timedelta(int(renewalType)*365/12)
					except:
						newExpiration = False

				if not testMode:
					if member_row.update_record(expiration=newExpiration):
						member = self.get_member_by_row_id(memberID)

				else:
					member = self.get_member_by_row_id(memberID)
					if member:
						member["expiration"] = newExpiration
		return member

	def genterate_new_member_template(self):
		newMemberTemplate = {
			"newMemberID": self.genterate_new_key(),
			"genderOptions": False,
			"memberTypeOptions": False
		}
		genders = self.db().select(self.db.gender_types.ALL)
		if genders:
			newMemberTemplate["genderOptions"] = []
			for gender in genders:
				newMemberTemplate["genderOptions"].append({"id": gender.id, "label": gender.gender_label})

		memberTypes = self.db().select(self.db.membership_type.ALL)
		if memberTypes:
			newMemberTemplate["memberTypeOptions"] = []
			for mType in memberTypes:
				if not mType.membership_label == "Revoked":
					newMemberTemplate["memberTypeOptions"].append({"id": mType.id, "label": mType.membership_label})

		return newMemberTemplate

	def genterate_new_key(self):
		import random, string
		exists = False

		newKey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
		newKey = newKey.replace("O", "0");
		if self.db(self.db.members.member_number == newKey).count() > 0:
			exists = True

		if exists:
			return self.genterate_new_key()
		else:
			return newKey

	def get_staff_actions(self, range, staffID):
		staffActions = False
		if range:
			from datetime import date
			NOW = datetime.now() - timedelta(hours=9)
			if range == "week":
				NOW = NOW - timedelta(days=7)
			elif range == "month":
				NOW = NOW - timedelta(1*365/12)

			query = self.db.staff_logs.created >= NOW
			if staffID:
				query = query & (self.db.staff_logs.staff_id == int(staffID))

			results = self.db(query).select()
			if results:
				staffActions = []
				for result in results:
					thisChange = {
						"action": result.staff_action,
						"actionDate": result.created
					}
					staffer = self.db.auth_user(result.staff_id)
					if staffer:
						thisChange["staffer"] = staffer.first_name + " " + staffer.last_name
					staffActions.append(thisChange)

		return staffActions

	def _get_credits_by_row_id(self, memberRowID):
		credits = False
		if memberRowID:
			query = (self.db.member_credits.member_id == memberRowID) & (self.db.member_credits.used == None)
			results = self.db(query).select()
			if results:
				credits = []
				for result in results:
					thisCredit = {
						"creditID": result.id,
						"creditLabel": result.credit
					}
					credits.append(thisCredit)
		return credits


	def create_credit(self, memberID, creditType):
		credits = False
		if memberID and creditType:
			creditMap = {
				"enter-f": "Free Standard entry - Friday",
				"enter-s": "Free Standard entry - Saturday",
				"enterplus-f": "Free VIP entry - Friday",
				"enterplus-s": "Free VIP entry - Saturday",
				"vip": "Free VIP upgrade with paided entry"
			}

			newID = self.db.member_credits.insert(
				member_id= int(memberID),
				credit= creditMap[creditType]
			)
			if newID:
				credits = self._get_credits_by_row_id(int(memberID))

		return credits

	def use_credit(self, memberID, creditID):
		credits = False
		if memberID and creditID:
			credit = self.db.member_credits(int(creditID))
			if credit:
				from datetime import date
				thisWorked = credit.update_record(used=datetime.now())
				if thisWorked:
					credits = self._get_credits_by_row_id(int(memberID))

		return credits

class MembersComments:
	def __init__(self, db, memberID):
		self.db = db
		self.memberID = memberID

	def get_comments(self):
		commentQuery = self.db.member_comments.member_id == self.memberID
		# WE ARE USING THE ABOVE DECLARED QUERY AS A FILTER ON THE DB, NOTICE TABLE IS DECLARED IN THE FILTER
		commentRows = self.db(commentQuery).select()
		if commentRows:
			memberComments = []
			for comment in commentRows:
				thisComment = {
					"made_by": False,
					"created": comment.create_date,
					"comment": comment.comment
				}
				# SINCE WE ARE USING ROW ID, WE DO NOT NEED A QUERY, ON A FILTER AT THE TABLE LEVEL
				user = self.db.auth_user(comment.staff_id)
				if user:
					thisComment["made_by"] = user.first_name + " " + user.last_name

				memberComments.append(thisComment)

			return memberComments
		return False

	def set_comment(self, staffID, comment):
		if staffID and comment:
			newCommentID = self.db.member_comments.insert(
				member_id=self.memberID,
				staff_id=int(staffID),
				comment=comment
			)
			if newCommentID:
				self.db.commit()
				return self.get_comments()
		else:
			return False


