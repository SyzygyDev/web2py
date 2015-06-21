# coding: utf8

apiVersion = '1.0'

import gluon.contrib.simplejson as simplejson

response.generic_patterns = ['json', 'jsonp']

@auth.requires_login()
def get_tournaments():
    from Tournament import Tournament
    TournamentObj = Tournament (db)
    tournaments = TournamentObj.get_tournaments()
    from Location import Location
    LocationObj = Location (db)
    locations=LocationObj.get_locations()
    if auth.has_membership('Admin'):
        types=TournamentObj.get_tournament_types()
        return api_response(tournaments=tournaments, types=types, locations=locations)
    else:
        return api_response(tournaments=tournaments, locations=locations)

@auth.requires_login()
def new_tournament():
    jsonData = simplejson.loads(request.body.read()) if request.body else {}
    tournament = False
    if jsonData:
        from Tournament import Tournament
        TournamentObj = Tournament (db)
        tournament = TournamentObj.create_new_tournament(jsonData)
    if tournament:
        return api_response(tournament=tournament)
    else:
        return api_error(message="Something went wrong, we'll figure it out")

@auth.requires_login()
def new_location():
    jsonData = simplejson.loads(request.body.read()) if request.body else {}
    newLocationID = False
    if jsonData:
        from Location import Location
        LocationObj = Location (db)
        newLocationID = LocationObj.create_new_location(jsonData)
    if newLocationID:
        return api_response(locationID=newLocationID)
    else:
        return api_error(message="Something went wrong, we'll figure it out")

@auth.requires_login()
def get_tournaments1():
    projectID = request.vars.project_id or None
    showDetails = False if (request.vars.show_details == "false") else True
    from Project import Project
    projectObj = Project(db)

    if not showDetails:
        results = db(db.projects.owner == session.organization).count()
        return api_response(project=results)

    else:
        # Retrieve the list of projects belonging to the organization
        if projectID:
            project = projectObj.get_project(projectID)
            if project:
                appKey = project.get("default_app_key") or None
                if not appKey:
                    appKey = projectObj.get_app_key_from_project(projectID)

                if appKey:
                    from Application import Application
                    application = Application(db)
                    appSettings = application.get_application(appKey)
                    projectAppSettings = {}
                    projectAppSettings['nickname'] = appSettings['nickname']
                    projectAppSettings['domain'] = appSettings['domain']
                    projectAppSettings['touUrl'] = appSettings['touUrl']
                    projectAppSettings['privacyUrl'] = appSettings['privacyUrl']
                    projectAppSettings['facebookAppID'] = appSettings['facebookAppID']
                    projectAppSettings['googleAnalyticsCode'] = appSettings['googleAnalyticsCode']
                    projectAppSettings['headerImageUrl'] = appSettings['headerImageUrl']
                    projectAppSettings['iconImageUrl'] = appSettings['iconImageUrl']

                    project.update(projectAppSettings)

                return api_response(project=project)
            else:
                return api_error('Input03', "Nope")

        else:
            projects = projectObj.get_projects_by_owner(session.organization)

            if projects:
                from TMLocation import Event
                eventObj = Event(db)
                from Poll import Poll
                pollObj = Poll(db)
                for project in projects:
                    project['thumbnails'] = []
                    for activity in project['activities']:
                        if activity['coverImageUrl']:
                            if len(project['thumbnails']) < 9:
                                alreadyExists = False
                                for image in project['thumbnails']:
                                    if image == activity['coverImageUrl']:
                                        alreadyExists = True

                                if not alreadyExists:
                                    project['thumbnails'].append(activity['coverImageUrl'])

                    project['events'] = eventObj.get_events_by_project(project['projectID'], "all")
                    project['contests'] = pollObj.get_polls(projectID=project['projectID'], details=False)

                return api_response(projects=projects)
            else:
                return api_response(projects=None)


@auth.requires_login()
def reassign_ingredient():
    jsonData = simplejson.loads(request.body.read()) if request.body else {}
    layoutName = jsonData.get("layoutName")
    oldID = jsonData.get("oldID")
    newID = jsonData.get("newID")
    removeOld = jsonData.get("removeOld")
    updated = False
    if layoutName and oldID and newID:
        from Embed import Embed
        embedDao = Embed(db)
        updated = embedDao.edit_ingredient_mapping(layoutName, oldID, newID)
        if updated and removeOld:
            query = db.ingredients.id == oldID
            db(query).delete()
    if updated:
        return api_response(update="success")
    else:
        return api_error('Input01', "I'm not angry, just disappointed")

@auth.requires_login()
def library():
    type = request.vars.type or 'image'
    sourceMediaType = request.vars.source_type or None

    if request.post_vars.query == '':
        query = ''
    else:
        query = request.post_vars.query or request.get_vars.query or ''

    if query != session.priorQuery:
        index = 0
    else:
        index = request.post_vars.index or request.get_vars.index or 0

    session.priorQuery = query

    count = request.post_vars.count or request.get_vars.count or 20
    total = None

    if index:
        index = int(index)
    if count:
        count = int(count)

    # Initialize output variables
    subtitle = ''
    total = ''
    media = []

    if type == 'image':
        # Retrieve images
        heading = 'Images'
        from Images import Images
        imageObj = Images(db)
        # images = imageObj.search_images_by_owner(session.organization, query, index, count)
        images = imageObj.search_images_by_owner(1, query, index, count)
        total = images['count']
        media = images['images']
    elif type == 'video_embedded':
        # Retrieve videos
        heading = 'Videos'
        from VideoEmbedded import VideoEmbedded
        videoObj = VideoEmbedded(db)
        # videos = videoObj.search_videos_by_owner(session.organization, query, index, count)
        videos = videoObj.search_videos_by_owner(1, query, index, count)
        total = videos['count']
        media = videos['videos']
    elif type == 'audio':
        # Retrieve audio clips - not implemented yet
        heading = 'Audio'
        media = []
    elif type == 'url':
        # Retrieve all URLs
        heading = 'URLs'
        from Url import Url
        urlObj = Url(db)
        # urls = urlObj.search_urls_by_owner(session.organization, query, index, count)
        urls = urlObj.search_urls_by_owner(1, query, index, count)
        total = urls['count']
        media = urls['urls']

    if count > total:
        count = total

    return api_response(title='Media Library',
        heading=heading,
        type=type,
        media=media,
        query=query,
        index=index,
        count=count,
        total=total)

def api_response(**kwargs):

    success_response = {
        'version': apiVersion,
        'success': True,
        'data': dict(**kwargs)
    }

    return success_response


def api_error(message=''):

    error_response = {
        'version': apiVersion,
        'success': False,
        'info': message
    }
    # WE WILL ADD ERROR LOGGING HERE SOMETIME

    return error_response
