# -*- coding: utf-8 -*-
from urllib import parse
import json
import re

import scrapy
from scrapy import Request
import requests

from ScrapyDemo.utils.common import get_md5
from ScrapyDemo.items import (CnblogsItem, CustomItemLoader)


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        '''
        1. 获取新闻列表页中的新闻url并交给scrapy下载后调用响应的解析方法
        2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse继续跟进
        '''
        post_nodes = response.css('#news_list .news_block')
        for post_node in post_nodes:
            image_url = post_node.css(
                '.entry_summary a img::attr(src)').extract_first('')
            if image_url.startswith('//'):
                image_url = 'https' + image_url
            post_url = post_node.css('h2 a::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        # next_url = response.css(
        #     'div.pager a:last-child::text').extract_first('')
        # if next_url == 'Next >':
        #     next_url = response.css(
        #         'div.pager a:last-child::attr(href)').extract_first('')
        #     yield Request(url=parse.urljoin(response.url, next_url),
        #                   callback=self.parse)

        # next_url = response.xpath(
        #     '//a[contains(text(), "Next >")]/@href').extract_first('')
        # yield Request(url=parse.urljoin(response.url, next_url),
        #               callback=self.parse)
        pass

    def parse_detail(self, response):
        match_re = re.match('.*?(\d+)', response.url)
        if match_re:
            post_id = match_re.group(1)

            item_loader = CustomItemLoader(
                item=CnblogsItem(), response=response)
            item_loader.add_css('title', '#news_title a::text')
            item_loader.add_css('content', '#news_content')
            item_loader.add_css('create_date', '#news_info .time::text')
            item_loader.add_css('tags', '.news_tags a::text')
            item_loader.add_value('url', response.url)
            if response.meta.get('front_image_url', []):
                item_loader.add_value(
                    'front_image_url', response.meta.get('front_image_url', ''))

            yield Request(
                url=parse.urljoin(
                    response.url, '/NewsAjax/GetAjaxNewsInfo?contentId={}'.format(post_id)),
                meta={'cnblogs_item_loader': item_loader, 'url': response.url},
                callback=self.parse_nums)

    def parse_nums(self, response):
        j_data = json.loads(response.text)
        item_loader = response.meta.get('cnblogs_item_loader', '')
        item_loader.add_value('praise_nums', j_data['DiggCount'])
        item_loader.add_value('fav_nums', j_data['TotalView'])
        item_loader.add_value('comment_nums', j_data['CommentCount'])
        item_loader.add_value('url_object_id', get_md5(
            response.meta.get('url', '')))

        # 若透传cnblogs_item，此处可直接为其赋值，例如 cnblogs_item['new_key']='new_value'
        cnblogs_item = item_loader.load_item()

        yield cnblogs_item
