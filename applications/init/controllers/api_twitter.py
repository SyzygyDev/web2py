# -*- coding: utf-8 -*-
apiVersion = '0.9'


import gluon.contrib.simplejson as simplejson
from Twitter import *

response.generic_patterns = ['json', 'jsonp']

def search():

    tweetReturn = []
    tweetCount = 0

    searchString = request.vars.search or None
    searchMaxId = request.vars.max_id or None
    searchCount = request.vars.count or 50

    if not searchString:
        return api_error('Twitter01')


    tso = TwitterSearchOrder()
    tso.setKeywords([searchString])
    #for multiple word search(which we dont do yet) format as such: tso.setKeywords(['#Hashtag1', '#Hashtag2'])

    if searchMaxId:
        tso.setMaxID(int(searchMaxId))

    ####count NOT fed to TMTwitter module so we can get as many as needed for photos####
    tso.setCount(100)

    ts = TwitterSearch(
            consumer_key = "df3F1LW5H5kiOUzLTxBZmy8eG",
            consumer_secret = "1dmteTOpMISVyySVA9h5dXJ83XmHAhme3LvxYUk6tTGdOMg0Fm",
            access_token = "2458306394-hUrmNS6qsjmwt42qHfiPykse7JvTutKNegLHigr",
            access_token_secret = "CbM7fWgwbe1ahMlAPkxvPinGGLRjrOFmMQYbCqtmhxKAj"
        )
    for tweet in ts.searchTweetsIterable(tso):
        duplicate = False
        if 'media' in tweet['entities']:
            result = {}
            result['user_name'] = tweet['user']['screen_name']
            result['user_id'] = tweet['user']['id']
            result['caption'] = tweet['text']
            result['type'] = 'Image'
            result['primary_tag'] = searchString
            result['profile_picture'] = tweet['user']['profile_image_url_https']
            result['imageURL'] = tweet['entities']['media'][0]['media_url_https']
            result['thumbURL'] = tweet['entities']['media'][0]['media_url_https']
            result['smImageURL'] = tweet['entities']['media'][0]['media_url_https']
            result['original_link'] = tweet['entities']['media'][0]['url']
            result['created_time'] = tweet['created_at']
            result['curation_id'] = tweet['id_str']
            result['source'] = "Twitter"
            if tweet['geo']:
                result['latitude'] = tweet['geo']['coordinates'][0]
                result['longitude'] = tweet['geo']['coordinates'][1]
            # result['rawData'] = tweet  ##### here for debugging, yields complete return

            #UGLY check for retweet duplicates, catches most of them
            if len(tweetReturn) >=1:
                for original in tweetReturn:
                    if result['imageURL'] == original['imageURL']:
                        duplicate = True

            if duplicate == False:
                tweetReturn.append(result)
                tweetCount = tweetCount + 1
                if tweetCount == int(searchCount):
                    return api_response(tweets=tweetReturn)

    if len(tweetReturn) >=1:
        return api_response(message='not enough twitter photos', tweets=tweetReturn)
    else:
        return api_response(message='no twitter photos', tweets=False)


def api_response(**kwargs) :
    resp = dict(**kwargs)

    resp.update({
        'version': apiVersion,
        'success': True,
    })

    return resp


def api_error(code, message='', info='') :

    error_response = {
        'version': apiVersion,
        'success': False,
        'error': code,
        'reason': message,
        'info': info,
    }

    return error_response