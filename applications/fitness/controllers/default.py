# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    return dict()

def coaching():
    return dict()

def services():
    return dict()


def contact():
    emailSuccess = False

    subjectKey = request.vars.key or None
    subjectMap = {
        "pgt": "Personal Gym Training",
        "nc": "Nutritional Consultation",
        "tc": "Training Consultation",
        "spc": "Skype/Phone Consultations",
        "cp": "Contest Preparation",
        "fc": "1:1 fitness coaching",
        "ofc": "Online fitness coaching"
    }

    emailSubject = subjectMap.get(subjectKey) if subjectKey else False


    form = SQLFORM.factory(
        Field('name', requires=IS_NOT_EMPTY()),
        Field('email', requires =[ IS_EMAIL(error_message='You must provide a valid email!'), IS_NOT_EMPTY() ]),
        Field('Phone_Number', label="Phone Number"),
        Field('message', requires=IS_NOT_EMPTY(), type='text')
    )
    if form.process().accepted:
        from datetime import datetime
        messageSent = datetime.now().strftime( "%A, %b %d %Y at %I:%M:%S %p" )
        thisMessage = "On " + messageSent + ":\nFrom: " + form.vars.name + "\n" + "Email address: " + form.vars.email + "\n"
        if form.vars.Phone_Number:
            thisMessage = thisMessage + "Phone: " + form.vars.Phone_Number + "\n"
        thisMessage = thisMessage + "___________________________________________\n\nMessage: \n" + form.vars.message

        x = mail.send(to=['web_contact@gimmeamonth.com'],
            subject=emailSubject or "Fitness website response",
            message= thisMessage)
        if x == True:
            emailSuccess = thisMessage
            # otherMessage = "The club is open Fridays 9:00pm to 2:00am and Saturdays 9:00pm to 3:00am.\n"
            # otherMessage = otherMessage + "Our staff typically responds during this time, but we will get to your email as soon as we can.\n\n\n" 
            # otherMessage = otherMessage + "We recieved the following:\n" + thisMessage
            # mail.send(to=[form.vars.email],
            #     subject="We appreciate your email",
            #     message= otherMessage)
    return dict(form=form, emailSuccess=emailSuccess, emailSubject=emailSubject)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
