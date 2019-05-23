from scrapy.cmdline import execute

try:
    execute(
        [
            'scrapy',
            'crawl',
            'crawl_squad_spider',
        ]
    )
except SystemExit:
    pass
