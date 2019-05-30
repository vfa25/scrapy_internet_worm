# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from .utils.common import get_nums


class GithubtrendingItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    tag = scrapy.Field()
    date_type = scrapy.Field()
    title_homepage = scrapy.Field()
    title_detail = scrapy.Field(
        input_processor = MapCompose(lambda x: x.strip())
    )
    describe = scrapy.Field(
        input_processor = MapCompose(lambda x: x.strip())
    )
    programming_language = scrapy.Field()
    star = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    fork = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    build_by = scrapy.Field()
    octicon_star = scrapy.Field(
        input_processor = MapCompose(lambda x: x.strip())
    )


class TrendingItemLoader(ItemLoader):
    # 自定义item_loader
    default_output_processor = TakeFirst()
