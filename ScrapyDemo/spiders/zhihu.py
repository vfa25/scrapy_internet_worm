# -*- coding: utf-8 -*-
import time
import re
import pickle
import datetime
import json
from urllib import parse

import scrapy
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


from ScrapyDemo.settings import ZHIHU_PASSWORD
from ScrapyDemo.items import ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    browser = None

    # question的第一页answer的请求url
    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default'

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def start_requests(self):
        from selenium.webdriver.chrome.options import Options
        options = Options()

        options.add_argument("--disable-extensions")
        # options.add_argument('window-size=1280x800')
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        self.browser = webdriver.Chrome(
            executable_path='./chromedriver',
            chrome_options=options
        )

        try:
            self.browser.maximize_window()
        except:
            pass

        try:
            cookies = pickle.load(
                open('./cookies/zhihu.cookie', 'rb'))
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
        except:
            cookie_dict = None

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict, callback=self.judge_login)]

    def judge_login(self, response):

        self.browser.get('https://www.zhihu.com/signin')

        if self.__is_login():
            return [scrapy.Request(url=self.start_urls[0], dont_filter=True)]

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
                english_captcha_element = self.browser.find_element_by_class_name(
                    'Captcha-englishImg')
            except:
                english_captcha_element = None

            try:
                chinese_captcha_element = self.browser.find_element_by_class_name(
                    'Captcha-chineseImg')
            except:
                chinese_captcha_element = None

            if chinese_captcha_element:
                if action._actions:
                    action._actions = []
                    self.browser.execute_script(
                        'document.querySelectorAll(".Button.ChineseCaptchaPoint").forEach(function(el){el.click()});')
                # chinese_captcha_point = self.browser.find_element_by_class_name('')
                # ele_position = chinese_captcha_element.location
                # x_relative = ele_position['x']
                # y_relative = ele_position['y']
                # self.browser_navigation_panel_height = self.browser.execute_script(
                #     'return window.outerHeight - window.innerHeight'
                # )
                base64_text = chinese_captcha_element.get_attribute('src')
                import base64
                code = base64_text.replace(
                    'data:image/jpg;base64,', '').replace('%0A', '')
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
                        last_position.append(
                            [positions[1][1], positions[1][0]])
                        last_position.append(
                            [positions[0][1], positions[0][0]])
                    else:
                        last_position.append(
                            [positions[0][1], positions[0][0]])
                        last_position.append(
                            [positions[1][1], positions[1][0]])

                    first_position = [
                        int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
                    second_position = [
                        int(last_position[1][0] / 2), int(last_position[1][1] / 2)]
                    action.move_to_element_with_offset(
                        chinese_captcha_element, first_position[0], first_position[1]).click()
                    action.move_to_element_with_offset(
                        chinese_captcha_element, second_position[0], second_position[1]).click().perform()
                else:
                    last_position.append([positions[0][1], positions[0][0]])

                    first_position = [
                        int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
                    action.move_to_element_with_offset(
                        chinese_captcha_element, first_position[0], first_position[1]).click().perform()
                print(last_position)
                self.__inputLoginInfo()
                time.sleep(3)

            if english_captcha_element:
                base64_text = english_captcha_element.get_attribute('src')
                import base64
                code = base64_text.replace(
                    'data:image/jpg;base64,', '').replace('%0A', '')
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

                self.__clear_input(
                    '.Captcha.SignFlow-captchaContainer input[name="captcha"]')
                self.browser.find_element_by_css_selector(
                    '.Captcha.SignFlow-captchaContainer input[name="captcha"]').send_keys(rsp.pred_rsp.value)
                self.__inputLoginInfo()
                time.sleep(3)

        cookies = self.browser.get_cookies()
        pickle.dump(cookies, open(
            './cookies/zhihu.cookie', 'wb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

    def parse(self, response):
        '''
        1. 提取出html页面中的所有url，并跟踪这些url进一步爬取
        2. 如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        '''
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith(
            'https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match('(.*zhihu.com/question/(\d+))(/|$).*', url)
            if match_obj:
                # 如果提取到question相关的页面，则下载后交由提取函数进行提取
                response_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(
                    response_url,
                    headers=self.headers,
                    callback=self.parse_question,
                    meta={
                        'question_id': question_id
                    })
            else:
                # 如果不是question页面，则进一步跟踪
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)
                pass

    def parse_question(self, response):
        '''
        处理question页面，从页面中提取出具体的question item
        '''

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css('title', '.QuestionHeader-title::text')
        item_loader.add_css('content', '.QuestionHeader-detail')
        item_loader.add_value('url', response.url)
        question_id = response.meta.get('question_id', '')
        item_loader.add_value('zhihu_id', int(question_id))
        item_loader.add_css('answer_num', '.List-headerText ::text')
        item_loader.add_css(
            'comments_num', '.QuestionHeader-Comment button::text')
        item_loader.add_css(
            'watch_user_num', '.QuestionFollowStatus-counts .NumberBoard-itemValue::text')
        item_loader.add_css(
            'topics', '.QuestionHeader-topics .TopicLink .Popover div::text')

        question_item = item_loader.load_item()

        yield question_item
        # yield scrapy.Request(
        #     self.start_answer_url.format(question_id, 20, 0),
        #     headers=self.headers,
        #     callback=self.parse_answer)

    def parse_answer(self, response):
        '''
        处理question的answer
        '''
        ans_json = json.loads(response.text)

        # 提取answer的具体字段
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else answer['excerpt']
            answer_item['parise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()

            yield answer_item

        is_end = ans_json['paging']['is_end']
        next_url = ans_json['paging']['next']
        if not is_end:
            yield scrapy.Request(
                next_url,
                headers=self.headers,
                callback=self.parse_answer)

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
            user_avatar = self.browser.find_element_by_css_selector(
                '.Avatar.AppHeader-profileAvatar')
        except:
            user_avatar = None
        return user_avatar
