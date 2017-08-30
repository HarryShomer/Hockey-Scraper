import pandas as pd
import requests
import json
import time
import shared


def get_pbp(game_id):
    """
    Given a game_id it returns the raw json
    Ex: http://statsapi.web.nhl.com/api/v1/game/2016020475/feed/live
    :param game_id: the game
    :return: raw json of game
    """
    url = 'http://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game_id)

    try:
        response = shared.get_url(url)
        pbp_json = json.loads(response.text)
    except requests.exceptions.HTTPError as e:
        print('Json pbp for game {} is not there'.format(game_id), e)
        return None

    time.sleep(1)
    return pbp_json


def change_event_name(event):
    """
    Change event names from json style to html
    ex: BLOCKED_SHOT to BLOCK
    :param event: event type
    :return: fixed event type
    """
    event_types ={
        'PERIOD_START': 'PSTR',
        'FACEOFF': 'FAC',
        'BLOCKED_SHOT': 'BLOCK',
        'GAME_END': 'GEND',
        'GIVEAWAY': 'GIVE',
        'GOAL': 'GOAL',
        'HIT': 'HIT',
        'MISSED_SHOT': 'MISS',
        'PERIOD_END': 'PEND',
        'SHOT': 'SHOT',
        'STOP': 'STOP',
        'TAKEAWAY': 'TAKE',
        'PENALTY': 'PENL',
        'Early Intermission Start': 'EISTR',
        'Early Intermission End': 'EIEND',
        'Shootout Completed': 'SOC',
    }

    try:
        return event_types[event]
    except KeyError:
        return event


def get_teams(json):
    """
    Get teams 
    :param json: pbp json
    :return: dict with home and away
    """
    return {'Home': shared.TEAMS[json['gameData']['teams']['home']['name'].upper()],
            'Away': shared.TEAMS[json['gameData']['teams']['away']['name'].upper()]}


def parse_event(event):
    """
    Parses a single event when the info is in a json format
    :param event: json of event 
    :return: dictionary with the info
    """
    play = dict()

    play['period'] = event['about']['period']
    play['event'] = str(change_event_name(event['result']['eventTypeId']))
    play['seconds_elapsed'] = shared.convert_to_seconds(event['about']['periodTime'])

    # If there's a players key that means an event occurred on the play.
    if 'players' in event.keys():
        play['p1_name'] = shared.fix_name(event['players'][0]['player']['fullName'])
        play['p1_ID'] = event['players'][0]['player']['id']

        for i in range(len(event['players'])):
            if event['players'][i]['playerType'] != 'Goalie':
                play['p{}_name'.format(i + 1)] = shared.fix_name(event['players'][i]['player']['fullName'].upper())
                play['p{}_ID'.format(i + 1)] = event['players'][i]['player']['id']

        # Coordinates aren't always there
        try:
            play['xC'] = event['coordinates']['x']
            play['yC'] = event['coordinates']['y']
        except KeyError:
            play['xC'] = ''
            play['yC'] = ''

    """
    # Sometimes they record events for shots in the wrong zone (or maybe not)...so change it
    if play['xC'] != 'Na' and play['yC'] != 'Na':

        if play['Ev_Team'] == home_team:
            # X should be negative in 1st and 3rd for home_team
            if (play['Period'] == 1 or play['Period'] == 3) and play['xC'] > 0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])
            elif play['Period'] == 2 and play['xC'] < 0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])
        else:
            # X should be positive in 1st and 3rd for away_team
            if (play['Period'] == 1 or play['Period'] == 3) and play['xC'] < 0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])
            elif play['Period'] == 2 and play['xC'] > 0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])
    """

    return play


def parse_json(game_json):
    """
    Scrape the json for a game
    :param game_json: raw json
    :return: Either a DataFrame with info for the game 
    """
    columns = ['period', 'event', 'seconds_elapsed', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name', 'p3_ID', 'xC', 'yC']

    plays = game_json['liveData']['plays']['allPlays'][2:]  # All the plays/events in a game

    # Go through all events and store all the info in a list
    # 'PERIOD READY' & 'PERIOD OFFICIAL'..etc aren't found in html...so get rid of them
    event_to_ignore = ['PERIOD_READY', 'PERIOD_OFFICIAL', 'GAME_READY', 'GAME_OFFICIAL']
    events = [parse_event(play) for play in plays if play['result']['eventTypeId'] not in event_to_ignore]

    return pd.DataFrame(events, columns=columns)


def scrape_game(game_id):
    """
    Used for debugging 
    :param game_id: game to scrape
    :return: DataFrame of game info
    """
    try:
        game_json = get_pbp(game_id)
    except requests.exceptions.HTTPError as e:
        print('Json pbp for game {} is not there'.format(game_id), e)
        return None

    try:
        game_df = parse_json(game_json)
    except Exception as e:
        print('Error for Json pbp for game {}'.format(game_id), e)
        return None

    return game_df

