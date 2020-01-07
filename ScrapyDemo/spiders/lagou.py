# -*- coding: utf-8 -*-
import os

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import pickle

from ScrapyDemo.settings import LAGOU_USERNAME, LAGOU_PASSWORD


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    rules = (
        Rule(LinkExtractor(allow=('zhaopin/.*')), follow=True),
        Rule(LinkExtractor(allow=('gongsi/j\d+\.html')), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+\.html'),
             callback='parse_job', follow=True),
    )

    # def parse_start_url(self, response):
    #     return []

    # def process_results(self, response, results):
    #     return results

    def start_requests(self):
        '''
        override该入口方法，以selenium模拟登录后拿到cookie交给scrapy的request使用
        '''
        # 从文件中读取cookie

        cookies = None
        try:
            if os.path.exists('./cookies/lagou.cookie'):
                cookies = pickle.load(
                    open('./cookies/lagou.cookie', 'rb'))
        except:
            pass

        if not cookies:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            options = Options()

            options.add_argument("--disable-extensions")
            # options.add_argument('window-size=1280x800')
            # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

            browser = webdriver.Chrome(
                executable_path='./chromedriver',
                chrome_options=options
            )

            from selenium.webdriver.common.action_chains import ActionChains
            action = ActionChains(browser)
            browser.get('https://passport.lagou.com/login/login.html')
            browser.find_element_by_css_selector(
                'div[data-view="passwordLogin"] div[data-propertyname="username"] .input.input_white').send_keys(LAGOU_USERNAME)
            browser.find_element_by_css_selector(
                'div[data-view="passwordLogin"] div[data-propertyname="password"] .input.input_white').send_keys(LAGOU_PASSWORD)
            browser.find_element_by_css_selector(
                'div[data-view="passwordLogin"] .sense_login_password input[type="submit"]').click()
            import time
            time.sleep(3)

            is_login = False
            while not is_login:
                try:
                    if browser.find_element_by_css_selector('.unick'):
                        is_login = True
                except:
                    pass

                try:
                    captcha_element = browser.find_element_by_css_selector(
                        '.geetest_window>.geetest_item:first-child>.geetest_item_wrap>img')
                except:
                    captcha_element = None

                if captcha_element:
                    if action._actions:
                        action._actions = []

                    img_url = captcha_element.get_attribute('src')
                    import ssl
                    ssl._create_default_https_context = ssl._create_unverified_context
                    import urllib
                    urllib.request.urlretrieve(
                        img_url, filename='lagou_validate.jpeg')
                    # import requests
                    # html = requests.get(img_url)
                    # fh = open('lagou_validate.jpeg', 'wb')
                    # fh.write(html.content)
                    # fh.close()

                    from tools.chaojiying import Chaojiying_Client
                    from settings import (chaojiying_username,
                                          chaojiying_password, chaojiying_app_id)
                    chaojiying = Chaojiying_Client(
                        chaojiying_username, chaojiying_password, chaojiying_app_id)
                    im = open('lagou_validate.jpeg', 'rb').read()
                    pos_obj = chaojiying.PostPic(im, 9004)
                    if pos_obj['err_no'] == 0 or pos_obj['err_str'] == 'OK':
                        pic_str = pos_obj['pic_str']
                        positions = pic_str.split('|')
                        from ScrapyDemo.utils.common import get_coordinate
                        for item in positions:
                            point = item.split(',')
                            el_index = get_coordinate(point)
                            browser.find_element_by_css_selector(
                                '.geetest_window>.geetest_item:nth-child({})'.format(el_index)).click()

                        browser.find_element_by_css_selector(
                            '.geetest_commit').click()
                        time.sleep(3)

            cookies = browser.get_cookies()
            # 写入cookie到文件中
            pickle.dump(cookies, open(
                './cookies/lagou.cookie', 'wb'))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

        pass

    def parse_job(self, response):
        '''
        解析拉勾网的职位
        '''
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item
