import re



def get_nums(value):
    match_re = re.match('.*?(\d+).*', value, re.S)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums