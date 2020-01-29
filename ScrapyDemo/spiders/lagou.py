# -*- coding: utf-8 -*-
import os
import datetime

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import pickle

from ScrapyDemo.items import CustomItemLoader, LagouJobItem
from ScrapyDemo.settings import LAGOU_USERNAME, LAGOU_PASSWORD
from ScrapyDemo.utils.common import get_md5


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
                        time.sleep(5)

            cookies = browser.get_cookies()
            # 写入cookie到文件中
            pickle.dump(cookies, open(
                './cookies/lagou.cookie', 'wb'))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def parse_job(self, response):
        '''
        解析拉勾网的职位
        '''
        item_loader = CustomItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css('title', '.job-name::attr(title)')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('salary', '.job_request .salary::text')
        item_loader.add_xpath(
            'job_city', '//*[@class="job_request"]/h3/span[2]/text()')
        item_loader.add_xpath(
            'work_years', '//*[@class="job_request"]/h3/span[3]/text()')
        item_loader.add_xpath(
            'degree_need', '//*[@class="job_request"]/h3/span[4]/text()')
        item_loader.add_xpath(
            'job_type', '//*[@class="job_request"]/h3/span[5]/text()')
        item_loader.add_css('tags', '.position-label li::text')
        item_loader.add_css('publish_time', '.publish_time::text')
        item_loader.add_css('job_advantage', '.job-advantage p::text')
        item_loader.add_css('job_desc', '.job_bt div')
        item_loader.add_css('job_addr', '.work_addr')
        item_loader.add_css('company_name', '#job_company dt a img::attr(alt)')
        item_loader.add_css('company_url', '#job_company dt a::attr(href)')
        item_loader.add_value('crawl_time', datetime.datetime.now())

        job_item = item_loader.load_item()
        return job_item
