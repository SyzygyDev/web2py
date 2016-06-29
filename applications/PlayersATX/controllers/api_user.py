# -*- coding: utf-8 -*-
import logging

apiVersion = '0.9'

import gluon.contrib.simplejson as simplejson

from Events import Events
eventDAL = Events(db)

# The following line is required for .json output.
# Note: There are security implications related to generic views.
# See:
#   https://groups.google.com/forum/?fromgroups=#!topic/web2py/Jk-TIoQhRh4
#   http://comments.gmane.org/gmane.comp.python.web2py/67902
response.generic_patterns = ['json', 'jsonp']

response.headers['Cache-Control'] = "max-age=0"

def verify_member_id():
    memberID = request.vars.memberID or None
    memberLastName = request.vars.name or None
    memberInfo = False
    processMemberInfo = False
    responses = []

    if memberID and memberLastName:
        query = (db.members.member_number == memberID) | (db.members.his_l_name == memberLastName) | (db.members.her_l_name == memberLastName)
        memberRecords = db(query).select()
        if memberRecords:
            for memberRecord in memberRecords:
                responses.append({"rowID": memberRecord.member_number, "compare": memberID})
                if not memberInfo:
                    if memberID == memberRecord.member_number:
                        if memberLastName == memberRecord.his_l_name or memberLastName == memberRecord.her_l_name:
                            processMemberInfo = True

                    if processMemberInfo:
                        memberInfo = {
                            "fName": memberRecord.his_f_name,
                            "lName": memberRecord.his_l_name,
                            "fName1": memberRecord.her_f_name,
                            "lName1": memberRecord.her_l_name,
                            "email": memberRecord.his_email or memberRecord.her_email or None,
                            "status": "valid"
                        }
                        if memberRecord.gender:
                            memberInfo["gender"] = db.gender_types(memberRecord.gender).gender_label

                        if memberRecord.expiration:
                            from datetime import datetime, timedelta
                            TODAY = datetime.now().date()
                            if memberRecord.expiration < TODAY:
                                memberInfo["status"] = "expired"

                        if memberRecord.status:
                            memberStatus = db.membership_type(memberRecord.status).membership_label
                            if memberStatus == "Revoked":
                                memberInfo["status"] = "Revoked"

        else:
            memberInfo = getTestMemberData(memberID)


    return api_response(memberInfo=memberInfo, tempInfo=responses)

def purchase_event():
    jsonData = simplejson.loads(request.body.read()) if request.body else {}
    purchaseOrder = False
    if jsonData:
        from Purchase import Purchase
        purchaseObj = Purchase(db)

        purchaseOrder = purchaseObj.create_purchase_order(jsonData)

        if purchaseOrder:
            if purchaseOrder.get("successCode") == 1:
                from datetime import datetime
                PurchaseDateTime = datetime.now().strftime( "%A, %b %d %Y at %I:%M:%S %p" ) + "(GMT)"
                thisMessage = "On " + PurchaseDateTime + ":\n" + jsonData.get("fName") + " " + jsonData.get("lName") + "\n"
                if jsonData.get("memberID"):
                    thisMessage = thisMessage + "Member ID - " + jsonData.get("memberID") + "\n"
                if jsonData.get("fName1") and jsonData.get("lName1"):
                    thisMessage = thisMessage + "attending with" + jsonData.get("fName1") + " " + jsonData.get("lName1") + "\n"

                thisMessage = thisMessage + "Purchased: " + jsonData.get("label") + "\n"
                if purchaseOrder.get("eventName"):
                    thisMessage = thisMessage + "for " + purchaseOrder.get("eventName") + "\n"
                thisMessage = thisMessage + "Cost: $" + str(jsonData.get("price", 0)) + "\n"
                thisMessage = thisMessage + "___________________________________________\nThe transaction was approved.\n"
                thisMessage = thisMessage + "NMI transaction ID: " + purchaseOrder.get("txnID") + "\n"
                thisMessage = thisMessage + "Players Confirmation Code: " + purchaseOrder.get("confirmation") + "\n"

                x = mail.send(to=['reservations@playersatx.club'],
                    subject="Event Purchase Online",
                    message= thisMessage)
                if x == True and jsonData.get("email"):
                    cardMap = {
                        "card": "Credit",
                        "amex": "American Express",
                        "visa": "Visa",
                        "mastercard": "Mastercard",
                        "discover": "Discover"
                    }
                    otherMessage = "On " + PurchaseDateTime + ":\n"
                    otherMessage = otherMessage + jsonData.get("billingData")["firstname"] + " " + jsonData.get("billingData")["lastname"] + "'s\n"
                    otherMessage = otherMessage + cardMap[jsonData.get("cardData", {"thisCard":"card"})["thisCard"]] + " card ending in \""
                    otherMessage = otherMessage + jsonData.get("cardData")["cleanCCnumber"][-4:] + "\" was charged\n"
                    otherMessage = otherMessage + "$" + str(jsonData.get("price", 0)) + "\n"
                    otherMessage = otherMessage + "Purchased: " + jsonData.get("label") + "\n"
                    if purchaseOrder.get("eventName"):
                        otherMessage = otherMessage + "for " + purchaseOrder.get("eventName") + "\n"
                    otherMessage = otherMessage + "___________________________________________\nThe purchase was approved\n"

                    otherMessage = otherMessage + "for " + jsonData.get("fName") + " " + jsonData.get("lName") + ", "
                    if jsonData.get("memberID"):
                        otherMessage = otherMessage + "Member ID - " + jsonData.get("memberID")
                    if jsonData.get("fName1") and jsonData.get("lName1"):
                        otherMessage = otherMessage + ",\n" + "who will be attending with " + jsonData.get("fName1") + " " + jsonData.get("lName1") + "\n"
                    otherMessage = otherMessage + "Players Confirmation Code: " + purchaseOrder.get("confirmation") + "\n"
                    mail.send(to=[jsonData.get("email")],
                        subject="Purchase confirmation",
                        message= otherMessage)

    return api_response(thisPurchase=purchaseOrder)

def members_export():
    mailSent = False
    from Members import Members
    exportData = Members(db).export_members()
    if exportData["memberExport"]:
        import cStringIO
        import csv
        stream = cStringIO.StringIO()

        fieldNames = [
            'Member Number',
            'Member Type',
            'Expiration',
            'His Last Name',
            'His First Name',
            'His Email',
            'His DoB',
            'His DL',
            'Her Last Name',
            'Her First Name',
            'Her Email',
            'Her DoB',
            'Her DL',
            'Address',
            'City',
            'State',
            'Zip',
            'Phone'
        ]

        csv_writer = csv.writer(stream)
        csv_writer.writerow(fieldNames)
        for member in exportData["memberExport"]:
            currentRow = (
                member['member_number'],
                member['member_type'],
                member['expiration'],
                member['his_lName'],
                member['his_fName'],
                member['his_email'],
                member['his_dob'],
                member['his_dl'],
                member['her_lName'],
                member['her_fName'],
                member['her_email'],
                member['her_dob'],
                member['her_dl'],
                member['address'],
                member['city'],
                member['state'],
                member['zip'],
                member['phone']
            )
            csv_writer.writerow(currentRow)

        stream.seek(0)
        mailSent = mail.send(to=['admin@playersatx.club','syzygywebbed@gmail.com'],
            subject= str(exportData["exportDate"]) + " Member List",
            message= "Here is the members list as of " + str(exportData["exportDate"]) + "\n\nThis is an automated email.",
            attachments = mail.Attachment(stream, filename='memberDatabase.csv')
        )
    return api_response(Mail_sent=mailSent)


def api_response(**kwargs):
    resp = dict(**kwargs)

    resp.update({
        'version': apiVersion,
        'success': True
    })

    return resp

def getTestMemberData(memberID):
    memberInfo = False
    if memberID == "c123":
        memberInfo = {
            "fName": "Cade",
            "lName": "Moore",
            "fName1": "Mesha",
            "lName1": "Moore",
            "email": "cadeatwork@gmail.com",
            "gender": "Couple",
            "status": "valid"
        }
    elif memberID == "c456":
        memberInfo = {
            "fName": "Cade",
            "lName": "Moore",
            "fName1": "Mesha",
            "lName1": "Moore",
            "email": "cadeatwork@gmail.com",
            "gender": "Couple",
            "status": "expired"
        }
    elif memberID == "t123":
        memberInfo = {
            "fName": "Tammy",
            "lName": "Szabo",
            "fName1": None,
            "lName1": None,
            "email": "tammy@mycrotch.com",
            "gender": "Single Female",
            "status": "valid"
        }
    elif memberID == "s123":
        memberInfo = {
            "fName": "Rob",
            "lName": "Szabo",
            "fName1": None,
            "lName1": None,
            "email": "rob@insane.com",
            "gender": "Single Male",
            "status": "Revoked"
        }

    return memberInfo