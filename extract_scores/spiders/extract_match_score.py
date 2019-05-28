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
import os
import json

class ExtractMatchScoreSpider(CrawlSpider):
    name = 'extract_match_score'

    def start_requests(self):
        start_urls = ['http://www.espncricinfo.com/ci/engine/series/index.html', 'http://www.espncricinfo.com/story/_/id/18791072/all-cricket-teams-index']
        for url in start_urls:
            if 'index.html' in url:
                yield scrapy.Request(url=url, 
                                    callback=self.parse_series_html, 
                                    errback=self.scrapy_error_callback)
            elif 'all-cricket-teams-index' in url:
                yield scrapy.Request(url=url, 
                                    callback=self.parse_teams_html, 
                                    errback=self.scrapy_error_callback)
            else:
                pass

    
    def scrapy_error_callback(self, failure):
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error(f'HttpError on {response.url}')


    def parse_teams_html(self, response):
        self.logger.info(f'Response from all-teams-index url received')
        teams_df = pd.DataFrame()
        for each_sel in response.xpath('//*[@id="article-feed"]/article/div/div/p'):
            team_id_name_list = each_sel.xpath('./a/@href').re(r'.*id\/(\d+)\/([a-z\-]+).*')
            if len(team_id_name_list) == 2:
                team_dict = {'id': team_id_name_list[0],
                            'name': team_id_name_list[1]}
                teams_df = teams_df.append(team_dict, ignore_index=True)
        teams_df.to_json('/tmp/teams.json')


    def parse_series_html(self, response):
        self.logger.info(f'Received ALL-YEARS response for the url: {response.url}')
        self.config_dir = os.environ.get('EXTRACT_MATCH_SCORE_ENVIRON', os.getcwd())
        self.config_file_path = os.path.join(self.config_dir, 'config.json')
        if os.path.exists(self.config_file_path):
            self.config_data = dict()
            with open(self.config_file_path, 'r') as fp:
                self.config_data = json.load(fp)
            series_years = response.xpath('//*[@class="season-links"]/a/text()').extract()
            year_links = response.xpath('//*[@class="season-links"]/a/@href').getall()
            url = "http://www.espncricinfo.com"
            for idx, each_link in enumerate(year_links):

                if 'years_of_interest' in self.config_data and \
                            series_years[idx].split('/')[0] in self.config_data['years_of_interest']:

                    self.logger.info(f'Retriving the data for series year: {series_years[idx]} from ' + urllib.parse.urljoin(url, each_link))
                    my_app_metadata = dict()
                    my_app_metadata['series_year'] = series_years[idx]
                    yield scrapy.Request(url=urllib.parse.urljoin(url, each_link), 
                                        callback=self.parse_yearly_series, 
                                        errback=self.scrapy_error_callback,
                                        meta=my_app_metadata)
        else:
            self.logger.error(f'Config file Not found! Config Dir: {self.config_dir}')


    def parse_yearly_series(self, response):
        received_meta_data = response.meta.get('series_year', 'Unknown')
        self.logger.info(f'Received YEARLY-SERIES for year: {received_meta_data} response for the url: {response.url}')

        series_categories = response.xpath('//*[@class="match-section-head"]/h2/text()').extract()
        for idx, each_series_category in enumerate(series_categories):
            self.logger.info('Examining the event type {}'.format(each_series_category))
            if each_series_category in self.config_data['event_type']:
                odi_selectors = response.xpath('//*[@class="series-summary-wrap"]')[idx]
                series_ids = odi_selectors.xpath('./section/@data-series-id').extract()
                self.logger.info('Series IDs : {}'.format(series_ids))
                for each_series_id in series_ids:
                    my_app_metadata = dict()
                    my_app_metadata['series_id'] = each_series_id

                    #TODO Remove the if to get the data of all the series
                    # interested_series_id = '12032'
                    # if each_series_id == interested_series_id:
                    yield scrapy.Request(url = f'http://www.espncricinfo.com/ci/engine/match/index/series.html?series={each_series_id}', 
                                        callback=self.parse_bilateral_series,
                                        errback=self.scrapy_error_callback,
                                        meta=my_app_metadata)
                break


    def parse_bilateral_series(self, response):
        received_meta_data = response.meta.get('series_id', 'Unknown')
        self.logger.info(f'Received response for BILATERAL-SERIES: {received_meta_data} from url: {response.url}')

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

