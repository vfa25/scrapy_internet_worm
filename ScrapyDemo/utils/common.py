import re
import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(value):
    match_re = re.match('.*?(\d+).*', value, re.S)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def get_coordinate(point):
    pos_x = point[0]
    pos_y = point[1]
    result_x = _compute_coordinate(pos_x)
    result_y = _compute_coordinate(pos_y)
    return result_x + (result_y - 1) * 3


def _compute_coordinate(value):
    value = int(value)
    if value < 115:
        result = 1
    elif value < 230:
        result = 2
    else:
        result = 3
    return result


if __name__ == '__main__':
    print(get_md5('https://baidu.com'))
