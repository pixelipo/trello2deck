from random import randint
from datetime import datetime


def randomColor():
    r = lambda: randint(0,255)
    return ('%02X%02X%02X' % (r(),r(),r()))


def timeToEpoch(input_time):
    if input_time is None:
        return None

    # Convert time to since-epoch
    utc_time = datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return int((utc_time - datetime(1970, 1, 1)).total_seconds())
