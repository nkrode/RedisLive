import datetime
# Original fix for Py2.6: https://github.com/mozilla/mozdownload/issues/73
def total_seconds(td):
    # Keep backward compatibility with Python 2.6 which doesn't have
    # this method
    if hasattr(td, 'total_seconds'):
        return td.total_seconds()
    else:
        return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def convert_to_epoch(timestamp):
        if (type(timestamp) is datetime.date):
            timestamp = datetime.datetime.fromordinal(timestamp.toordinal())
        timestamp = timestamp.replace(tzinfo=None)
	diff = (timestamp - datetime.datetime(1970, 1, 1))
	seconds = int(total_seconds(diff))
	return seconds
