import logging
import sys
# from pprint import  pprint
import traceback
from functools import wraps

from util import GUIUtilities


def work_exception(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """
    @wraps( function )
    def wrapper(*args, **kwargs):
        try:
            if args or kwargs:
                return function(*args, **kwargs)
            else:
                return function()
        except Exception as ex:
            return None, ex

    return wrapper
