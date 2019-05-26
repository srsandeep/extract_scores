# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose

def remove_newlines_and_strip(input_str):
    return input_str.replace('\n', ' ').strip()


class ExtractScoresItem(scrapy.Item):
    # define the fields for your item here like:
    series_id = scrapy.Field()
    event_id = scrapy.Field()
    event_type = scrapy.Field()
    event_date = scrapy.Field(input_processor = MapCompose(remove_newlines_and_strip))
    event_location_info = scrapy.Field(input_processor = MapCompose(remove_newlines_and_strip))
    event_scorecard_link = scrapy.Field()
    event_first_participant = scrapy.Field(input_processor = MapCompose(remove_newlines_and_strip))
    event_second_participant = scrapy.Field(input_processor = MapCompose(remove_newlines_and_strip))
