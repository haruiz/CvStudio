import inspect
import sys
import traceback
from functools import wraps
from cvstudio.util import GUIUtils


def gui_exception(func):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            GUIUtils.show_error_message(
                f"{str(traceback.format_exception_only( exc_type, exc_value )[0])}"
            )

    return wrapper
