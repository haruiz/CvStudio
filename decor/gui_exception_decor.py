import logging
import sys
# from pprint import  pprint
import traceback
from functools import wraps

from util import GUIUtilities


def gui_exception(func):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if len(args) == 1:
                return func(*args)
            else:
                return func(*args, **kwargs)

        except Exception as ex:
            exc_type,exc_value,exc_traceback=sys.exc_info()
            GUIUtilities.show_error_message("{}".format(str(traceback.format_exception_only( exc_type, exc_value )[0])))
    return wrapper
