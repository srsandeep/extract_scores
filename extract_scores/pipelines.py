# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from commentry_getter.innings import MatchInfo

class ExtractScoresPipeline(object):

    def map_event_name_to_type(self, event_info):
        if 'ODI' in event_info:
            return 'ODI'
        elif 'Test' in event_info:
            return 'TEST'
        elif 'T20' in event_info:
            return 'T20'
        else:
            return 'OTHER'


    def process_item(self, item, spider):
        item['event_type'] = self.map_event_name_to_type(item['event_location_info'])

        if 'event_id' in item and item['event_id'] is not None:
            item['event_scorecard_link'] = 'http://site.web.api.espn.com/apis/site/v2/sports/cricket/{}/playbyplay?contentorigin=espn&event={}&page=100&period=1&section=cricinfo'.format(item['series_id'], item['event_id'])

            # match_info = MatchInfo(int(item['series_id']), int(item['event_id']))
            # match_info.get_event_commentary()

        return item
