# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ExtractScoresItem(scrapy.Item):
    # define the fields for your item here like:
    match_type = scrapy.Field()
    match_date = scrapy.Field()
    location_info = scrapy.Field()
    match_scorecard_link = scrapy.Field()
    match_first_inning_participant = scrapy.Field()
    match_second_inning_participant = scrapy.Field()
