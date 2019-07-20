# -*- coding: utf-8 -*-
import scrapy
from urllib import parse as urlparse
from scrapy.http import Request
from ScrapyDemo.items import AntdAsideNavItem, TrendingItemLoader


class AntDesignAsideSpider(scrapy.Spider):
    name = 'ant_design_aside'
    allowed_domains = ['ant.design']
    start_urls = ['https://ant.design/docs/react/introduce-cn']

    def parse(self, response):
        post_nodes = response.css('#Components\$Menu .ant-menu-item-group')

        for post_node in post_nodes:
            primary_title = post_node.css(
                '.ant-menu-item-group-title::text').extract_first('')
            secondary_nodes = post_node.css(
                '.ant-menu-item-group-list>.ant-menu-item')
            for secondary_node in secondary_nodes:
                secondary_key = secondary_node.css(
                    'a::attr(href)').extract_first('')
                secondary_title = secondary_node.css(
                    'span.chinese::text').extract_first('')
                yield Request(
                    url=urlparse.urljoin(response.url, secondary_key),
                    meta={
                        'primary_title': primary_title,
                        'secondary_title': secondary_title,
                        'secondary_key': secondary_key
                    },
                    callback=self.parse_block
                )

    def parse_block(self, response):
        primary_title = response.meta.get('primary_title', '')
        secondary_title = response.meta.get('secondary_title', '')
        secondary_key = response.meta.get('secondary_key', '')

        post_nodes = response.css('#demo-toc>li')

        for post_node in post_nodes:
            aside_nav_item = AntdAsideNavItem()
            item_loader = TrendingItemLoader(
                item=aside_nav_item,
                selector=post_node
            )

            item_loader.add_value('primary_title', primary_title)
            item_loader.add_value('secondary_title', secondary_title)
            item_loader.add_value('secondary_key', secondary_key)
            least_title = post_node.css('a::text').extract_first('')
            item_loader.add_value('least_title', least_title)
            least_key = post_node.css('a::attr(href)').extract_first('')
            item_loader.add_value('least_key', least_key)

            aside_nav_item = item_loader.load_item()
            yield aside_nav_item
