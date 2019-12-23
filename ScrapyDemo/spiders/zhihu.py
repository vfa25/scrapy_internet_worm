# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
import time
import pickle
# from mouse import move, click

from ScrapyDemo.settings import ZHIHU_PASSWORD


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    def parse(self, response):
        pass

    def start_requests(self):
        # cookies = pickle.load(open('/Users/a/Documents/pythonCode/ScrapyDemo/cookies/zhihu.cookie', 'rb'))
        # cookie_dict = {}
        # for cookie in cookies:
        #     cookie_dict[cookie['name']] = cookie['value']

        # return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.keys import Keys
        options = Options()

        options.add_argument("--disable-extensions")
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        browser = webdriver.Chrome(
            executable_path='/Users/a/Documents/pythonCode/ScrapyDemo/chromedriver',
            chrome_options=options
        )
        browser.get('https://www.zhihu.com/signin')

        browser.find_element_by_css_selector(
            '.SignFlow-tabs .SignFlow-tab:nth-child(2)').click()

        browser.find_element_by_css_selector(
            '.SignFlow-accountInput.Input-wrapper input').send_keys(Keys.CONTROL + 'a')
        browser.find_element_by_css_selector(
            '.SignFlow-accountInput.Input-wrapper input').send_keys('17601226104')
        browser.find_element_by_css_selector(
            '.SignFlow-password input').send_keys(Keys.CONTROL + 'a')
        print(ZHIHU_PASSWORD)
        browser.find_element_by_css_selector(
            '.SignFlow-password input').send_keys(ZHIHU_PASSWORD)
        browser.find_element_by_css_selector(
            '.Button.SignFlow-submitButton').click()

        browser.get('https://www.zhihu.com/')
        cookies = browser.get_cookies()
        pickle.dump(cookies, open(
            '/Users/a/Documents/pythonCode/ScrapyDemo/cookies/zhihu.cookie', 'wb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
