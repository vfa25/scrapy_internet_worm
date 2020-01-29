# -*- coding: utf-8 -*-

from random import Random
import scrapy
from urllib import parse as urlparse
from scrapy.http import Request
from ScrapyDemo.items import (
    AntdAsideNavItem, AntdComponentDetailItem, CustomItemLoader)


random_ins = Random()


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
                secondary_name = secondary_node.css(
                    'a>span:first-child::text').extract_first('')
                secondary_title = secondary_node.css(
                    'span.chinese::text').extract_first('')
                yield Request(
                    url=urlparse.urljoin(response.url, secondary_key),
                    meta={
                        'primary_title': primary_title,
                        'secondary_title': secondary_title,
                        'secondary_name': secondary_name,
                        'secondary_key': secondary_key
                    },
                    callback=self.parse_block
                )

    def parse_block(self, response):
        primary_title = response.meta.get('primary_title', '')
        secondary_title = response.meta.get('secondary_title', '')
        secondary_name = response.meta.get('secondary_name', '')
        secondary_key = response.meta.get('secondary_key', '')

        post_nodes = response.css('#demo-toc>li')

        for post_node in post_nodes:
            # aside_nav_item = AntdAsideNavItem()
            # item_loader = CustomItemLoader(
            #     item=aside_nav_item,
            #     selector=post_node
            # )
            # item_loader.add_value('primary_title', primary_title)
            # item_loader.add_value('secondary_title', secondary_title)
            # item_loader.add_value('secondary_name', secondary_name)
            # item_loader.add_value('secondary_key', secondary_key)
            # aside_nav_item = item_loader.load_item()
            # yield aside_nav_item

            detail_id = post_node.css('a::attr(href)').extract_first('')
            name = post_node.css('a::text').extract_first('')
            if not detail_id:
                return
            css_str = detail_id + '>.code-box-meta>.code-box-description'
            detail_block = response.css(css_str)

            component_detail_item = AntdComponentDetailItem()
            component_loader = CustomItemLoader(
                item=component_detail_item,
                selector=post_node
            )
            component_loader.add_value('name', name)
            component_loader.add_value(
                'easy_to_use', random_ins.randint(1, 99))
            component_loader.add_value('key', detail_id.replace('#', '', 1))
            component_loader.add_value('category_name', secondary_name)
            least_title = detail_block.css(' div *::text').extract()
            component_loader.add_value(
                'desc', ''.join([str(i) for i in least_title]))
            component_detail_item = component_loader.load_item()
            yield component_detail_item
