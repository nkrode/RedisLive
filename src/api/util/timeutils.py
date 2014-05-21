from datetime import datetime

def convert_to_epoch(timestamp):
	diff = (timestamp - datetime(1970, 1, 1))
	seconds = int(total_seconds(diff))
	return seconds


# Original fix for Py2.6: https://github.com/mozilla/mozdownload/issues/73
def total_seconds(dt):
	# Keep backward compatibility with Python 2.6 which doesn't have
	# this method
	if hasattr(datetime, 'total_seconds'):
		return dt.total_seconds()
	else:
		return (dt.microseconds + (dt.seconds + dt.days * 24 * 3600) * 10**6) / 10**6
