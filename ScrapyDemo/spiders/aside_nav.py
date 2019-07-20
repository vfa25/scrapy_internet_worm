# -*- coding: utf-8 -*-
import scrapy


class AsideNavSpider(scrapy.Spider):
    name = 'aside_nav'
    allowed_domains = ['https://ant.design/docs/react/introduce-cn']
    start_urls = ['http://https://ant.design/docs/react/introduce-cn/']

    def parse(self, response):
        pass
