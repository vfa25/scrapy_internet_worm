# -*- coding: utf-8 -*-
from urllib import parse
import json
import re

import scrapy
from scrapy import Request
import requests

from ScrapyDemo.utils.common import get_md5
from ScrapyDemo.items import (CnblogsItem)


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        '''
        1. 获取新闻列表页中的新闻url并交给scrapy下载后调用响应的解析方法
        2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse继续跟进
        '''
        post_nodes = response.css('#news_list .news_block')[:1]
        for post_node in post_nodes:
            image_url = post_node.css(
                '.entry_summary a img::attr(src)').extract_first('')
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

        # next_url = response.xpath('//a[contains(text(), "Next >")]/@href').extract_first('')
        # yield Request(url=parse.urljoin(response.url, next_url),
        #                 callback=self.parse)
        pass

    def parse_detail(self, response):
        match_re = re.match('.*?(\d+)', response.url)
        if match_re:
            post_id = match_re.group(1)

            cnblogs_item = CnblogsItem()
            title = response.css('#news_title a::text').extract_first('')
            create_date = response.css(
                '#news_info .time::text').extract_first('')
            match_re = re.match('.*?(\d+.*)', create_date)
            if match_re:
                create_date = match_re.group(1)
            content = response.css('#news_content').extract_first('')
            tag_list = response.css('.news_tags a::text').extract()
            tags = ','.join(tag_list)

            # html = requests.get(url=parse.urljoin(response.url, '/NewsAjax/GetAjaxNewsInfo?contentId={}'.format(post_id)))

            cnblogs_item['title'] = title
            cnblogs_item['create_date'] = create_date
            cnblogs_item['content'] = content
            cnblogs_item['tags'] = tags
            cnblogs_item['url'] = response.url
            cnblogs_item['front_image_url'] = response.meta.get(
                'front_image_url', '')

            yield Request(
                url=parse.urljoin(
                    response.url, '/NewsAjax/GetAjaxNewsInfo?contentId={}'.format(post_id)),
                meta={'cnblogs_item': cnblogs_item},
                callback=self.parse_nums)
        pass

    def parse_nums(self, response):
        j_data = json.loads(response.text)
        cnblogs_item = response.meta.get('cnblogs_item', '')

        praise_nums = j_data['DiggCount']
        fav_nums = j_data['TotalView']
        comment_nums = j_data['CommentCount']

        cnblogs_item['praise_nums'] = praise_nums
        cnblogs_item['fav_nums'] = fav_nums
        cnblogs_item['comment_nums'] = comment_nums

        cnblogs_item['url_object_id'] = get_md5(cnblogs_item['url'])

        yield cnblogs_item
