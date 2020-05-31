
import requests
from scrapy.selector import Selector
import MySQLdb

import sys
import os
import re

abs_dir = os.path.abspath('.')
if abs_dir not in sys.path:
    sys.path.append(abs_dir)

from ScrapyDemo.utils.common import get_md5  # noqa: E402
from ScrapyDemo.myconfig import (
    MYSQL_HOST, MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT)  # noqa: E402,E501

MYSQL_CONF = {'host': MYSQL_HOST, 'user': MYSQL_USER, 'passwd': MYSQL_PASSWORD,
              'port': MYSQL_PORT, 'db': MYSQL_DBNAME, 'charset': 'utf8'}
con = MySQLdb.connect(**MYSQL_CONF)
cursor = con.cursor()

td_reg = re.compile('\<\/?td\>', re.I)


def crawl_ips():
    # 爬取西刺的免费ip代理
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }
    for i in range(2):
        # 高匿代理
        re = requests.get(
            'https://www.xicidaili.com/nn/{0}'.format(i), headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css('#ip_list tr')

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css('.bar::attr(title)').extract()[0]
            if speed_str:
                speed = float(speed_str.split('秒')[0])
            all_texts = tr.css('td').extract()

            ip = td_reg.sub('', all_texts[1])
            port = td_reg.sub('', all_texts[2])
            proxy_type = td_reg.sub('', all_texts[5])
            id = get_md5('{}:{}'.format(ip, port))

            ip_list.append((id, ip, port, proxy_type, speed))

        print(ip_list)
        for ip_info in ip_list:
            cursor.execute(
                '''
                insert proxy_ip(id, ip, port, proxy_type, speed) VALUES ('{0}', '{1}', '{2}', '{3}', {4})
                ON DUPLICATE KEY UPDATE ip=VALUES(ip),
                port=VALUES(port),
                proxy_type=VALUES(proxy_type),
                speed=VALUES(speed)
                '''.format(
                    ip_info[0], ip_info[1], ip_info[2], ip_info[3], ip_info[4]
                )
            )
            con.commit()


class GetIP(object):
    def delete_ip(self, id):
        # 从数据库中删除无效的ip
        delete_sql = '''
        delete from proxy_ip where id='{0}'
        '''.format(id)
        cursor.execute(delete_sql)
        con.commit()

    def judge_ip(self, ip, port, proxy_type, id):
        # 判断ip是否可用
        http_url = 'http://www.baidu.com'
        # proxy_url = "http://123.169.99.204:9999"
        proxy_url = '{0}://{1}:{2}'.format(proxy_type, ip, port)
        try:
            proxy_dict = {
                'http': proxy_url
            }
            response = requests.get(http_url, proxies=proxy_dict)
            pass
        except Exception as e:
            print('invalid ip and port')
            self.delete_ip(id)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print('effective ip')
                return True
            else:
                print('invalid ip and port')
                self.delete_ip(id)
                return False

    def get_random_ip(self):
        # 从数据库中随机获取一个可用IP
        random_sql = '''
        SELECT ip, port, proxy_type, id FROM proxy_ip ORDER BY RAND() LIMIT 1
        '''
        cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            proxy_type = ip_info[2].lower() if ip_info[2] else 'http'
            id = ip_info[3]

            judge_re = self.judge_ip(ip, port, proxy_type, id)
            if judge_re:
                return '{0}://{1}:{2}'.format(proxy_type, ip, port)
            else:
                return self.get_random_ip()
        else:
            return None


if __name__ == "__main__":
    # crawl_ips()
    # pass
    get_ip = GetIP()
    get_ip.get_random_ip()
