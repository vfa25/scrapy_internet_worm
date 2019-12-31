# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
import time
import pickle
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


from ScrapyDemo.settings import ZHIHU_PASSWORD


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    browser = None

    def parse(self, response):
        '''
        1. 提取出html页面中的所有url，并跟踪这些url进一步爬取
        2. 如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        '''
        pass

    def start_requests(self):
        from selenium.webdriver.chrome.options import Options
        options = Options()

        options.add_argument("--disable-extensions")
        # options.add_argument('window-size=1280x800')
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        self.browser = webdriver.Chrome(
            executable_path='/Users/a/Documents/pythonCode/ScrapyDemo/chromedriver',
            chrome_options=options
        )

        try:
            self.browser.maximize_window()
        except:
            pass

        cookies = pickle.load(open('/Users/a/Documents/pythonCode/ScrapyDemo/cookies/zhihu.cookie', 'rb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict, callback=self.judge_login)]

    def judge_login(self, response):

        self.browser.get('https://www.zhihu.com/signin')

        if self.__is_login():
            return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=response.request.cookies)]

        action = ActionChains(self.browser)
        self.browser.find_element_by_css_selector(
            '.SignFlow-tabs .SignFlow-tab:nth-child(2)').click()

        self.__inputLoginInfo(password=ZHIHU_PASSWORD + '1')

        time.sleep(3)
        login_success = False
        while not login_success:
            try:
                if self.__is_login():
                    login_success = True
            except:
                pass

            try:
                english_captcha_element = self.browser.find_element_by_class_name('Captcha-englishImg')
            except:
                english_captcha_element = None

            try:
                chinese_captcha_element = self.browser.find_element_by_class_name('Captcha-chineseImg')
            except:
                chinese_captcha_element = None

            if chinese_captcha_element:
                self.browser.execute_script('document.querySelectorAll(".Button.ChineseCaptchaPoint.Button--plain").forEach(function(el){el.click()});')
                # chinese_captcha_point = self.browser.find_element_by_class_name('')
                # ele_position = chinese_captcha_element.location
                # x_relative = ele_position['x']
                # y_relative = ele_position['y']
                # self.browser_navigation_panel_height = self.browser.execute_script(
                #     'return window.outerHeight - window.innerHeight'
                # )
                base64_text = chinese_captcha_element.get_attribute('src')
                import base64
                code = base64_text.replace('data:image/jpg;base64,', '').replace('%0A', '')
                fh = open('yzm_cn.jpeg', 'wb')
                fh.write(base64.b64decode(code))
                fh.close()

                from zheye import zheye
                z = zheye()
                positions = z.Recognize('yzm_cn.jpeg')
                last_position = []

                # 格式化倒立文字的坐标（zheye默认坐标返回为y,x的格式）
                if len(positions) == 2:
                    if positions[0][1] > positions[1][1]:
                        last_position.append([positions[1][1], positions[1][0]])
                        last_position.append([positions[0][1], positions[0][0]])
                    else:
                        last_position.append([positions[0][1], positions[0][0]])
                        last_position.append([positions[1][1], positions[1][0]])

                    first_position = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
                    second_position = [int(last_position[1][0] / 2), int(last_position[1][1] / 2)]
                    action.move_to_element_with_offset(chinese_captcha_element, first_position[0], first_position[1]).click()
                    action.move_to_element_with_offset(chinese_captcha_element, second_position[0], second_position[1]).click().perform()
                else:
                    last_position.append([positions[0][1], positions[0][0]])

                    first_position = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
                    action.move_to_element_with_offset(chinese_captcha_element, first_position[0], first_position[1]).click().perform()
                print(last_position)
                self.__inputLoginInfo()

            if english_captcha_element:
                base64_text = english_captcha_element.get_attribute('src')
                import base64
                code = base64_text.replace('data:image/jpg;base64,', '').replace('%0A', '')
                fh = open('yzm_en.jpeg', 'wb')
                fh.write(base64.b64decode(code))
                fh.close()

                from tools.fateadm_api import FateadmApi
                from ScrapyDemo.settings import (
                    ff_app_id, ff_app_key, ff_pd_id, ff_pd_key)

                api = FateadmApi(ff_app_id, ff_app_key, ff_pd_id, ff_pd_key)

                pred_type = "30400"
                # 返回详细识别结果
                rsp = api.PredictFromFile(pred_type, 'yzm_en.jpeg')

                while True:
                    if not rsp or rsp.ret_code != 0 or not rsp.pred_rsp or not rsp.pred_rsp.value:
                        rsp = api.PredictFromFile(pred_type, 'yzm_en.jpeg')
                    else:
                        break

                self.__clear_input('.Captcha.SignFlow-captchaContainer input[name="captcha"]')
                self.browser.find_element_by_css_selector(
                    '.Captcha.SignFlow-captchaContainer input[name="captcha"]').send_keys(rsp.pred_rsp.value)
                self.__inputLoginInfo()
                pass

        # self.browser.get('https://www.zhihu.com/')
        cookies = self.browser.get_cookies()
        pickle.dump(cookies, open(
            '/Users/a/Documents/pythonCode/ScrapyDemo/cookies/zhihu.cookie', 'wb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

    def __inputLoginInfo(self, name='17601226104', password=ZHIHU_PASSWORD):
        self.__clear_input('.SignFlow-accountInput.Input-wrapper input')
        self.browser.find_element_by_css_selector(
            '.SignFlow-accountInput.Input-wrapper input').send_keys(name)

        self.__clear_input('.SignFlow-password input')
        self.browser.find_element_by_css_selector(
            '.SignFlow-password input').send_keys(password)
        self.browser.find_element_by_css_selector(
            '.Button.SignFlow-submitButton').click()

    def __clear_input(self, css_str):
        '''
        MacOS，模拟 Keys.COMMAND 的方法
        self.browser.find_element_by_css_selector(css_str).send_keys(Keys.CONTROL + 'a')
        '''
        ele = self.browser.find_element_by_css_selector(css_str)
        value = ele.get_attribute('value')
        for i in value:
            ele.send_keys(Keys.BACK_SPACE)

    def __is_login(self):
        try:
            user_avatar = self.browser.find_element_by_css_selector('.Avatar.AppHeader-profileAvatar')
        except:
            user_avatar = None
        return user_avatar
