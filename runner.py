from scrapy.cmdline import execute

try:
    execute(
        [
            'scrapy',
            'crawl',
            'extract_match_score',
        ]
    )
except SystemExit:
    pass