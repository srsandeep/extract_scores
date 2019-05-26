import requests
# from my_logger import logger

# TODO: If logging is to be integrated with scrapy logger, then use getlogger(<scrapy-spider-name>)
import logging
logger = logging.getLogger('extract_match_score')

from enum import Enum
MAX_NUM_PAGES_TO_DOWNLOAD = 2

class MatchType(Enum):
    ODI_MATCH = 1
    TEST_MATCH = 2
    T20_MATCH = 3
    OTHER_MATCH = 4

class SeriesInfo:

    def __init__(self, series_id):
        self.series_id = series_id
        self.match_ids = []

    def add_match_id(self, match_id):
        self.match_ids.append(match_id)

    def get_odi_match_ids(self):
        return self.match_ids

class MatchInfo:

    def __init__(self, series_id, match_id):
        self.series_id = series_id
        self.match_id = match_id
        self.match_type = MatchType.ODI_MATCH
        self.teams = ['Zimbabwe', 'South Africa']
        self.location = ''
        self.date_played = ''
        self.num_pages = dict()
        self.commentry_data = None
        self.dummy_page_num = 100

    def get_num_pages(self, innings_id):
        if innings_id not in self.num_pages:
            response = requests.get(self.get_commentry_url(innings_id, 0))
            if response.status_code == 200:
                self.num_pages[innings_id] = response.json()['commentary']['pageCount']
                logger.debug(f'Num pages: {self.num_pages[innings_id]} inning: {innings_id}, matchId: {self.match_id}, seriesId: {self.series_id}')
            else:
                logger.error(f'Failed to get number of pages for seriedId: {self.series_id} matchId: {self.match_id} inning: {innings_id}')
                self.num_pages[innings_id] = 1

        #TODO: Remove the min page count in production code
        return min(self.num_pages[innings_id], MAX_NUM_PAGES_TO_DOWNLOAD)

    def get_commentry_url(self, innings_id, page_num):
        if page_num == 0:
            return f'http://site.web.api.espn.com/apis/site/v2/sports/cricket/{str(self.series_id)}/playbyplay?contentorigin=espn&event={str(self.match_id)}&page={str(self.dummy_page_num)}&period={innings_id}&section=cricinfo'
        elif page_num <= self.get_num_pages(innings_id):
            return f'http://site.web.api.espn.com/apis/site/v2/sports/cricket/{str(self.series_id)}/playbyplay?contentorigin=espn&event={str(self.match_id)}&page={str(page_num)}&period={innings_id}&section=cricinfo'

    def get_commentry_page(self, innings_id, page_num):
        if page_num <= self.num_pages[innings_id]:
            logger.info(f'Getting commentary for Series: {self.series_id}, Match: {self.match_id}, InningId: {innings_id}, PageNum: {page_num} , URL: {self.get_commentry_url(innings_id, page_num)}')
            response_commentry = requests.get(self.get_commentry_url(innings_id, page_num))
            if response_commentry.status_code == 200:
                return response_commentry.json()
            else:
                logger.warn('Received failure response code: {}'.format(response_commentry.status_code))
                # raise Exception('Received failure response code: {}'.format(response_commentry.status_code))
        else:
            logger.warn(f'Page num: {page_num} greater than max pages')
            # raise Exception('{} > max pages: {}'.format(page_num, self.num_pages[innings_id]))

    def get_innings_commentry(self, innings_id):
        for each_page_num in range(self.get_num_pages(innings_id)):
            response = self.get_commentry_page(innings_id, each_page_num)
            logger.info('Innings: {} Data: {}'.format(innings_id, response['commentary'].keys()))

    def get_event_commentary(self):
        for each_inning in ['1', '2']:
            self.get_innings_commentry(each_inning)


# def get_innings_data(series_id, match_id):
#     #http://site.web.api.espn.com/apis/site/v2/sports/cricket/18886/playbyplay?contentorigin=espn&event=1174242&page=11&period=2&section=cricinfo
#     response = requests.get('http://site.web.api.espn.com/apis/site/v2/sports/cricket/18886/playbyplay?contentorigin=espn&event=1174242&page=11&period=2&section=cricinfo')
#     # count: 306, pageIndex: 11, pageSize: 25, pageCount: 13
#     print (response)

if __name__ == "__main__":
    first_match = MatchInfo(18886, 1174242)
    logger.info('Completed the initialization')
    first_match.get_innings_commentry('1')