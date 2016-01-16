#!/usr/bin/env python
# coding: utf8
from gluon import *
import requests

class Purchase:
	def __init__(self, db):
		self.db = db

	def get_current_purchases(self, eventID=""):
		from datetime import datetime, timedelta
		AFTERME = datetime.now() - timedelta(days=4)
		AFTERME = AFTERME.date()
		BEFOREME = datetime.now() + timedelta(days=4)
		BEFOREME = BEFOREME.date()
		purchases = False

		if eventID:
			purchases = False
		else:
			query = (self.db.events.expiration >= AFTERME) & (self.db.events.expiration <= BEFOREME)
			events = self.db(query).select()
			if events:
				for event in events:
					thisEventPurchases = self._get_purchase_by_event(event)
					if thisEventPurchases:
						if not purchases:
							purchases = []
						purchases = purchases + thisEventPurchases
		return purchases

	def _get_purchase_by_event(self, event):
		purchaseReturn = False
		if event:
			query = self.db.event_price.event_id == event.id
			prices = self.db(query).select()
			if prices:
				for price in prices:
					query = (self.db.purchases.price_id == price.id) & (self.db.purchases.is_pending == False)
					purchases = self.db(query).select()
					if purchases:
						if not purchaseReturn:
							purchaseReturn = []
						for purchase in purchases:
							thisPurchase = self._extract_purchase(purchase)
							if thisPurchase:
								buyLabel = self.db.event_price_label(price.price_label_id).price_label if self.db.event_price_label() else None
								thisPurchase["buy"] = buyLabel
								purchaseReturn.append(thisPurchase)

			if purchaseReturn:
				for purchase in purchaseReturn:
					purchase["eventDate"] = event.expiration
					purchase["event"] = event.event_name

		return purchaseReturn

	def _extract_purchase(self, purchaseRow):
		memberKey = None
		if not purchaseRow:
			return False
		if purchaseRow.notes:
			notes =  purchaseRow.f_name + " " + purchaseRow.l_name + " " + purchaseRow.notes
		else:
			notes = purchaseRow.f_name + " " + purchaseRow.l_name

		if purchaseRow.member_id:
			memberRow = self.db.members(purchaseRow.member_id)
			if memberRow:
				memberKey = memberRow.member_number

		thisPurchase = {
			"id": purchaseRow.id,
			"confirmation": purchaseRow.purchase_id,
			"memberID": memberKey,
			"lName": purchaseRow.l_name,
			"fName": purchaseRow.f_name,
			"purchaser": notes,
			"email": purchaseRow.e_mail,
			"purchaseDate": purchaseRow.update_date
		}
		return thisPurchase



	def create_purchase_order(self, purchaseJson):
		priceID = purchaseJson.get("id")
		purchaseResponse = False
		if priceID:
			priceID = int(priceID)
			purchaseOrderID = purchaseJson.get("purchaseOrderID")
			if not purchaseOrderID:
				purchaseKey = self._gen_purchase_key()
				memberID = None
				memberKey = purchaseJson.get("memberID")
				if memberKey:
					memberID = self.db(self.db.members.member_number == memberKey).select().first()
					if memberID:
						memberID = memberID.id
				fName1 = purchaseJson.get("fName1")
				lName1 = purchaseJson.get("lName1")
				if fName1 and lName1:
					purchaseJson["notes"] = "attending with " + fName1 + " " + lName1
				purchaseOrderID = self.db.purchases.insert(
					purchase_id=purchaseKey,
					price_id=priceID,
					member_id=memberID,
					f_name=purchaseJson.get("fName"),
					l_name=purchaseJson.get("lName"),
					e_mail=purchaseJson.get("email"),
					notes=purchaseJson.get("notes")
				)
				purchaseOrderID = str(purchaseOrderID)

			if purchaseOrderID:
				purchaseResponse = self._do_sale(
					purchaseOrderID,
					purchaseJson.get("label"),
					purchaseJson.get("billingData"),
					purchaseJson.get("cardData"),
					purchaseJson.get("price"),
					int(purchaseJson.get("attempt", 1))
				)

				if purchaseResponse:
					purchaseRecord = self.db.purchases(int(purchaseOrderID))
					if purchaseResponse["successCode"] == 1:
						txnID = purchaseResponse["txnID"]
						isPending = False
						purchaseResponse["confirmation"] = purchaseKey

						query = (self.db.events.id == self.db.event_price.event_id) & (self.db.event_price.id == priceID)
						result = self.db(query).select().first()
						if result:
							purchaseResponse["eventName"] = result.events.event_name

					else:
						txnID = purchaseResponse["txnID"] + "-" + purchaseResponse["reasonCode"]
						isPending = True

					purchaseRecord.update_record(is_pending=isPending, temp_number=txnID)

		return purchaseResponse

	def purchase_info(self, eventID):
		thisReturn = {
			"summary": [],
			"purchases": []
		}
		if eventID:
			# GET ALL PRICES FOR EVENT
			purchaseResults = self.db(self.db.event_price.event_id == eventID).select()
			if purchaseResults:
				purchaseIDArray = []
				for purchaseResult in purchaseResults:
					purchaseIDArray.append(purchaseResult.id)
				purchases = thisReturn["purchases"]
				results = self.db(self.db.purchases.price_id.belongs(purchaseIDArray)).select()
				if results:
					for result in results:
						thisPurchase = {
							"purchaseID": result.purchase_id,
							"completed": result.update_date,
							"transactionID": None,
							"failed": result.is_pending,
							"reason": None,
							"email": result.e_mail,
							"fName": result.f_name,
							"lName": result.l_name,
							"extras": result.notes,
							"price": None,
							"priceID": result.price_id,
							"priceLabel": None,
							"eventID": None,
							"event": None
						}

						if "-" in result.temp_number:
							transArray = result.temp_number.split("-")
							thisPurchase["transactionID"] = transArray[0]
							thisPurchase["reason"] = transArray[1]
						else:
							thisPurchase["transactionID"] = result.temp_number

						priceRow = self.db.event_price(result.price_id)
						if priceRow:
							thisPurchase["price"] = priceRow.price
							thisPurchase["priceLabel"] = self.db.event_price_label(priceRow.price_label_id).price_label
							thisPurchase["eventID"] = priceRow.event_id
							thisPurchase["event"] = self.db.events(priceRow.event_id).event_name

						purchases.append(thisPurchase)
		else:
			summary = thisReturn["summary"]
			results = self.db(self.db.event_price.id >= 1).select(self.db.event_price.event_id, distinct=True)
			if results:
				from decimal import *
				for result in results:
					thisSummary = {
						"eventID": result.event_id,
						"failures": 0,
						"purchases": 0,
						"revenue": 0.00,
						"event": "",
						"eventDate": False
					}
					eventDetails = self.db.events(result.event_id)
					if eventDetails:
						thisSummary["event"] = eventDetails.event_name
						thisSummary["eventDate"] = eventDetails.expiration
					priceArray = self.db(self.db.event_price.event_id == result.event_id).select()
					if priceArray:
						for priceRow in priceArray:
							query = (self.db.purchases.is_pending == False) & (self.db.purchases.price_id == priceRow.id)
							purchaseCount = self.db(query).count()
							thisSummary["purchases"] = thisSummary["purchases"] + purchaseCount
							thisSummary["revenue"] = Decimal(thisSummary["revenue"]) + Decimal(Decimal(purchaseCount) * priceRow.price)

							query = (self.db.purchases.is_pending == True) & (self.db.purchases.price_id == priceRow.id)
							failCount = self.db(query).count()
							thisSummary["failures"] = thisSummary["failures"] + failCount

					if thisSummary["purchases"] >= 1:
						summary.append(thisSummary)

		return thisReturn

	def _gen_purchase_key(self):
		import random, string
		exists = False

		newKey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		newKey = newKey.replace("O", "0");
		if self.db(self.db.purchases.purchase_id == newKey).count() > 0:
			exists = True

		if exists:
			return self._gen_purchase_key()
		else:
			return newKey


	def _do_sale(self, orderid, orderdescription, billingJson, cardJson, amount, attempt):
		responseData = False
		txnPost = {}

		# ORDER INFO
		txnPost['username'] = "kimjo512"
		txnPost['password'] = "Dragline2010"
		txnPost['orderid'] = orderid;
		txnPost['orderdescription'] = orderdescription

		# BILLING INFO
		txnPost['firstname'] = billingJson.get("firstname")
		txnPost['lastname']  = billingJson.get("lastname")
		txnPost['address1']  = billingJson.get("address1")
		txnPost['address2']  = billingJson.get("address2")
		txnPost['city']      = billingJson.get("city")
		txnPost['state']     = billingJson.get("state")
		txnPost['zip']       = billingJson.get("zip")
		txnPost['country']   = "US"

		# CARD INFO
		txnPost['ccnumber'] = cardJson.get("cleanCCnumber")
		txnPost['ccexp'] = cardJson.get("ccExpMonth") + cardJson.get("ccExpYear")
		txnPost['cvv'] = cardJson.get("cvv");

		# SALE INFO
		txnPost["amount"] = amount
		txnPost["type"] = 'sale'

		r = requests.post("https://secure.nmi.com/api/transact.php", data=txnPost)
		if r:
			responseData = {}
			extraData = {}
			responses = r.text.split("&")
			for response in responses:
				tempResponse = response.split("=")
				if tempResponse[0] == "response":
					responseData["successCode"] = int(tempResponse[1])
				extraData[tempResponse[0]] = self._check__code(tempResponse[0], tempResponse[1])

			if responseData.get("successCode") > 1:
				responseData["reasonCode"] = extraData.get("response_code")

			responseData["txnID"] = extraData.get("transactionid")


		return responseData

	def _check__code(self, codeType, responseCode):
		result = responseCode
		codeMap = {
			"response_code":{
				"100":"Transaction was approved.",
				"200":"Transaction was declined by processor.",
				"201":"Do not honor.",
				"202":"Insufficient funds.",
				"203":"Over limit.",
				"204":"Transaction not allowed.",
				"220":"Incorrect payment information.",
				"221":"No such card issuer.",
				"222":"No card number on file with issuer.",
				"223":"Expired card.",
				"224":"Invalid expiration date.",
				"225":"Invalid card security code.",
				"240":"Call issuer for further information.",
				"250":"Pick up card.",
				"251":"Lost card.",
				"252":"Stolen card.",
				"253":"Fraudulent card.",
				"260":"Declined with further instructions available.", #(See response text) 
				"261":"Declined-Stop all recurring payments.",
				"262":"Declined-Stop this recurring program.",
				"263":"Declined-Update cardholder data available.",
				"264":"Declined-Retry in a few days.",
				"300":"Transaction was rejected by gateway.",
				"400":"Transaction error returned by processor.",
				"410":"Invalid merchant configuration.",
				"411":"Merchant account is inactive.",
				"420":"Communication error.",
				"421":"Communication error with issuer.",
				"430":"Duplicate transaction at processor.",
				"440":"Processor format error.",
				"441":"Invalid transaction information.",
				"460":"Processor feature not available.",
				"461":"Unsupported card type."
			},
			"cvvresponse":{
				"M":"CVV2/CVC2 match",
				"N":"CVV2/CVC2 no match",
				"P":"Not processed",
				"S":"Merchant has indicated that CVV2/CVC2 is not present on card",
				"U":"Issuer is not certified and/or has not provided Visa encryption keys"
			},
			"avsresponse":{
				"X":"Exact match, 9-character numeric ZIP",
				"Y":"Exact match, 5-character numeric ZIP",
				"D":"Exact match, 5-character numeric ZIP",
				"M":"Exact match, 5-character numeric ZIP",
				"A":"Address match only",
				"B":"Address match only",
				"W":"9-character numeric ZIP match only",
				"Z":"5-character ZIP match only",
				"P":"5-character ZIP match only",
				"L":"5-character ZIP match only",
				"N":"No address or ZIP match only",
				"C":"No address or ZIP match only",
				"U":"Address unavailable",
				"G":"Non-U.S. issuer does not participate",
				"I":"Non-U.S. issuer does not participate",
				"R":"Issuer system unavailable",
				"E":"Not a mail/phone order",
				"S":"Service not supported",
				"O":"AVS not available",
				"B":"AVS not available"
			}
		}

		codeObj = codeMap.get(codeType)
		if codeObj:
			result = codeObj.get(responseCode) or result

		return result