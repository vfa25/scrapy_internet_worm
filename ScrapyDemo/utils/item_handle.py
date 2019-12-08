import re
import time


def date_convert(value):
    match_re = re.match('.*?(\d+.*)', value)
    if match_re:
        return match_re.group(1)
    return time.time()
