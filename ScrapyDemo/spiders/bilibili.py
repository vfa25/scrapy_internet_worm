# -*- coding: utf-8 -*-
import time
import re
import pickle
import base64
import datetime
import json
from urllib import parse
from PIL import Image
from io import BytesIO
from random import randint

import scrapy
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


from ScrapyDemo.settings import bili_username, bili_password

class BiliLoginSpider(scrapy.Spider):
    name = 'bilibili'
    allowed_domains = ['passport.bilibili.com']
    start_urls = ['https://passport.bilibili.com/login']
    browser = None

    headers = {
        "HOST": "passport.bilibili.co",
        "Referer": "https://passport.bilibili.co",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def start_requests(self):
        from selenium.webdriver.chrome.options import Options
        options = Options()

        # options.add_argument("--disable-extensions")
        # # options.add_argument('window-size=1280x800')
        # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        self.browser = webdriver.Chrome(
            executable_path='./chromedriver',
            chrome_options=options
        )
        self.login()

    def get_image(self, base64_str, image_file_name):
        # 获取验证码图片
        # time.sleep(2)
        img_base64 = base64_str.split(',')[1]
        img_bytes = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_bytes))
        img.save(image_file_name)
        return img

    def login(self):
        action = ActionChains(self.browser)
        try:
            self.browser.maximize_window()
        except Exception as e:
            pass


        while not self.is_login():

            self.browser.get('https://passport.bilibili.com/login')

            username_ele = self.browser.find_element_by_css_selector('#login-username')
            password_ele = self.browser.find_element_by_css_selector('#login-passwd')
            username_ele.send_keys(bili_username)
            password_ele.send_keys(bili_password)

            # 1. 点击登录调出滑动验证码
            login_ele = self.browser.find_element_by_css_selector('.btn.btn-login')
            login_ele.click()

            time.sleep(5)


            img_info1 = self.browser.execute_script('return document.querySelector(".geetest_canvas_fullbg.geetest_fade.geetest_absolute").toDataURL("image/png");')
            # 截取验证码
            image1 = self.get_image(img_info1, 'chatcha1.png')
            img_info2 = self.browser.execute_script('return document.querySelector(".geetest_canvas_bg.geetest_absolute").toDataURL("image/png");')
            # 截取验证码
            image2 = self.get_image(img_info2, 'chatcha2.png')
            # img_info3 = self.browser.execute_script('return document.querySelector(".geetest_canvas_slice.geetest_absolute").toDataURL("image/png");')
            # # 截取验证码
            # image3 = self.get_image(img_info3, 'chatcha3.png')

            # 获取拖动距离
            drag_distance = self.img_contrast(image1, image2)

            # 随机拖动曲线
            drag_track = self.drag_operation(drag_distance)

            slider = self.browser.find_element_by_css_selector('.geetest_slider_button')
            ActionChains(self.browser).click_and_hold(slider).perform()
            for x in drag_track:
                ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).release().perform()
            time.sleep(5)
            pass
        pass

    def is_login(self):
        try:
            self.browser.find_element_by_xpath('//span[contains(text(), "动态")]')
            return True
        except:
            return False


    def compare_pixel(self, image1, image2, i, j):
        # 判断两个像素是否相同，RGB
        pixel1 = image1.load()[i, j]
        pixel2 = image2.load()[i, j]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(pixel1[2] - pixel2[2]) < threshold:
            return True
        return False

    def img_contrast(self, image1, image2):
        left = 60
        has_find = False
        for i in range(left, image1.size[0]):
            if has_find:
                break
            for j in range(image1.size[1]):
                if not self.compare_pixel(image1, image2, i, j):
                    left = i
                    has_find = True
                    break

        left -= 6
        return left

    def drag_operation(self, distance):
        '''
        开始加速，然后减速，生长曲线，且加入随机变动
        '''
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 3 / 4
        # 间隔时间
        t = 0.1
        v = 0
        while current < distance:
            if current < mid:
                a = randint(2, 3)
            else:
                a = - randint(6, 7)
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            track.append(round(move))

        return track
