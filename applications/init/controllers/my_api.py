# -*- coding: utf-8 -*-
import logging

apiVersion = '0.9'

import gluon.contrib.simplejson as simplejson

# The following line is required for .json output.
# Note: There are security implications related to generic views.
# See:
#   https://groups.google.com/forum/?fromgroups=#!topic/web2py/Jk-TIoQhRh4
#   http://comments.gmane.org/gmane.comp.python.web2py/67902
response.generic_patterns = ['json', 'jsonp']

response.headers['Cache-Control'] = "max-age=0"

def test_api():
    varString = ""
    if request.vars:
        for thisVar in request.vars:
            varString = varString + thisVar + ":" + request.vars[thisVar] + "|"
        varString = varString[:-1]

        db.callback_test.insert(test_vars=varString)


    return api_response(weGotThese=varString)


def api_response(**kwargs):
    resp = dict(**kwargs)

    resp.update({
        'version': apiVersion,
        'success': True
    })

    return resp