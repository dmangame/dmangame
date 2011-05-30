import time
import datetime
from google.appengine.ext import webapp
register = webapp.template.create_template_register()

@register.filter
def hash(h,key):
    return h[key]

@register.filter
def datetime_to_seconds(value):
    dt = value
    seconds = time.mktime(dt.timetuple())
    return seconds

@register.filter
def truncate(value, arg):
    """
    Truncates a string after a given number of chars
    Argument: Number of chars to truncate after
    """
    try:
        length = int(arg)
    except ValueError: # invalid literal for int()
        return value # Fail silently.
    if not isinstance(value, basestring):
        value = str(value)
    if (len(value) > length):
        return value[:length]
    else:
        return value

