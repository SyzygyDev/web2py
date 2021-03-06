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
    emailSuccess = False

    form = SQLFORM.factory(
        Field('first_name', requires=IS_NOT_EMPTY()),
        Field('last_name', requires=IS_NOT_EMPTY()),
        Field('email', requires =[ IS_EMAIL(error_message='You must provide a valid email!'), IS_NOT_EMPTY() ]),
        Field('Phone_Number', label="Phone Number"),
        Field('message', requires=IS_NOT_EMPTY(), type='text')
    )
    if form.process().accepted:
        from datetime import datetime
        messageSent = datetime.now().strftime( "%A, %b %d %Y at %I:%M:%S %p" )
        thisMessage = "On " + messageSent + ":\nFrom: " + form.vars.first_name + " " + form.vars.last_name + "\n" + "Email address: " + form.vars.email + "\n"
        if form.vars.Phone_Number:
            thisMessage = thisMessage + "Phone: " + form.vars.Phone_Number + "\n"
        thisMessage = thisMessage + "\n___________________________________________\nMessage: \n" + form.vars.message

        x = mail.send(to=['Kim@CryoStudioNorth.com'],
            subject="CryoStudioNorth.com website response",
            message= thisMessage)
        if x == True:
            emailSuccess = True
            otherMessage = "Cryo Studio North is waiting to serve you. We are by appointment only.\n"
            otherMessage = otherMessage + "Our staff typically responds during this time, but we will get to your email as soon as we can.\n\n\n" 
            otherMessage = otherMessage + "We recieved the following:\n" + thisMessage
            mail.send(to=[form.vars.email],
                subject="We appreciate your email",
                message= otherMessage)
    return dict(form=form, emailSuccess=emailSuccess)


# def user():
#     """
#     exposes:
#     http://..../[app]/default/user/login
#     http://..../[app]/default/user/logout
#     http://..../[app]/default/user/register
#     http://..../[app]/default/user/profile
#     http://..../[app]/default/user/retrieve_password
#     http://..../[app]/default/user/change_password
#     http://..../[app]/default/user/manage_users (requires membership in
#     use @auth.requires_login()
#         @auth.requires_membership('group name')
#         @auth.requires_permission('read','table name',record_id)
#     to decorate functions that need access control
#     """
#     return dict(form=auth())

# @cache.action()
# def download():
#     """
#     allows downloading of uploaded files
#     http://..../[app]/default/download/[filename]
#     """
#     return response.download(request, db)


# def call():
#     """
#     exposes services. for example:
#     http://..../[app]/default/call/jsonrpc
#     decorate with @services.jsonrpc the functions to expose
#     supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
#     """
#     return service()


# @auth.requires_signature()
# def data():
#     """
#     http://..../[app]/default/data/tables
#     http://..../[app]/default/data/create/[table]
#     http://..../[app]/default/data/read/[table]/[id]
#     http://..../[app]/default/data/update/[table]/[id]
#     http://..../[app]/default/data/delete/[table]/[id]
#     http://..../[app]/default/data/select/[table]
#     http://..../[app]/default/data/search/[table]
#     but URLs must be signed, i.e. linked with
#       A('table',_href=URL('data/tables',user_signature=True))
#     or with the signed load operator
#       LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
#     """
#     return dict(form=crud())
