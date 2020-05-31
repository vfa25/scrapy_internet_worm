# -*- coding: utf-8 -*-

import sys
import os

# Scrapy settings for ScrapyDemo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from ScrapyDemo.myconfig import *

BOT_NAME = 'ScrapyDemo'

SPIDER_MODULES = ['ScrapyDemo.spiders']
NEWSPIDER_MODULE = 'ScrapyDemo.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
RANDOM_UA_TYPE = 'random_chrome'
# Obey robots.txt rules
# [关闭] 遵循Robot协议
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# 在scrapy.downloadermiddlewares.cookies中，
# 可以看到：类方法from_crawler和实例方法process_request
# 会作用于所有的Request（即从第一个上提取cookie并设置在请求头）
COOKIES_ENABLED = True
# 开启cookie调试
COOKIES_DEBUG = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'ScrapyDemo.middlewares.ScrapyDemoSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    #    'ScrapyDemo.middlewares.ScrapyDemoDownloaderMiddleware': 543,
    # 在settings文件中设置USER_AGENT参数后，会为每个Request设置请求头字段
    #    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 2
    'ScrapyDemo.middlewares.RandomProxyMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    # 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    # 'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'ScrapyDemo.pipelines.ScrapyDemoPipeline': 300,
    # mysql pipeline
    'ScrapyDemo.pipelines.MysqlTwistedPipline': 4,
    # json pipeline
    # 'ScrapyDemo.pipelines.JsonWithEncodingPipeline': 300,
    # 'ScrapyDemo.pipelines.JsonExporterPipeline': 3,
    # images pipeline
    # 'ScrapyDemo.pipelines.customImagesPipeline': 1
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

IMAGES_URLS_FIELD = 'front_image_url'
project_dir = os.path.dirname(os.path.abspath(__file__))
IMAGES_STORE = os.path.join(project_dir, 'images')

sys.path.insert(0, project_dir)

# 设置mysql入库的 时间格式化
SQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SQL_DATE_FORMAT = '%Y-%m-%d'
