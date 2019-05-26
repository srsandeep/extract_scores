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
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from commentry_getter.innings import MatchInfo, MatchType

class ExtractMatchScoreSpider(CrawlSpider):
    name = 'extract_match_score'

    def start_requests(self):
        start_urls = ['http://www.espncricinfo.com/ci/engine/series/index.html']
        for url in start_urls:
            yield scrapy.Request(url=url, 
                                callback=self.parse_series_html, 
                                errback=self.scrapy_error_callback)

    
    def scrapy_error_callback(self, failure):
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error(f'HttpError on {response.url}')


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
                my_app_metadata = dict()
                my_app_metadata['series_year'] = series_years[idx]
                yield scrapy.Request(url=urllib.parse.urljoin(url, each_link), 
                                    callback=self.parse_yearly_series, 
                                    errback=self.scrapy_error_callback,
                                    meta=my_app_metadata)


    def parse_yearly_series(self, response):
        received_meta_data = response.meta.get('series_year', 'Unknown')
        self.logger.info(f'Received YEARLY-SERIES for year: {received_meta_data} response for the url: {response.url}')
        #TODO: Enhance the logic to include T20 Mens, Tests Mens
        series_categories = response.xpath('//*[@class="match-section-head"]/h2/text()').extract()
        for idx, each_series_category in enumerate(series_categories):
            if each_series_category == 'One-Day Internationals':
                odi_selectors = response.xpath('//*[@class="series-summary-wrap"]')[idx]
                series_ids = odi_selectors.xpath('./section/@data-series-id').extract()
                for each_series_id in series_ids:
                    my_app_metadata = dict()
                    my_app_metadata['series_id'] = each_series_id

                    #TODO Remove the if to get the data of all the series
                    interested_series_id = '12032'
                    if each_series_id == interested_series_id:
                        yield scrapy.Request(url = f'http://www.espncricinfo.com/ci/engine/match/index/series.html?series={each_series_id}', 
                                            callback=self.parse_bilateral_series,
                                            errback=self.scrapy_error_callback,
                                            meta=my_app_metadata)
                break


    def parse_bilateral_series(self, response):
        received_meta_data = response.meta.get('series_id', 'Unknown')
        self.logger.info(f'Received response for BILATERAL-SERIES: {received_meta_data} from url: {response.url}')
        event_ids = response.xpath('//*[@class="match-articles"]/a[contains(text(), "Scorecard")]/@href').re(r'.*series\/\d+\/scorecard\/(\d+)\/.*')

        #Extract the Event information for the item loader
        for each_selector in response.xpath('//*/section[@class="matches-day-block"]/section'):
            event_loader = ItemLoader(item=ExtractScoresItem(), 
                                selector=each_selector)
            event_loader.default_output_processor = TakeFirst()
            event_loader.add_xpath('event_location_info', './div[@class="match-info"]/span[@class="match-no"]/a/text()')
            event_loader.add_xpath('event_date', './div[@class="match-info"]/span[@class="bold"]/text()')
            event_loader.add_xpath('event_first_participant', './div[@class="innings-info-1"]/text()')
            event_loader.add_xpath('event_second_participant', './div[@class="innings-info-2"]/text()')
            event_loader.add_xpath('event_id', 
                                './*[@class="match-articles"]/a[contains(text(), "Scorecard")]/@href', 
                                re=r'.*series\/\d+\/scorecard\/(\d+)\/.*')
            event_loader.add_value('series_id', [received_meta_data])
            yield event_loader.load_item()

