# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# mysql相关
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

# json相关
import codecs
import json

from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline


class customImagesPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        '''
        override 图片下载，以字段front_image_path缓存获取到的下载路径
        '''
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path

        return item


class JsonWithEncodingPipeline(object):
    # 自定义json文件导出
    def __init__(self):
        self.file = codecs.open('data/cnblogs.json', 'a', encoding='utf-8')
        pass

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + ',\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    # 调用sctapy提供的json exporter导出json数据
    def __init__(self):
        self.file = open('data/cnlogsexport.json', 'wb')
        self.exporter = JsonItemExporter(
            self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class MysqlTwistedPipline(object):
    '''
    异步写入mqsql
    '''

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
        # 连接池
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 第一个参数传入连接池执行的回调函数，以使异步执行入库
        # 后面的参数都将作为前者的实参
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print('failure', failure, item, spider)

    def do_insert(self, cursor, item):
        '''
        真正的入库逻辑
        根据不同的item构建不同的sql语句并插入到mysql中
        '''
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
