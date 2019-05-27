from scrapy.cmdline import execute
import os

os.environ['EXTRACT_MATCH_SCORE_ENVIRON'] = os.path.dirname(__file__)

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