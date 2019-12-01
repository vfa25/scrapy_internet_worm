# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from .utils.common import get_nums


class AntdAsideNavItem(scrapy.Item):
    primary_title = scrapy.Field()
    secondary_title = scrapy.Field()
    secondary_name = scrapy.Field()
    secondary_key = scrapy.Field()


class AntdComponentDetailItem(scrapy.Item):
    desc = scrapy.Field()
    name = scrapy.Field()
    key = scrapy.Field()
    key = scrapy.Field()
    easy_to_use = scrapy.Field()
    category_name = scrapy.Field()

class CnblogsItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()

class ScrapyDemoItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    tag = scrapy.Field()
    date_type = scrapy.Field()
    title_homepage = scrapy.Field()
    title_detail = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip())
    )
    describe = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip())
    )
    programming_language = scrapy.Field()
    star = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fork = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    build_by = scrapy.Field()
    octicon_star = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip())
    )


class TrendingItemLoader(ItemLoader):
    # 自定义item_loader
    default_output_processor = TakeFirst()
