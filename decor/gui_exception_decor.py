import sys
import traceback
from functools import wraps

from util import GUIUtilities


def gui_exception(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            if args or kwargs:
                return function(*args, **kwargs)
            else:
                return function()
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            GUIUtilities.show_error_message("{}".format(str(traceback.format_exception_only(exc_type, exc_value)[0])))

    return wrapper
