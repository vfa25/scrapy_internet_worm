# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import (MapCompose, TakeFirst, Identity, Join)
from .utils.common import extract_num
from .utils.item_handle import (date_convert)
from .settings import (SQL_DATE_FORMAT, SQL_DATETIME_FORMAT)


class AntdAsideNavItem(scrapy.Item):
    primary_title = scrapy.Field()
    secondary_title = scrapy.Field()
    secondary_name = scrapy.Field()
    secondary_key = scrapy.Field()


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into zhihu_question(zhihu_id, topics, url, title, content,
            answer_num, comments_num, watch_user_num, click_num, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE title=VALUES(title),
            topics=VALUES(topics),
            content=VALUES(content),
            answer_num=VALUES(answer_num),
            comments_num=VALUES(comments_num),
            watch_user_num=VALUES(watch_user_num),
            click_num=VALUES(click_num)
            '''
        zhihu_id = self['zhihu_id'][0]
        topics = ','.join(self['topics'])
        url = self['url'][0]
        title = ''.join(self['title'])
        content = ''.join(self['content'])
        answer_num = extract_num(''.join(self['answer_num']))
        comments_num = extract_num(''.join(self['comments_num']))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            click_num = int(self["watch_user_num"][1].replace(',', ''))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            click_num = 0

        params = (zhihu_id, topics, url, title, content,
                  answer_num, comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content,
            praise_num, comments_num, create_time, update_time, crawl_time, crawl_update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content),
            praise_num=VALUES(praise_num),
            comments_num=VALUES(comments_num),
            update_time=VALUES(update_time),
            crawl_update_time=VALUES(crawl_time)
        '''

        create_time = datetime.datetime.fromtimestamp(
            self['create_time']).strftime(SQL_DATE_FORMAT)
        update_time = datetime.datetime.fromtimestamp(
            self['update_time']).strftime(SQL_DATE_FORMAT)
        params = (
            self['zhihu_id'], self['url'], self['question_id'],
            self['author_id'], self['content'], self['praise_num'],
            self['comments_num'], create_time, update_time,
            self['crawl_time'].strftime(SQL_DATETIME_FORMAT),
            None
        )
        return insert_sql, params


class AntdComponentDetailItem(scrapy.Item):
    desc = scrapy.Field()
    name = scrapy.Field()
    key = scrapy.Field()
    key = scrapy.Field()
    easy_to_use = scrapy.Field()
    category_name = scrapy.Field()


class CnblogsItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip())
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(separator=',')
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into cnblogs(title, url_object_id)
            VALUES (%s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)
            '''
        params = (self['url_object_id'], self['title'])

        return insert_sql, params


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
        input_processor=MapCompose(extract_num)
    )
    fork = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    build_by = scrapy.Field()
    octicon_star = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip())
    )


class TakeFirstItemLoader(ItemLoader):
    '''
    自定义item_loader：取list的first_extract
    '''
    default_output_processor = TakeFirst()
