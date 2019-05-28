# -*- coding: utf-8 -*-
import scrapy


class GithubAppSpider(scrapy.Spider):
    name = 'github_app'
    allowed_domains = ['https://github.com/trending']
    start_urls = ['http://https://github.com/trending/']

    def parse(self, response):
        pass
