# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

# 异步写入mqsql


class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print('failure', failure)


    def do_insert(self, cursor, item):
        insert_sql = '''
        insert into trending(url_object_id, tag, date_type, url,title_homepage,
        title_detail, `describe`, programming_language, star, fork, build_by, octicon_star)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(
            insert_sql, (
                item['url_object_id'],
                item['tag'],
                item['date_type'],
                item['url'],
                item['title_homepage'],
                item['title_detail'],
                item['describe'],
                item['programming_language'],
                item['star'],
                item['fork'],
                item['build_by'],
                item['octicon_star']
            )
        )
