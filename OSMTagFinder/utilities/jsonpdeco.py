# -*- coding: utf-8 -*-
'''
Created on 29.11.2014

@author: aisipos, see https://gist.github.com/aisipos/1094140 for this decorator
'''

from functools import wraps
from flask import request, current_app

def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            reqData = str((f(*args, **kwargs).get_data()))
            content = str(callback) + '(' + reqData + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return f(*args, **kwargs)
    return decorated_function
