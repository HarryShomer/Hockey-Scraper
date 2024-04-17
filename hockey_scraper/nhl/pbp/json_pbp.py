"""
This module contains functions to scrape the Json Play by Play for any given game
"""

import json
import pandas as pd
from operator import itemgetter
import hockey_scraper.utils.shared as shared


def get_pbp(game_id):
    """
    Given a game_id it returns the raw json
    Ex: https://api-web.nhle.com/v1/gamecenter/2023010044/play-by-play
    
    :param game_id: string - the game
    
    :return: raw json of game or None if couldn't get game
    """
    page_info = {
        "url": 'https://api-web.nhle.com/v1/gamecenter/{}/play-by-play'.format(game_id),
        "name": game_id,
        "type": "json_pbp",
        "season": game_id[:4],
    }
    response = shared.get_file(page_info)

    if not response:
        shared.print_error("Json pbp for game {} is either not there or can't be obtained".format(game_id))
        return {}
    else:
        return json.loads(response)


def get_teams(pbp_json):
    """
    Get teams 

    :param pbp_json: raw play by play json

    :return: dict with home and away
    """
    return {
        'Home': shared.convert_tricode(pbp_json['homeTeam']['abbrev']),
        'Away': shared.convert_tricode(pbp_json['awayTeam']['abbrev'])
    }


def change_event_name(event):
    """
    Change event names from json style to html (ex: BLOCKED_SHOT to BLOCK). 
    
    :param event: event type
    
    :return: fixed event type
    """
    event_types = {
        'PERIOD-START': 'PSTR',
        'FACEOFF': 'FAC',
        'BLOCKED-SHOT': 'BLOCK',
        'GAME-END': 'GEND',
        'GIVEAWAY': 'GIVE',
        'GOAL': 'GOAL',
        'HIT': 'HIT',
        'MISSED SHOT': 'MISS',
        'PERIOD-END': 'PEND',
        'SHOT-ON-GOAL': 'SHOT',
        'STOPPAGE': 'STOP',
        'TAKEAWAY': 'TAKE',
        'PENALTY': 'PENL',
        'EARLY INT START': 'EISTR',
        'EARLY INT END': 'EIEND',
        'SHOOTOUT COMPLETE': 'SOC',
        'CHALLENGE': 'CHL',
        'EMERGENCY GOALTENDER': 'EGPID'
    }

    return event_types.get(event.upper(), event)


def parse_event(event):
    """
    Parses a single event when the info is in a json format
    
    :param event: json of event 
    
    :return: dictionary with the info
    """
    play = dict()

    play['event_id'] = event['eventId']
    play['period'] = event['periodDescriptor']['number']
    play['event'] = str(change_event_name(event['typeDescKey'].upper()))
    play['seconds_elapsed'] = shared.convert_to_seconds(event['timeInPeriod'])
    
    play['p1_name'], play['p2_name'], play['p3_name'] = '', '', ''
    if 'details' in event.keys():
        details = event['details'].keys()
        # If there's a players key that means an event occurred on the play.

        if 'scoringPlayerId' in details:
            play['p1_ID'] = event['details']['scoringPlayerId']

        if 'shootingPlayerId' in details:
            play['p1_ID'] = event['details']['shootingPlayerId']

        if 'assist1PlayerId' in details:
            play['p2_ID'] = event['details']['assist1PlayerId']
            
        if 'assist2PlayerId' in details:
            play['p3_ID'] = event['details']['assist2PlayerId']

        if 'blockingPlayerId' in details:
            play['p2_ID'] = event['details']['blockingPlayerId']

        if 'xCoord' in details:
            play['xC'] = event['details']['xCoord']
            play['yC'] = event['details']['yCoord']
        

    return play


def parse_json(game_json, game_id):
    """
    Scrape the json for a game
    
    :param game_json: raw json
    :param game_id: game id for game
    
    :return: Either a DataFrame with info for the game or None when fail
    """
    columns = ['period', 'event', 'seconds_elapsed', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name', 'p3_ID', 'xC', 'yC']

    # 'PERIOD READY' & 'PERIOD OFFICIAL'..etc aren't found in html...so get rid of them
    events_to_ignore = ['PERIOD READY', 'PERIOD OFFICIAL', 'GAME READY', 'GAME OFFICIAL', 'GAME SCHEDULED']

    try:
        plays = game_json['plays']
        events = [parse_event(play) for play in plays if play['typeDescKey'].upper() not in events_to_ignore]
    except Exception as e:
        shared.print_error('Error parsing Json pbp for game {} {}'.format(game_id, e))
        return None

    # Sort by event id.
    # Sometimes it's not in order of the assigned id in the json. Like, 156...155 (not sure how this happens).
    sorted_events = sorted(events, key=itemgetter('event_id'))

    return pd.DataFrame(sorted_events, columns=columns)


def scrape_game(game_id):
    """
    **Used for debugging** 

    HTML depends on json so can't follow this structure
    
    :param game_id: game to scrape
    
    :return: DataFrame of game info
    """
    game_json = get_pbp(game_id)

    if not game_json:
        shared.print_error("Json pbp for game {} is not either not there or can't be obtained".format(game_id))
        return None

    try:
        game_df = parse_json(game_json, game_id)
    except Exception as e:
        shared.print_error('Error parsing Json pbp for game {} {}'.format(game_id, e))
        return None

    return game_df
