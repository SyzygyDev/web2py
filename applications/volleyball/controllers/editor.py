# -*- coding: utf-8 -*-

@auth.requires_login()
@auth.requires_membership('Admin')
def index():
    locationID = request.vars.location or None
    angularData = {
        "userData":auth.user.email
    }
    if locationID:
        angularData["location"] = locationID

    return dict(angularData=angularData)

@auth.requires_login()
@auth.requires_membership('Admin')
def new_location():
    referer = request.vars.referer or None
    angularData = {
        "userData":auth.user.email
    }
    if referer:
        angularData["referer"] = referer
    return dict(angularData=angularData)

def terms():
    return dict(message=T('Hello World'))

def signup():
    form1 = False
    form2 = False
    angularData = {"noData":True}
    if auth.is_logged_in():
        if auth.has_membership('Admin'):
            redirect(URL("editor", "index"))
        if len(auth.user_groups) < 1:
            auth.add_membership(3, auth.user.id)
        angularData = {
            "userData":auth.user,
            "groups":auth.user_groups
        }
    else:
        form1=auth.register()
        form2=auth.login()
    return dict(form1=form1, form2=form2, angularData=angularData)

@auth.requires_login()
def register2():
    angularData = False
    if auth.is_logged_in():
        if auth.has_membership('Admin'):
            redirect(URL("editor", "index"))
        ANGULAR_DATA = {
            "UserID":auth.user_id
        }
    return dict(form1=auth.register(), form2=auth.login(), angularData=ANGULAR_DATA)

def schedule():
    return dict(message=T('Hello World'))

def contact():
    return dict(message=T('Hello World'))

def results():
    bracketData = {
        "tournament":_get_tournament_data(),
        "teams":_get_teams_data(),
    }
    ANGULAR_DATA = {
        "bracketData":bracketData
    }
    return dict(angularData=ANGULAR_DATA)

def bracketA():
    angularData = {"teams":request.vars.team_count or None}
    return dict(angularData=angularData)


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

def _get_tournament_data():
    return {"type":"SE","conferences":[{"matches":[[{"team1":{"id":"1","score":8},"team2":{"id":"2","score":11},"meta":{"matchId":"match-C1-1-1"},"details":{}},{"team1":{"id":"3","score":""},"team2":{"id":"4","score":""},"meta":{"matchId":"match-C1-1-2"},"details":{}},{"team1":{"id":"5","score":""},"team2":{"id":"6","score":""},"meta":{"matchId":"match-C1-1-3"},"details":{}},{"team1":{"id":"7","score":""},"team2":{"id":"8","score":""},"meta":{"matchId":"match-C1-1-4"},"details":{}}],[{"team1":{"id":"9","score":""},"team2":{"id":"2","score":""},"meta":{"matchId":"match-C1-2-1","matchType":1},"details":{}},{"team1":{"id":"10","score":""},"team2":{"id":"","score":""},"meta":{"matchId":"match-C1-2-2","matchType":1},"details":{}},{"team1":{"id":"11","score":""},"team2":{"id":"","score":""},"meta":{"matchId":"match-C1-2-3","matchType":1},"details":{}},{"team1":{"id":"12","score":""},"team2":{"id":"","score":""},"meta":{"matchId":"match-C1-2-4","matchType":1},"details":{}}],[{"team1":{"id":"","score":""},"team2":{"id":"","score":""},"meta":{"matchId":"match-C1-3-1"},"details":{}},{"team1":{"id":"","score":""},"team2":{"id":"","score":""},"meta":{"matchId":"match-C1-3-2"},"details":{}}],[{"team1":{"id":"","score":""},"team2":{"id":"","score":""},"meta":{"matchId":"match-C1-4-1","matchType":"finals"},"details":{}},{"team1":{"id":"","score":""},"team2":{"id":"","score":""},"meta":{"matchId":"match-C1-4-2","matchType":"bronze"},"details":{}}]]}],"properties":{"status":"In progress"}}

def _get_teams_data():
    return [[{"name":"Team 1","id":"1","flag":"","members":[]},{"name":"Team 2","id":"2","flag":"","members":[]},{"name":"Team 3","id":"3","flag":"","members":[]},{"name":"Team 4","id":"4","flag":"","members":[]},{"name":"Team 5","id":"5","flag":"","members":[]},{"name":"Team 6","id":"6","flag":"","members":[]},{"name":"Team 7","id":"7","flag":"","members":[]},{"name":"Team 8","id":"8","flag":"","members":[]},{"name":"Team 9","id":"9","flag":"","members":[]},{"name":"Team 10","id":"10","flag":"","members":[]},{"name":"Team 11","id":"11","flag":"","members":[]},{"name":"Team 12","id":"12","flag":"","members":[]}]]

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
