import re
import hashlib


def get_md5(url):
    # 生成md5字符串
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(value):
    # 提取数值
    match_re = re.match('.*?(\d+).*', value, re.S)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_splash(value):
    # 去掉左斜线
    return value.replace('/', '')


def handle_break_line(value):
    # 取出 \n 的换行
    value_list = value.split('\n')
    value_list = [item.strip() for item in value_list]
    return ''.join(value_list)


def get_coordinate(point):
    # 处理拉勾网登录的点按验证码，返回在九宫格中、落点格子
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
