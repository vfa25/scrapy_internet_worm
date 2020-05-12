from scrapy.cmdline import execute
import sys
import os

abs_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_dir)
# execute(['scrapy', 'crawl', 'github_app'])
# execute(['scrapy', 'crawl', 'ant_design_aside'])
# execute(['scrapy', 'crawl', 'cnblogs'])
# execute(['scrapy', 'crawl', 'zhihu'])
# execute(['scrapy', 'crawl', 'lagou'])
execute(['scrapy', 'crawl', 'bilibili'])
