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

    def parse(self, response):
        pass

    def start_requests(self):
        from selenium.webdriver.chrome.options import Options
        options = Options()

        options.add_argument("--disable-extensions")
        # options.add_argument('window-size=1280x800')
        # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        browser = webdriver.Chrome(
            executable_path='/Users/a/Documents/pythonCode/ScrapyDemo/chromedriver',
            chrome_options=options
        )

        try:
            browser.maximize_window()
        except:
            pass

        browser.get('https://www.zhihu.com/signin')

        action = ActionChains(browser)
        browser.find_element_by_css_selector(
            '.SignFlow-tabs .SignFlow-tab:nth-child(2)').click()

        self.__inputLoginInfo(browser, password=ZHIHU_PASSWORD + '1')

        time.sleep(3)
        login_success = False
        while not login_success:
            try:
                notify_ele = browser.find_element_by_class_name('Popover PushNotifications AppHeader-notifications')
                login_success = True
            except:
                pass

            try:
                english_captcha_element = browser.find_element_by_class_name('Captcha-englishImg')
            except:
                english_captcha_element = None

            try:
                chinese_captcha_element = browser.find_element_by_class_name('Captcha-chineseImg')
            except:
                chinese_captcha_element = None

            if chinese_captcha_element:
                # ele_position = chinese_captcha_element.location
                # x_relative = ele_position['x']
                # y_relative = ele_position['y']
                # browser_navigation_panel_height = browser.execute_script(
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
                self.__inputLoginInfo(browser)

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

                self.__clear_input(browser, '.Captcha.SignFlow-captchaContainer input[name="captcha"]')
                browser.find_element_by_css_selector(
                    '.Captcha.SignFlow-captchaContainer input[name="captcha"]').send_keys(rsp.pred_rsp.value)
                self.__inputLoginInfo(browser)
                pass

    def __inputLoginInfo(self, browser, name='17601226104', password=ZHIHU_PASSWORD):
        self.__clear_input(browser, '.SignFlow-accountInput.Input-wrapper input')
        browser.find_element_by_css_selector(
            '.SignFlow-accountInput.Input-wrapper input').send_keys(name)

        self.__clear_input(browser, '.SignFlow-password input')
        browser.find_element_by_css_selector(
            '.SignFlow-password input').send_keys(password)
        browser.find_element_by_css_selector(
            '.Button.SignFlow-submitButton').click()

    def __clear_input(self, browser, css_str):
        '''
        MacOS，模拟 Keys.COMMAND 的方法
        browser.find_element_by_css_selector(css_str).send_keys(Keys.CONTROL + 'a')
        '''
        ele = browser.find_element_by_css_selector(css_str)
        value = ele.get_attribute('value')
        for i in value:
            ele.send_keys(Keys.BACK_SPACE)



    # def start_requests(self):
    #     # cookies = pickle.load(open('/Users/a/Documents/pythonCode/ScrapyDemo/cookies/zhihu.cookie', 'rb'))
    #     # cookie_dict = {}
    #     # for cookie in cookies:
    #     #     cookie_dict[cookie['name']] = cookie['value']

    #     # return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

    #     from selenium.webdriver.chrome.options import Options
    #     from selenium.webdriver.common.keys import Keys
    #     options = Options()

    #     options.add_argument("--disable-extensions")
    #     options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #     # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    #     browser = webdriver.Chrome(
    #         executable_path='/Users/a/Documents/pythonCode/ScrapyDemo/chromedriver',
    #         chrome_options=options
    #     )
    #     browser.get('https://www.zhihu.com/signin')

    #     browser.find_element_by_css_selector(
    #         '.SignFlow-tabs .SignFlow-tab:nth-child(2)').click()

    #     browser.find_element_by_css_selector(
    #         '.SignFlow-accountInput.Input-wrapper input').send_keys(Keys.CONTROL, 'a')
    #     browser.find_element_by_css_selector(
    #         '.SignFlow-accountInput.Input-wrapper input').send_keys('17601226104')
    #     browser.find_element_by_css_selector(
    #         '.SignFlow-password input').send_keys(Keys.CONTROL, 'a')
    #     print(ZHIHU_PASSWORD)
    #     browser.find_element_by_css_selector(
    #         '.SignFlow-password input').send_keys(ZHIHU_PASSWORD)

    #     browser.find_element_by_css_selector(
    #         '.Button.SignFlow-submitButton').click()

    #     browser.get('https://www.zhihu.com/')
    #     cookies = browser.get_cookies()
    #     pickle.dump(cookies, open(
    #         '/Users/a/Documents/pythonCode/ScrapyDemo/cookies/zhihu.cookie', 'wb'))
    #     cookie_dict = {}
    #     for cookie in cookies:
    #         cookie_dict[cookie['name']] = cookie['value']

    #     return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
