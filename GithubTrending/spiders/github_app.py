# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse as urlparse
from GithubTrending.utils.common import get_md5
from GithubTrending.items import GithubtrendingItem, TrendingItemLoader


class GithubAppSpider(scrapy.Spider):
    name = 'github_app'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/trending/']

    def parse(self, response):
        # 解析时间类型
        post_nodes = response.css(
            '.select-menu-modal-right .select-menu-list a')

        for post_node in post_nodes:
            post_url = post_node.css('::attr(href)').extract_first('')
            post_text = post_node.css(
                '.select-menu-item-text::text').extract_first('')
            yield Request(
                url=urlparse.urljoin(response.url, post_url),
                meta={
                    'date_type': post_text
                },
                callback=self.parse_nav
            )

    def parse_nav(self, response):
        # 接收时间类型
        date_type = response.meta.get('date_type', '')
        # 解析导航菜单
        post_nodes = response.css('.filter-list a.filter-item')

        for post_node in post_nodes:
            post_url = post_node.css('::attr(href)').extract_first('')
            post_text = post_node.css('::text').extract_first('')
            yield Request(
                url=urlparse.urljoin(response.url, post_url),
                meta={
                    'date_type': date_type,
                    'tag': post_text
                },
                callback=self.parse_list
            )

    def parse_list(self, response):
        date_type = response.meta.get('date_type', '')
        tag = response.meta.get('tag', '')
        post_nodes = response.css('.repo-list li')

        for post_node in post_nodes:
            # spider方法必须返回可迭代对象，Request或item
            # 应在此实例化
            article_item = GithubtrendingItem()
            # 通过item_loader加载item
            item_loader = TrendingItemLoader(
                item=article_item,
                selector=post_node
            )

            # 这里好烦，github加了个换行

            item_loader.add_value('tag', tag)
            item_loader.add_value('date_type', date_type)

            post_url = post_node.css(
                '.d-inline-block h3 a::attr(href)').extract_first()
            url = urlparse.urljoin(response.url, post_url)
            item_loader.add_value('url', url)
            item_loader.add_value('url_object_id', get_md5(url))

            item_loader.add_css(
                'title_homepage', 'div.d-inline-block h3 a .text-normal::text')
            title_detail = post_node.css(
                'div.d-inline-block h3 a::text').extract()
            item_loader.add_value(
                'title_detail', title_detail and title_detail[1])
            item_loader.add_css('describe', '.py-1 p::text')
            item_loader.add_css(
                'programming_language', 'div:last-child span[itemprop="programmingLanguage"]::text')

            star = post_node.css(
                'div:last-child>a:nth-of-type(1)::text').extract()
            item_loader.add_value('star', star and star[1])
            fork = post_node.css(
                'div:last-child>a:nth-of-type(2)::text').extract()
            item_loader.add_value('fork', fork and fork[1])

            imgs = post_node.css(
                'div:last-child>span:nth-last-child(2) a img::attr(src)').extract()
            imgs_str = ",".join(imgs)
            item_loader.add_value('build_by', imgs_str)

            octicon_star = post_node.css(
                'div:last-child>span:nth-last-child(1)::text').extract()
            item_loader.add_value(
                'octicon_star', octicon_star and octicon_star[1])

            article_item = item_loader.load_item()
            yield article_item
