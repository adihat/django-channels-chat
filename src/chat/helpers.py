import pytz

INDIAN_TIMEZONE = 'Asia/Kolkata'
UTC_TIMEZONE = 'UTC'
DATE_TIME_FORMAT = "%I:%M %p"

def get_str_from_datetime(obj, datetime_format):
    try:
        return obj.strftime(datetime_format)
    except:
        return obj


def convert_datetime_to_different_timezone(obj, current_time_zone, to_time_zone, preserve_tz_info=False):
    obj = obj.replace(tzinfo=None)
    obj_in_current_timezone = pytz.timezone(current_time_zone).localize(obj)
    if preserve_tz_info:
        return obj_in_current_timezone.astimezone(pytz.timezone(to_time_zone))
    return obj_in_current_timezone.astimezone(pytz.timezone(to_time_zone)).replace(tzinfo=None)
