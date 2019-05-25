# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import urllib
from extract_scores.items import ExtractScoresItem
import pandas as pd
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
import re


class ExtractMatchScoreSpider(CrawlSpider):
    name = 'extract_match_score'

    def start_requests(self):
        start_urls = ['http://www.espncricinfo.com/ci/engine/series/index.html']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_series_html)

    def parse_item(self, response):
        item = {}
        self.logger.info(f'I am inside {response.url}')
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item

    def parse_series_html(self, response):
        self.logger.info(f'Received ALL-YEARS response for the url: {response.url}')
        series_years = response.xpath('//*[@class="season-links"]/a/text()').extract()
        year_links = response.xpath('//*[@class="season-links"]/a/@href').getall()
        url = "http://www.espncricinfo.com"
        for idx, each_link in enumerate(year_links):
            # TODO: Remove the 2018 if clause after debug
            if series_years[idx] == '2018':
                self.logger.info(f'Retriving the data for series year: {series_years[idx]} from ' + urllib.parse.urljoin(url, each_link))
                yield scrapy.Request(urllib.parse.urljoin(url, each_link), callback=self.parse_yearly_series)

    def parse_yearly_series(self, response):
        self.logger.info(f'Received YEARLY-SERIES response for the url: {response.url}')
        #TODO: Enhance the logic to include T20 Mens, Tests Mens
        series_categories = response.xpath('//*[@class="match-section-head"]/h2/text()').extract()
        for idx, each_series_category in enumerate(series_categories):
            if each_series_category == 'One-Day Internationals':
                odi_selectors = response.xpath('//*[@class="series-summary-wrap"]')[idx]
                series_ids = odi_selectors.xpath('./section/@data-series-id').extract()
                for each_series_id in series_ids:
                    yield scrapy.Request(f'http://www.espncricinfo.com/ci/engine/match/index/series.html?series={each_series_id}', callback=self.parse_bilateral_series)
                break

        # series_ids = response.xpath('//*[@class="series-summary-wrap"]/section/@data-series-id').extract()
        # # TODO: Remove the slicing in for loop
        # for each_series_id in series_ids[:2]:
        #     yield scrapy.Request(f'www.espncricinfo.com/ci/engine/match/index/series.html?series={each_series_id}', callback=self.parse_bilateral_series)

    def parse_bilateral_series(self, response):
        self.logger.info(f'Received BILATERAL-SERIES response for the url: {response.url}')
        all_match_series_match_id_tuples = response.xpath('//*[@class="match-articles"]/a[contains(text(), "Scorecard")]/@href').extract()
        for each_scorecard_link in all_match_series_match_id_tuples:
            # TODO: Replace the below with call to the rest API for extracting the pages
            series_match_tuple = re.search(r'.*series\/(\d+)\/scorecard\/(\d+)\/.*', each_scorecard_link).groups()
            self.logger.info('Series: {} Match: {} Link: {}'.format(series_match_tuple[0], series_match_tuple[1], each_scorecard_link))