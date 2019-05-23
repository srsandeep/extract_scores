# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ExtractMatchScoreSpider(CrawlSpider):
    name = 'extract_match_score'
    allowed_domains = ['espncricinfo.com']
    start_urls = ['http://www.espncricinfo.com/series/18651/commentary/1144146/south-africa-vs-zimbabwe-1st-odi-zim-in-sa-2018-19']

    rules = (
        Rule(LinkExtractor(allow=[r'18651', r'18652']), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        self.logger.info(f'I am inside {response.url}')
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item
