from scrapy.cmdline import execute
import sys
import os

abs_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_dir)
execute(['scrapy', 'crawl', 'github_app'])
