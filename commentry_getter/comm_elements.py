"""
Elements for 2 innings
"""
from commentry_getter.innings import MatchInfo

class EventCommentary(object):

    def process_item(self, item, spider):

        if 'event_scorecard_link' in item and item['event_scorecard_link'] is not None:
            spider.logger.info('event_scorecard_link key located!')
            match_info = MatchInfo(int(item['series_id']), int(item['event_id']))
            match_info.get_event_commentary()
        else:
            spider.logger.warn('event_scorecard_link key is missing!')

        return item

# data_dictionary = {
#     'delivery_id' : None,
#     'batting_side_team_id' : None,
#     'bowling_side_team_id' : None,

#     'batsman_striker_id' : None,
#     'batsman_striker_score' : None,
#     'batsman_striker_balls_faced' : None,

#     'bowler_id' : None,
#     'bowler_balls_bowled' : None,
#     'bowler_runs_conceded' : None,
#     'bowler_wickets' : None,

#     'batsman_non_striker_id' : None,
#     'batsman_non_striker_score' : None,
#     'batsman_non_striker_balls_faced' : None,

#     'bowler_2_id' : None,
#     'bowler_2_balls_bowled' : None,
#     'bowler_2_runs_conceded' : None,
#     'bowler_2_wickets' : None,

#     'delivery_score' : None,
#     'awayScore' : None,

#     'dismissal_flag' : None,
#     'dismissal_type': None,
#     'dismissal_bowled_flag' : None,

#     'ball_limit' : None,
#     'num_balls' : None,
#     'remain_num_balls' : None,
#     'target_score' : None,
#     'remain_runs' : None,
#     'current_score' : None,
#     'num_wickets_lost' : None,
#     'byes' : None,
#     'leg_byes' : None,
#     'no_balls' : None,
#     'wides' : None,

#     'current_over' : None,
#     'overs_limit' : None,
#     'runs_in_current_over' : None,
#     'playtype_id' : None,
#     'playtype_description' : None,
# }

# Delivery id: commentary.items[10].id

# Batsman id: a['commentary']['items'][idx]['batsman']['athlete']['id']
# Batsman current score: a['commentary']['items'][idx]['batsman']['totalRuns']
# Batsman balls faced: commentary.items[""0""].batsman.faced
# Batsman team id: commentary.items[11].batsman.team.id

# Bowler id: commentary.items[11].bowler.athlete.id
# Bowler current overs bowled: commentary.items[10].bowler.overs
# Bowler current balls bowled: commentary.items[10].bowler.balls
# Bowler runs conceded: commentary.items[10].bowler.conceded
# Bowler wickets: commentary.items[10].bowler.wickets
# Bowler team id: commentary.items[10].bowler.team.id

# Non-striker id: commentary.items[2].otherBatsman.athlete.id
# Non-striker score: commentary.items[2].otherBatsman.runs
# Non-striker balls faced: commentary.items[2].otherBatsman.faced
# Non striker team id: commentary.items[2].otherBatsman.team.id

# Other bowler id: commentary.items[2].otherBowler.athlete.id
# Other bowler balls bowled: commentary.items[2].otherBowler.balls
# Other bowler runs conceded: commentary.items[2].otherBowler.conceded
# Other bowler wickets: commentary.items[2].otherBowler.wickets
# Other bowler team id: commentary.items[2].otherBowler.team.id

# Ball score: commentary.items[10].scoreValue
# Score value: commentary.items[11].awayScore

# Dismissal flag: commentary.items[2].dismissal.dismissal
# Dismissal type: commentary.items[2].dismissal.type
# Dismissal bowled flag: commentary.items[2].dismissal.bowled

# Innings data
# balls limit: commentary.items[2].innings.ballLimit
# Number balls: commentary.items[2].innings.balls
# remaining balls: commentary.items[2].innings.remainingBalls
# Target: commentary.items[2].innings.target
# Remaining runs: commentary.items[2].innings.remainingRuns
# Current score: commentary.items[2].innings.runs
# Num lost wickets: commentary.items[2].innings.wickets
# Innings bytes: commentary.items[""0""].innings.byes
# Inning leg byes: commentary.items[""0""].innings.legByes
# Innings noBalls: commentary.items[""0""].innings.noBalls
# Innings wides: commentary.items[""0""].innings.wides

# Over: commentary.items[2].over.actual
# Over limit: commentary.items[2].over.limit
# Run in current over: commentary.items[1].over.runs

# Playtype: commentary.items[2].playType.id
# Playtype description: commentary.items[2].playType.description